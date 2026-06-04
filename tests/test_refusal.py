import pytest

from agentic_rag_lab.generation import MinimumEvidenceRefusalPolicy
from agentic_rag_lab.schemas import DocumentChunk, RetrievalResult


def test_policy_refuses_empty_query() -> None:
    policy = MinimumEvidenceRefusalPolicy()

    assert policy.should_refuse("   ", [_result(score=1.0)]) is True


def test_policy_refuses_empty_evidence() -> None:
    policy = MinimumEvidenceRefusalPolicy()

    assert policy.should_refuse("retrieval", []) is True


def test_policy_refuses_when_highest_score_is_below_min_score() -> None:
    policy = MinimumEvidenceRefusalPolicy(min_score=0.25)

    assert policy.should_refuse("retrieval", [_result(score=0.24)]) is True


def test_policy_allows_when_highest_score_equals_min_score() -> None:
    policy = MinimumEvidenceRefusalPolicy(min_score=0.25)

    assert policy.should_refuse("retrieval", [_result(score=0.25)]) is False


def test_policy_allows_when_any_evidence_meets_min_score() -> None:
    policy = MinimumEvidenceRefusalPolicy(min_score=0.25)

    assert policy.should_refuse(
        "retrieval",
        [_result(score=0.1), _result(score=0.5)],
    ) is False


def test_policy_validates_min_score() -> None:
    with pytest.raises(ValueError):
        MinimumEvidenceRefusalPolicy(min_score=-0.1)


def test_custom_min_score_changes_policy_behavior() -> None:
    lenient_policy = MinimumEvidenceRefusalPolicy(min_score=0.1)
    strict_policy = MinimumEvidenceRefusalPolicy(min_score=0.9)
    evidence = [_result(score=0.5)]

    assert lenient_policy.should_refuse("retrieval", evidence) is False
    assert strict_policy.should_refuse("retrieval", evidence) is True


def _result(score: float) -> RetrievalResult:
    return RetrievalResult(
        chunk=DocumentChunk(
            id="chunk-1",
            document_id="doc-1",
            text="retrieval evidence",
            metadata={},
        ),
        score=score,
    )
