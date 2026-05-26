from dataclasses import dataclass, field


@dataclass(frozen=True)
class SourceDocument:
    """A source document before chunking."""

    id: str
    text: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class DocumentChunk:
    """A chunk that can later be embedded and retrieved."""

    id: str
    document_id: str
    text: str
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class RetrievalResult:
    """A retrieved chunk plus score information."""

    chunk: DocumentChunk
    score: float


@dataclass(frozen=True)
class GeneratedAnswer:
    """An answer produced from retrieved evidence."""

    text: str
    citations: list[str] = field(default_factory=list)
    refused: bool = False
