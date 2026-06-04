"""HTTP API for reusable local knowledge bases."""

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from agentic_rag_lab.ingestion import load_directory, load_text_file
from agentic_rag_lab.schemas import SourceDocument

router = APIRouter(tags=["knowledge-bases"])


class KnowledgeBaseDocument(BaseModel):
    id: str
    text: str
    metadata: dict[str, str | int] = Field(default_factory=dict)


class CreateKnowledgeBaseRequest(BaseModel):
    documents: list[KnowledgeBaseDocument] = Field(default_factory=list)
    chunk_size: int = 400
    overlap: int = 0


class CreateKnowledgeBaseFromFileRequest(BaseModel):
    path: str
    chunk_size: int = 400
    overlap: int = 0


class CreateKnowledgeBaseFromDirectoryRequest(BaseModel):
    path: str
    chunk_size: int = 400
    overlap: int = 0
    extensions: list[str] | None = None


class CreateKnowledgeBaseResponse(BaseModel):
    knowledge_base_id: str
    document_count: int
    chunk_count: int


class KnowledgeBaseAnswerRequest(BaseModel):
    question: str
    limit: int = 5


class KnowledgeBaseAnswerResponse(BaseModel):
    text: str
    citations: list[str]
    refused: bool


@router.post("/knowledge-bases", response_model=CreateKnowledgeBaseResponse)
async def create_knowledge_base(
    request_body: CreateKnowledgeBaseRequest,
    request: Request,
) -> CreateKnowledgeBaseResponse:
    _validate_chunking_request(request_body.chunk_size, request_body.overlap)
    documents = [
        SourceDocument(
            id=document.id,
            text=document.text,
            metadata=dict(document.metadata),
        )
        for document in request_body.documents
    ]

    return _create_knowledge_base_response(
        request=request,
        documents=documents,
        chunk_size=request_body.chunk_size,
        overlap=request_body.overlap,
    )


@router.post("/knowledge-bases/from-file", response_model=CreateKnowledgeBaseResponse)
async def create_knowledge_base_from_file(
    request_body: CreateKnowledgeBaseFromFileRequest,
    request: Request,
) -> CreateKnowledgeBaseResponse:
    _validate_chunking_request(request_body.chunk_size, request_body.overlap)

    try:
        document = load_text_file(request_body.path)
    except (FileNotFoundError, OSError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _create_knowledge_base_response(
        request=request,
        documents=[document],
        chunk_size=request_body.chunk_size,
        overlap=request_body.overlap,
    )


@router.post(
    "/knowledge-bases/from-directory",
    response_model=CreateKnowledgeBaseResponse,
)
async def create_knowledge_base_from_directory(
    request_body: CreateKnowledgeBaseFromDirectoryRequest,
    request: Request,
) -> CreateKnowledgeBaseResponse:
    _validate_chunking_request(request_body.chunk_size, request_body.overlap)

    extensions = set(request_body.extensions) if request_body.extensions else None
    try:
        documents = load_directory(request_body.path, extensions=extensions)
    except (NotADirectoryError, OSError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return _create_knowledge_base_response(
        request=request,
        documents=documents,
        chunk_size=request_body.chunk_size,
        overlap=request_body.overlap,
    )


@router.post(
    "/knowledge-bases/{knowledge_base_id}/answer",
    response_model=KnowledgeBaseAnswerResponse,
)
async def answer_from_knowledge_base(
    knowledge_base_id: str,
    request_body: KnowledgeBaseAnswerRequest,
    request: Request,
) -> KnowledgeBaseAnswerResponse:
    if request_body.limit <= 0:
        raise HTTPException(status_code=400, detail="limit must be greater than 0")

    try:
        knowledge_base = _registry(request).get(knowledge_base_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    try:
        generated_answer = await knowledge_base.answer(
            request_body.question,
            limit=request_body.limit,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return KnowledgeBaseAnswerResponse(
        text=generated_answer.text,
        citations=generated_answer.citations,
        refused=generated_answer.refused,
    )


def _registry(request: Request):
    return request.app.state.knowledge_bases


def _create_knowledge_base_response(
    request: Request,
    documents: list[SourceDocument],
    chunk_size: int,
    overlap: int,
) -> CreateKnowledgeBaseResponse:
    try:
        knowledge_base = _registry(request).create(
            documents=documents,
            chunk_size=chunk_size,
            overlap=overlap,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return CreateKnowledgeBaseResponse(
        knowledge_base_id=knowledge_base.id,
        document_count=knowledge_base.document_count,
        chunk_count=knowledge_base.chunk_count,
    )


def _validate_chunking_request(chunk_size: int, overlap: int) -> None:
    if chunk_size <= 0:
        raise HTTPException(status_code=400, detail="chunk_size must be greater than 0")
    if overlap < 0:
        raise HTTPException(
            status_code=400,
            detail="overlap must be greater than or equal to 0",
        )
    if overlap >= chunk_size:
        raise HTTPException(status_code=400, detail="overlap must be smaller than chunk_size")


__all__ = [
    "CreateKnowledgeBaseFromDirectoryRequest",
    "CreateKnowledgeBaseFromFileRequest",
    "CreateKnowledgeBaseRequest",
    "CreateKnowledgeBaseResponse",
    "KnowledgeBaseAnswerRequest",
    "KnowledgeBaseAnswerResponse",
    "KnowledgeBaseDocument",
    "router",
]
