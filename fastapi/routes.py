from fastapi import APIRouter
from rag_service import rag_service
from pydantic_models import QuestionRequest, QuestionResponse

router = APIRouter()

@router.post("/ask", response_model=QuestionResponse)
async def ask_question(question: QuestionRequest):
    # Use the RAG service to process the question and get an answer
    result = rag_service.query(question.question)
    # Return the answer and sources in the response
    return QuestionResponse(answer=result['answer'], sources=result['source_documents'])