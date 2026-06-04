from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from agentic_rag_lab.generation import LocalAnswerPipeline
from agentic_rag_lab.schemas import SourceDocument

router = APIRouter(tags=["answer"])


class AnswerDocument(BaseModel):
    id: str
    text: str
    metadata: dict[str, str | int] = Field(default_factory=dict)


class AnswerRequest(BaseModel):
    question: str
    documents: list[AnswerDocument] = Field(default_factory=list)
    chunk_size: int = 400
    overlap: int = 0
    limit: int = 5


class AnswerResponse(BaseModel):
    text: str
    citations: list[str]
    refused: bool


@router.post("/answer", response_model=AnswerResponse)
async def answer(request_body: AnswerRequest, request: Request) -> AnswerResponse:
    _validate_request(request_body)
    documents = [
        SourceDocument(
            id=document.id,
            text=document.text,
            metadata=dict(document.metadata),
        )
        for document in request_body.documents
    ]

    try:
        pipeline = LocalAnswerPipeline.from_documents(
            documents,
            chunk_size=request_body.chunk_size,
            overlap=request_body.overlap,
            embedding_provider=request.app.state.embedding_provider,
            answer_generator=request.app.state.answer_generator,
        )
        generated_answer = await pipeline.answer(
            request_body.question,
            limit=request_body.limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return AnswerResponse(
        text=generated_answer.text,
        citations=generated_answer.citations,
        refused=generated_answer.refused,
    )


def _validate_request(request: AnswerRequest) -> None:
    if request.chunk_size <= 0:
        raise HTTPException(status_code=400, detail="chunk_size must be greater than 0")
    if request.overlap < 0:
        raise HTTPException(status_code=400, detail="overlap must be greater than or equal to 0")
    if request.overlap >= request.chunk_size:
        raise HTTPException(status_code=400, detail="overlap must be smaller than chunk_size")
    if request.limit <= 0:
        raise HTTPException(status_code=400, detail="limit must be greater than 0")


__all__ = [
    "AnswerDocument",
    "AnswerRequest",
    "AnswerResponse",
    "router",
]
