import os
import uuid
from typing import Dict, List

import chromadb

from config import (
    CHROMA_DIR,
    COLLECTION_NAME,
    DEFAULT_TOP_K,
    SUMMARY_BATCH_SIZE,
    MAX_SUMMARY_CHUNKS,
    MAX_QUESTION_CONTEXT_CHUNKS,
    MAX_EXPLANATION_CONTEXT_CHUNKS,
    MAX_REVIEW_CONTEXT_CHUNKS,
    UPLOAD_DIR,
)

from document_loader import load_document, chunk_text
from embedding_service import get_text_embedding, get_text_embeddings
from llm_service import ask_llm


class RAGService:
    """
    Main RAG service.

    Responsibilities:
    1. Read uploaded documents.
    2. Split documents into chunks.
    3. Generate embeddings using embedding_service.
    4. Store chunks and embeddings in ChromaDB.
    5. Retrieve relevant chunks for questions.
    6. Ask the selected LLM through llm_service.
    7. Generate document explanations.
    8. Generate review questions.
    9. Evaluate review answers.
    10. Delete selected documents or clear full database.
    """

    def __init__(self):
        os.makedirs(CHROMA_DIR, exist_ok=True)

        self.client = chromadb.PersistentClient(path=CHROMA_DIR)

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME
        )

    def _build_file_filter(self, selected_file_names: List[str] | None):
        """
        Builds ChromaDB metadata filter for selected documents.
        If no documents are selected, returns None.
        """
        if not selected_file_names:
            return None

        clean_names = [
            file_name.strip()
            for file_name in selected_file_names
            if file_name and file_name.strip()
        ]

        if not clean_names:
            return None

        if len(clean_names) == 1:
            return {
                "file_name": clean_names[0]
            }

        return {
            "file_name": {
                "$in": clean_names
            }
        }

    def ingest_document(self, file_path: str) -> Dict:
        """
        Reads uploaded document, splits it into chunks, creates embeddings in batch,
        and stores all chunks inside ChromaDB.
        """
        document_text = load_document(file_path)

        if not document_text.strip():
            raise ValueError(
                "No readable text found in this document. "
                "If this is a scanned PDF, OCR is required."
            )

        chunks = chunk_text(document_text)

        if not chunks:
            raise ValueError("No valid chunks were created from this document.")

        file_name = os.path.basename(file_path)

        ids = []
        documents = []
        metadatas = []

        for index, chunk in enumerate(chunks):
            chunk_id = str(uuid.uuid4())

            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append(
                {
                    "file_name": file_name,
                    "chunk_index": index,
                }
            )

        embeddings = get_text_embeddings(documents)

        self.collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        return {
            "file_name": file_name,
            "chunks_created": len(chunks),
            "message": (
                "Document uploaded, split into chunks, embedded, "
                "and stored successfully."
            ),
        }

    def retrieve_context(
        self,
        question: str,
        top_k: int = DEFAULT_TOP_K,
        selected_file_names: List[str] | None = None,
    ) -> List[Dict]:
        """
        Retrieves relevant chunks for a question.
        If selected_file_names is provided, search is limited to those documents.
        """
        if not question.strip():
            return []

        question_embedding = get_text_embedding(question)

        query_args = {
            "query_embeddings": [question_embedding],
            "n_results": top_k,
        }

        file_filter = self._build_file_filter(selected_file_names)

        if file_filter:
            query_args["where"] = file_filter

        results = self.collection.query(**query_args)

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        retrieved_chunks = []

        for document, metadata, distance in zip(documents, metadatas, distances):
            retrieved_chunks.append(
                {
                    "text": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )

        return retrieved_chunks

    def answer_question(
        self,
        question: str,
        selected_file_names: List[str] | None = None,
    ) -> Dict:
        """
        Answers a user question using only retrieved uploaded-document context.
        """
        chunks = self.retrieve_context(
            question=question,
            top_k=DEFAULT_TOP_K,
            selected_file_names=selected_file_names,
        )

        if not chunks:
            return {
                "answer": "I could not find this information in the selected uploaded documents.",
                "sources": [],
            }

        context_text = "\n\n".join(
            [
                f"Source File: {chunk['metadata'].get('file_name', 'unknown')}\n"
                f"Chunk Number: {chunk['metadata'].get('chunk_index', '-')}\n"
                f"Content:\n{chunk['text']}"
                for chunk in chunks
            ]
        )

        system_prompt = """
You are a company internal document assistant.

Strict rules:
1. Answer only from the provided DOCUMENT CONTEXT.
2. Do not use outside knowledge.
3. If the answer is not present in the context, say exactly:
   "I could not find this information in the uploaded documents."
4. Keep the answer clear, concise, and professional.
5. Use bullet points when helpful.
"""

        user_prompt = f"""
DOCUMENT CONTEXT:
{context_text}

USER QUESTION:
{question}

Answer using only the document context.
"""

        answer = ask_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        sources = [
            {
                "file_name": chunk["metadata"].get("file_name", "unknown"),
                "chunk_index": chunk["metadata"].get("chunk_index", "-"),
                "distance": chunk["distance"],
            }
            for chunk in chunks
        ]

        return {
            "answer": answer,
            "sources": sources,
        }

    def get_all_chunks(
        self,
        selected_file_names: List[str] | None = None,
    ) -> List[str]:
        """
        Returns stored document chunks.
        If selected_file_names is provided, returns chunks only from selected documents.
        """
        file_filter = self._build_file_filter(selected_file_names)

        if file_filter:
            results = self.collection.get(
                where=file_filter
            )
        else:
            results = self.collection.get()

        documents = results.get("documents", [])
        return documents

    def summarize_chunk_batch(self, batch_text: str, batch_number: int) -> str:
        """
        Summarizes one batch of document chunks while preserving important details.
        Works for company documents as well as technical/study documents.
        """
        system_prompt = """
You are a document understanding assistant.

Your task is to summarize the given document section WITHOUT losing important details.

Rules:
1. Use only the provided document section.
2. Do not add outside information.
3. Preserve definitions, formulas, algorithms, examples, steps, advantages, applications, rules, and key terms if present.
4. If the section is technical or academic, explain the concept clearly.
5. If the section is a company/policy document, preserve policies, workflows, responsibilities, and compliance points.
6. Avoid vague summaries. Keep specific points from the document.
"""

        user_prompt = f"""
DOCUMENT SECTION BATCH NUMBER:
{batch_number}

Create a detailed section summary in this format:

1. Main topic of this section
2. Important definitions or concepts
3. Step-by-step working / process / algorithm if present
4. Formula, rule, or condition if present
5. Examples or applications mentioned
6. Advantages / limitations / risks if present
7. Key terms and their meanings
8. Important points to remember

DOCUMENT SECTION:
{batch_text}
"""

        return ask_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

    def create_long_document_summary(
        self,
        max_chunks: int = MAX_SUMMARY_CHUNKS,
        selected_file_names: List[str] | None = None,
    ) -> str:
        """
        Creates a detailed explanation from uploaded document chunks.

        It first summarizes batches, then creates one final explanation.
        The final explanation adapts to the document type:
        - technical/study document
        - company/policy/process document
        """
        all_chunks = self.get_all_chunks(
            selected_file_names=selected_file_names
        )

        if not all_chunks:
            return "No documents uploaded yet."

        selected_chunks = all_chunks[:max_chunks]
        batch_summaries = []

        for start in range(0, len(selected_chunks), SUMMARY_BATCH_SIZE):
            batch = selected_chunks[start:start + SUMMARY_BATCH_SIZE]
            batch_text = "\n\n".join(batch)
            batch_number = (start // SUMMARY_BATCH_SIZE) + 1

            summary = self.summarize_chunk_batch(
                batch_text=batch_text,
                batch_number=batch_number,
            )

            batch_summaries.append(
                f"Batch {batch_number} Summary:\n{summary}"
            )

        combined_summaries = "\n\n".join(batch_summaries)

        system_prompt = """
You are a senior document explanation assistant.

Create a clear, detailed, and useful explanation from the provided section summaries.

Important rules:
1. Use only the provided summaries.
2. Do not add outside information.
3. Do not give a shallow or generic explanation.
4. Preserve important technical details, definitions, formulas, examples, algorithms, advantages, applications, workflows, and rules.
5. If the document is technical/academic, explain it like study notes.
6. If the document is company/policy/process based, explain it like employee onboarding material.
7. Do not force company headings like compliance or employee responsibility if they are not relevant.
"""

        user_prompt = f"""
Create a final detailed explanation from these section summaries.

First identify the document type:
- Technical / Academic / Study Notes
- Company Policy / Process / Training Document
- Mixed Document

Then explain using the most suitable format.

If it is a technical or academic document, use this format:

1. Document Type
2. Topic Overview
3. Main Purpose
4. Core Concepts Explained
5. Step-by-Step Working / Algorithm / Process
6. Formula or Important Logic if present
7. Important Examples
8. Advantages / Benefits
9. Applications / Use Cases
10. Limitations / Risks if mentioned
11. Key Terms and Meanings
12. Exam / Interview Ready Summary

If it is a company or policy document, use this format:

1. Document Type
2. Document Overview
3. Main Purpose
4. Important Topics Covered
5. Important Rules / Policies / Procedures
6. Important Workflows
7. Roles and Responsibilities if mentioned
8. Key Terms and Meanings
9. What a New Employee Should Understand
10. Risks / Compliance Points if mentioned
11. Short Final Summary

SECTION SUMMARIES:
{combined_summaries}
"""

        final_summary = ask_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        return final_summary

    def explain_documents(
        self,
        selected_file_names: List[str] | None = None,
    ) -> Dict:
        """
        Fast explanation generation.

        This does NOT create multiple batch summaries.
        It directly uses limited selected document chunks and makes only one LLM call.
        This is much faster for frontend Generate Explanation.
        """
        all_chunks = self.get_all_chunks(
            selected_file_names=selected_file_names
        )

        if not all_chunks:
            return {
                "explanation": "No document context found for the selected documents."
            }

        selected_chunks = all_chunks[:MAX_EXPLANATION_CONTEXT_CHUNKS]

        context_text = "\n\n".join(
            [
                f"Section {index + 1}:\n{chunk}"
                for index, chunk in enumerate(selected_chunks)
            ]
        )

        system_prompt = """
You are a document explanation assistant.

Rules:
1. Explain only from the provided document content.
2. Do not add outside information.
3. Detect whether the document is technical/study material or company/process material.
4. Use the most suitable explanation format.
5. Keep the explanation clear, useful, and not unnecessarily long.
"""

        user_prompt = f"""
DOCUMENT CONTENT:
{context_text}

Create a clear explanation from the document content.

If the document is technical/study material, use this format:

1. Document Type
2. Topic Overview
3. Main Purpose
4. Core Concepts Explained
5. Step-by-Step Working / Algorithm / Process
6. Formula or Important Logic if present
7. Important Examples
8. Advantages / Benefits
9. Applications / Use Cases
10. Key Terms and Meanings
11. Short Exam / Interview Ready Summary

If the document is company/policy/process material, use this format:

1. Document Type
2. Document Overview
3. Main Purpose
4. Important Topics Covered
5. Important Rules / Policies / Procedures
6. Important Workflows
7. Roles and Responsibilities if mentioned
8. Key Terms and Meanings
9. What a New Employee Should Understand
10. Risks / Compliance Points if mentioned
11. Short Final Summary
"""

        explanation = ask_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        return {
            "explanation": explanation
        }

    def parse_numbered_questions(self, raw_text: str) -> List[str]:
        """
        Converts numbered LLM output into a Python list of questions.

        Supported formats:
        1. Question
        1) Question
        Q1. Question
        """
        questions = []

        for line in raw_text.splitlines():
            clean_line = line.strip()

            if not clean_line:
                continue

            lowered = clean_line.lower()

            if lowered.startswith("q") and "." in clean_line:
                _, remaining = clean_line.split(".", 1)
                question_text = remaining.strip()

                if question_text:
                    questions.append(question_text)

                continue

            if "." in clean_line:
                first_part, remaining = clean_line.split(".", 1)

                if first_part.strip().isdigit():
                    question_text = remaining.strip()

                    if question_text:
                        questions.append(question_text)

                    continue

            if ")" in clean_line:
                first_part, remaining = clean_line.split(")", 1)

                if first_part.strip().isdigit():
                    question_text = remaining.strip()

                    if question_text:
                        questions.append(question_text)

                    continue

        if not questions:
            for line in raw_text.splitlines():
                clean_line = line.strip()

                if clean_line:
                    questions.append(clean_line)

        return questions

    def generate_review_questions(
        self,
        number_of_questions: int = 10,
        selected_file_names: List[str] | None = None,
    ) -> Dict:
        """
        Fast review question generation.

        This does NOT create a long document summary first.
        It directly uses limited selected document chunks and makes only one LLM call.
        This is much faster than batch summarization.
        """
        all_chunks = self.get_all_chunks(
            selected_file_names=selected_file_names
        )

        if not all_chunks:
            return {
                "questions": [],
                "raw_questions": "No documents found for selected document filter.",
            }

        selected_chunks = all_chunks[:MAX_REVIEW_CONTEXT_CHUNKS]

        context_text = "\n\n".join(
            [
                f"Section {index + 1}:\n{chunk}"
                for index, chunk in enumerate(selected_chunks)
            ]
        )

        system_prompt = """
You are a company training and assessment assistant.

Important rules:
1. Generate only questions.
2. Do not provide answers.
3. Do not provide expected answer points.
4. Do not provide hints.
5. Use only the provided document content.
6. Questions should test understanding, not only memorization.
7. Keep questions clear and professional.
"""

        user_prompt = f"""
DOCUMENT CONTENT:
{context_text}

Generate exactly {number_of_questions} review questions from the document content.

Rules:
1. Generate only questions.
2. Number each question clearly.
3. Use a mix of short-answer, descriptive, and scenario-based questions.
4. Do not include answers.
5. Do not include explanation.

Return only in this format:
1. Question text
2. Question text
3. Question text
"""

        raw_questions = ask_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        questions = self.parse_numbered_questions(raw_questions)

        return {
            "questions": questions,
            "raw_questions": raw_questions,
        }

    def evaluate_review_answer(
        self,
        question: str,
        user_answer: str,
        selected_file_names: List[str] | None = None,
    ) -> Dict:
        """
        Evaluates one user's answer using retrieved document context.
        Expected answer is shown only after user submits the answer.
        """
        if not question.strip():
            return {
                "evaluation": "Question cannot be empty.",
                "sources": [],
            }

        if not user_answer.strip():
            return {
                "evaluation": "Answer cannot be empty.",
                "sources": [],
            }

        chunks = self.retrieve_context(
            question=question,
            top_k=DEFAULT_TOP_K,
            selected_file_names=selected_file_names,
        )

        if not chunks:
            return {
                "evaluation": "No document context found for the selected documents.",
                "sources": [],
            }

        context_text = "\n\n".join(
            [
                f"Source File: {chunk['metadata'].get('file_name', 'unknown')}\n"
                f"Chunk Number: {chunk['metadata'].get('chunk_index', '-')}\n"
                f"Content:\n{chunk['text']}"
                for chunk in chunks
            ]
        )

        system_prompt = """
You are a company training evaluator.

Rules:
1. Evaluate only using the provided DOCUMENT CONTEXT.
2. Do not use outside knowledge.
3. Be fair and constructive.
4. Give expected answer only after evaluating the user's answer.
5. Keep the evaluation concise.
"""

        user_prompt = f"""
DOCUMENT CONTEXT:
{context_text}

REVIEW QUESTION:
{question}

USER ANSWER:
{user_answer}

Evaluate the user's answer in this exact format:

1. Result:
Correct / Partially Correct / Incorrect

2. Score:
Give a score out of 10.

3. Correct points:
Mention what the user wrote correctly.

4. Missing or incorrect points:
Mention what is missing or incorrect.

5. Expected answer:
Write the ideal answer based only on the document context.

6. Improvement suggestion:
Give one short improvement suggestion.
"""

        evaluation = ask_llm(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
        )

        sources = [
            {
                "file_name": chunk["metadata"].get("file_name", "unknown"),
                "chunk_index": chunk["metadata"].get("chunk_index", "-"),
                "distance": chunk["distance"],
            }
            for chunk in chunks
        ]

        return {
            "evaluation": evaluation,
            "sources": sources,
        }

    def evaluate_review_form(
        self,
        review_answers: List[Dict],
        selected_file_names: List[str] | None = None,
    ) -> Dict:
        """
        Evaluates multiple review answers safely.

        If one question fails, the full form does not crash.
        """
        if not review_answers:
            return {
                "results": [],
            }

        final_results = []

        for index, item in enumerate(review_answers, start=1):
            question = item.get("question", "").strip()
            user_answer = item.get("user_answer", "").strip()

            if not question:
                final_results.append(
                    {
                        "question_number": index,
                        "question": question,
                        "user_answer": user_answer,
                        "evaluation": "Invalid question. Please regenerate the review form.",
                        "sources": [],
                    }
                )
                continue

            if not user_answer:
                final_results.append(
                    {
                        "question_number": index,
                        "question": question,
                        "user_answer": user_answer,
                        "evaluation": """
1. Result:
Not Attempted

2. Score:
0/10

3. Correct points:
No answer was provided.

4. Missing or incorrect points:
The user did not attempt this question.

5. Expected answer:
Expected answer should be based on the selected uploaded document content.

6. Improvement suggestion:
Attempt the question using points from the selected document.
""",
                        "sources": [],
                    }
                )
                continue

            try:
                single_result = self.evaluate_review_answer(
                    question=question,
                    user_answer=user_answer,
                    selected_file_names=selected_file_names,
                )

                final_results.append(
                    {
                        "question_number": index,
                        "question": question,
                        "user_answer": user_answer,
                        "evaluation": single_result.get("evaluation", ""),
                        "sources": single_result.get("sources", []),
                    }
                )

            except Exception as e:
                final_results.append(
                    {
                        "question_number": index,
                        "question": question,
                        "user_answer": user_answer,
                        "evaluation": f"""
1. Result:
Evaluation Failed

2. Score:
Not available

3. Correct points:
Could not evaluate due to a backend/model error.

4. Missing or incorrect points:
Could not evaluate due to a backend/model error.

5. Expected answer:
Could not generate expected answer because evaluation failed.

6. Improvement suggestion:
Try again with fewer questions or check backend logs.

Technical error:
{str(e)}
""",
                        "sources": [],
                    }
                )

        return {
            "results": final_results,
        }

    def list_documents(self) -> Dict:
        """
        Lists unique uploaded document names.
        """
        results = self.collection.get()
        metadatas = results.get("metadatas", [])

        file_names = sorted(
            list(
                set(
                    metadata.get("file_name", "unknown")
                    for metadata in metadatas
                )
            )
        )

        return {
            "documents": file_names,
            "total_documents": len(file_names),
        }

    def delete_document(self, file_name: str) -> Dict:
        """
        Deletes one selected document from ChromaDB using file name.
        Also deletes the physical uploaded file from data/uploads if present.
        """
        results = self.collection.get(
            where={
                "file_name": file_name,
            }
        )

        ids = results.get("ids", [])

        if not ids:
            return {
                "deleted": False,
                "message": f"No indexed document found with name: {file_name}",
            }

        self.collection.delete(
            ids=ids,
        )

        file_path = os.path.join(UPLOAD_DIR, file_name)

        if os.path.exists(file_path):
            os.remove(file_path)

        return {
            "deleted": True,
            "file_name": file_name,
            "chunks_deleted": len(ids),
            "message": f"Document '{file_name}' removed successfully.",
        }

    def clear_database(self) -> Dict:
        """
        Clears the complete ChromaDB collection.
        """
        self.client.delete_collection(name=COLLECTION_NAME)

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME
        )

        return {
            "message": "ChromaDB vector database cleared successfully.",
        }