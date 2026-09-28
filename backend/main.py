import os
import shutil
from typing import List

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import UPLOAD_DIR
from ollama_service import check_ollama_running
from rag_service import RAGService


app = FastAPI(
    title="Company RAG Chatbot API",
    description="A free local RAG chatbot using FastAPI, ChromaDB, and Ollama.",
    version="1.0.0"
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


os.makedirs(UPLOAD_DIR, exist_ok=True)

rag_service = RAGService()


class QuestionRequest(BaseModel):
    question: str
    selected_file_names: List[str] = []


class ReviewQuestionRequest(BaseModel):
    number_of_questions: int = 10
    selected_file_names: List[str] = []


class ExplainRequest(BaseModel):
    selected_file_names: List[str] = []


class DeleteDocumentRequest(BaseModel):
    file_name: str


class EvaluateAnswerRequest(BaseModel):
    question: str
    user_answer: str
    selected_file_names: List[str] = []


class ReviewAnswerItem(BaseModel):
    question: str
    user_answer: str


class EvaluateReviewFormRequest(BaseModel):
    review_answers: List[ReviewAnswerItem]
    selected_file_names: List[str] = []


@app.get("/")
def home():
    return {
        "message": "Company RAG Chatbot Backend is running."
    }


@app.get("/health")
def health_check():
    return {
        "backend": "running",
        "ollama": check_ollama_running()
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    allowed_extensions = [".txt", ".pdf", ".docx"]

    file_extension = os.path.splitext(file.filename)[1].lower()

    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only .txt, .pdf, and .docx files are supported."
        )

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = rag_service.ingest_document(file_path)

        return result

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/ask")
def ask_question(request: QuestionRequest):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    try:
        return rag_service.answer_question(
            question=request.question,
            selected_file_names=request.selected_file_names
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/explain")
def explain_documents():
    try:
        return rag_service.explain_documents()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/explain-selected")
def explain_selected_documents(request: ExplainRequest):
    if not request.selected_file_names:
        raise HTTPException(
            status_code=400,
            detail="Please select at least one document."
        )

    try:
        return rag_service.explain_documents(
            selected_file_names=request.selected_file_names
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/generate-review-questions")
def generate_review_questions(request: ReviewQuestionRequest):
    if request.number_of_questions < 1:
        raise HTTPException(
            status_code=400,
            detail="Number of questions must be at least 1."
        )

    if request.number_of_questions > 30:
        raise HTTPException(
            status_code=400,
            detail="Number of questions cannot be more than 30."
        )

    try:
        return rag_service.generate_review_questions(
            number_of_questions=request.number_of_questions,
            selected_file_names=request.selected_file_names
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/evaluate-review-answer")
def evaluate_review_answer(request: EvaluateAnswerRequest):
    if not request.question.strip():
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty."
        )

    if not request.user_answer.strip():
        raise HTTPException(
            status_code=400,
            detail="Answer cannot be empty."
        )

    try:
        return rag_service.evaluate_review_answer(
            question=request.question,
            user_answer=request.user_answer,
            selected_file_names=request.selected_file_names
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/evaluate-review-form")
def evaluate_review_form(request: EvaluateReviewFormRequest):
    if not request.review_answers:
        raise HTTPException(
            status_code=400,
            detail="No review answers submitted."
        )

    try:
        review_answers = [
            {
                "question": item.question,
                "user_answer": item.user_answer
            }
            for item in request.review_answers
        ]

        return rag_service.evaluate_review_form(
            review_answers=review_answers,
            selected_file_names=request.selected_file_names
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.get("/documents")
def list_documents():
    try:
        return rag_service.list_documents()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.post("/delete-document")
def delete_document(request: DeleteDocumentRequest):
    if not request.file_name.strip():
        raise HTTPException(
            status_code=400,
            detail="File name cannot be empty."
        )

    try:
        return rag_service.delete_document(
            file_name=request.file_name
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@app.delete("/clear")
def clear_database():
    try:
        return rag_service.clear_database()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )