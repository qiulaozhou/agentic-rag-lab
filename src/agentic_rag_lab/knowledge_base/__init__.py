"""Local knowledge base boundary."""

from agentic_rag_lab.knowledge_base.disk import DiskBackedKnowledgeBaseRegistry
from agentic_rag_lab.knowledge_base.local import (
    InMemoryKnowledgeBaseRegistry,
    LocalKnowledgeBase,
)

__all__ = [
    "DiskBackedKnowledgeBaseRegistry",
    "InMemoryKnowledgeBaseRegistry",
    "LocalKnowledgeBase",
]
