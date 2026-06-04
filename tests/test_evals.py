import pytest

from agentic_rag_lab.evals import (
    EvalCase,
    EvalRunConfig,
    compare_eval_reports,
    run_eval_cases,
    run_eval_cases_with_config,
    run_eval_cases_with_pipeline_factory,
)
from agentic_rag_lab.schemas import GeneratedAnswer, SourceDocument


def test_eval_case_passes_answer_citation_and_refusal_checks() -> None:
    report = run_eval_cases(
        [
            EvalCase(
                id="answer-citation",
                question="answer pipeline citation traceability",
                documents=[
                    _document(
                        text="Answer pipeline citation traceability keeps RAG outputs inspectable.",
                        source_path="docs/rag.md",
                    )
                ],
                expected_refused=False,
                expected_citations=["docs/rag.md#chunk-0"],
                required_answer_terms=["traceability", "inspectable"],
            )
        ],
        chunk_size=120,
    )

    result = report.results[0]

    assert report.total == 1
    assert report.passed == 1
    assert report.failed == 0
    assert result.answer.refused is False
    assert result.answer_passed is True
    assert result.citation_passed is True
    assert result.refusal_passed is True


def test_eval_case_passes_for_expected_refusal() -> None:
    report = run_eval_cases(
        [
            EvalCase(
                id="expected-refusal",
                question="unrelated query",
                documents=[
                    _document(
                        text="!!!",
                        source_path="docs/symbols.txt",
                    )
                ],
                expected_refused=True,
            )
        ],
        chunk_size=120,
    )

    result = report.results[0]

    assert result.answer.refused is True
    assert result.answer.citations == []
    assert result.answer_passed is True
    assert result.citation_passed is True
    assert result.refusal_passed is True
    assert result.passed is True


def test_eval_case_fails_when_expected_citation_is_missing() -> None:
    report = run_eval_cases(
        [
            EvalCase(
                id="missing-citation",
                question="answer pipeline citation traceability",
                documents=[
                    _document(
                        text="Answer pipeline citation traceability keeps RAG outputs inspectable.",
                        source_path="docs/rag.md",
                    )
                ],
                expected_refused=False,
                expected_citations=["docs/wrong.md#chunk-0"],
                required_answer_terms=["traceability"],
            )
        ],
        chunk_size=120,
    )

    result = report.results[0]

    assert result.answer_passed is True
    assert result.citation_passed is False
    assert result.refusal_passed is True
    assert result.passed is False


def test_eval_case_fails_when_required_answer_term_is_missing() -> None:
    report = run_eval_cases(
        [
            EvalCase(
                id="missing-answer-term",
                question="answer pipeline citation traceability",
                documents=[
                    _document(
                        text="Answer pipeline citation traceability keeps RAG outputs inspectable.",
                        source_path="docs/rag.md",
                    )
                ],
                expected_refused=False,
                expected_citations=["docs/rag.md#chunk-0"],
                required_answer_terms=["not-present"],
            )
        ],
        chunk_size=120,
    )

    result = report.results[0]

    assert result.answer_passed is False
    assert result.citation_passed is True
    assert result.refusal_passed is True
    assert result.passed is False


def test_eval_report_summarizes_multiple_cases() -> None:
    report = run_eval_cases(
        [
            EvalCase(
                id="pass-answer",
                question="answer pipeline citation traceability",
                documents=[
                    _document(
                        text="Answer pipeline citation traceability keeps RAG outputs inspectable.",
                        source_path="docs/rag.md",
                    )
                ],
                expected_refused=False,
                expected_citations=["docs/rag.md#chunk-0"],
                required_answer_terms=["inspectable"],
            ),
            EvalCase(
                id="pass-refusal",
                question="unrelated query",
                documents=[_document(text="!!!", source_path="docs/symbols.txt")],
                expected_refused=True,
            ),
            EvalCase(
                id="fail-answer",
                question="answer pipeline citation traceability",
                documents=[
                    _document(
                        text="Answer pipeline citation traceability keeps RAG outputs inspectable.",
                        source_path="docs/rag.md",
                    )
                ],
                expected_refused=False,
                expected_citations=["docs/rag.md#chunk-0"],
                required_answer_terms=["missing"],
            ),
        ],
        chunk_size=120,
    )

    assert report.total == 3
    assert report.passed == 2
    assert report.failed == 1
    assert report.answer_passed == 2
    assert report.citation_passed == 3
    assert report.refusal_passed == 3


def test_eval_case_supports_empty_question_refusal() -> None:
    report = run_eval_cases(
        [
            EvalCase(
                id="empty-question",
                question="   ",
                documents=[
                    _document(
                        text="RAG outputs need refusal behavior.",
                        source_path="docs/refusal.md",
                    )
                ],
                expected_refused=True,
            )
        ],
        chunk_size=120,
    )

    result = report.results[0]

    assert result.answer.refused is True
    assert result.passed is True


def test_eval_runner_supports_custom_pipeline_factory() -> None:
    report = run_eval_cases_with_pipeline_factory(
        [
            EvalCase(
                id="custom-pipeline",
                question="custom provider answer",
                documents=[_document(text="not used by fake pipeline", source_path="docs/rag.md")],
                expected_refused=False,
                expected_citations=["docs/custom.md#chunk-0"],
                required_answer_terms=["custom", "provider"],
            )
        ],
        chunk_size=120,
        pipeline_factory=lambda case, chunk_size, overlap: _StaticPipeline(
            GeneratedAnswer(
                text="custom provider answer",
                citations=["docs/custom.md#chunk-0"],
                refused=False,
            )
        ),
    )

    result = report.results[0]

    assert result.passed is True
    assert result.answer.text == "custom provider answer"


def test_eval_runner_supports_run_config() -> None:
    config = EvalRunConfig(
        label="candidate",
        chunk_size=120,
        pipeline_factory=lambda case, chunk_size, overlap: _StaticPipeline(
            GeneratedAnswer(
                text="configured provider answer",
                citations=["docs/config.md#chunk-0"],
                refused=False,
            )
        ),
    )

    report = run_eval_cases_with_config(
        [
            EvalCase(
                id="configured",
                question="configured provider",
                documents=[_document(text="not used", source_path="docs/rag.md")],
                expected_refused=False,
                expected_citations=["docs/config.md#chunk-0"],
                required_answer_terms=["configured"],
            )
        ],
        config,
    )

    assert report.passed == 1


def test_eval_comparison_has_no_delta_when_reports_match() -> None:
    baseline = run_eval_cases(
        [
            EvalCase(
                id="same",
                question="answer pipeline citation traceability",
                documents=[
                    _document(
                        text="Answer pipeline citation traceability keeps RAG outputs inspectable.",
                        source_path="docs/rag.md",
                    )
                ],
                expected_refused=False,
                expected_citations=["docs/rag.md#chunk-0"],
                required_answer_terms=["traceability"],
            )
        ],
        chunk_size=120,
    )
    candidate = run_eval_cases(
        [
            EvalCase(
                id="same",
                question="answer pipeline citation traceability",
                documents=[
                    _document(
                        text="Answer pipeline citation traceability keeps RAG outputs inspectable.",
                        source_path="docs/rag.md",
                    )
                ],
                expected_refused=False,
                expected_citations=["docs/rag.md#chunk-0"],
                required_answer_terms=["traceability"],
            )
        ],
        chunk_size=120,
    )

    comparison = compare_eval_reports("local", baseline, "candidate", candidate)

    assert comparison.baseline_label == "local"
    assert comparison.candidate_label == "candidate"
    assert comparison.total == 1
    assert comparison.passed_delta == 0
    assert comparison.answer_passed_delta == 0
    assert comparison.citation_passed_delta == 0
    assert comparison.refusal_passed_delta == 0
    assert comparison.changed_case_ids == []


def test_eval_comparison_detects_answer_delta() -> None:
    baseline = _report(
        "case-1",
        GeneratedAnswer(text="expected term", citations=["docs/rag.md#chunk-0"]),
        answer_passed=True,
        citation_passed=True,
        refusal_passed=True,
    )
    candidate = _report(
        "case-1",
        GeneratedAnswer(text="missing", citations=["docs/rag.md#chunk-0"]),
        answer_passed=False,
        citation_passed=True,
        refusal_passed=True,
    )

    comparison = compare_eval_reports("local", baseline, "candidate", candidate)

    assert comparison.passed_delta == -1
    assert comparison.answer_passed_delta == -1
    assert comparison.citation_passed_delta == 0
    assert comparison.refusal_passed_delta == 0
    assert comparison.changed_case_ids == ["case-1"]


def test_eval_comparison_detects_citation_delta() -> None:
    baseline = _report(
        "case-1",
        GeneratedAnswer(text="answer", citations=["docs/rag.md#chunk-0"]),
        answer_passed=True,
        citation_passed=True,
        refusal_passed=True,
    )
    candidate = _report(
        "case-1",
        GeneratedAnswer(text="answer", citations=["docs/other.md#chunk-0"]),
        answer_passed=True,
        citation_passed=False,
        refusal_passed=True,
    )

    comparison = compare_eval_reports("local", baseline, "candidate", candidate)

    assert comparison.citation_passed_delta == -1
    assert comparison.changed_case_ids == ["case-1"]


def test_eval_comparison_detects_refusal_delta() -> None:
    baseline = _report(
        "case-1",
        GeneratedAnswer(text="answer", citations=["docs/rag.md#chunk-0"], refused=False),
        answer_passed=True,
        citation_passed=True,
        refusal_passed=True,
    )
    candidate = _report(
        "case-1",
        GeneratedAnswer(text="refused", citations=[], refused=True),
        answer_passed=True,
        citation_passed=True,
        refusal_passed=False,
    )

    comparison = compare_eval_reports("local", baseline, "candidate", candidate)

    assert comparison.refusal_passed_delta == -1
    assert comparison.changed_case_ids == ["case-1"]


def test_eval_comparison_requires_matching_case_ids() -> None:
    baseline = _report(
        "baseline",
        GeneratedAnswer(text="answer"),
        answer_passed=True,
        citation_passed=True,
        refusal_passed=True,
    )
    candidate = _report(
        "candidate",
        GeneratedAnswer(text="answer"),
        answer_passed=True,
        citation_passed=True,
        refusal_passed=True,
    )

    with pytest.raises(ValueError, match="same case ids"):
        compare_eval_reports("local", baseline, "candidate", candidate)


def _document(text: str, source_path: str) -> SourceDocument:
    return SourceDocument(
        id=source_path,
        text=text,
        metadata={"source_path": source_path, "file_type": ".md"},
    )


class _StaticPipeline:
    def __init__(self, answer: GeneratedAnswer) -> None:
        self._answer = answer

    async def answer(self, question: str, limit: int = 5) -> GeneratedAnswer:
        return self._answer


def _report(
    case_id: str,
    answer: GeneratedAnswer,
    answer_passed: bool,
    citation_passed: bool,
    refusal_passed: bool,
):
    from agentic_rag_lab.evals import EvalReport, EvalResult

    return EvalReport(
        results=[
            EvalResult(
                case_id=case_id,
                answer=answer,
                answer_passed=answer_passed,
                citation_passed=citation_passed,
                refusal_passed=refusal_passed,
            )
        ]
    )
