"""Deterministic local RAG evaluation helpers."""

from __future__ import annotations

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Protocol

from agentic_rag_lab.generation import LocalAnswerPipeline
from agentic_rag_lab.schemas import GeneratedAnswer, SourceDocument


@dataclass(frozen=True)
class EvalCase:
    """A small local RAG evaluation case."""

    id: str
    question: str
    documents: list[SourceDocument]
    expected_refused: bool
    expected_citations: list[str] = field(default_factory=list)
    required_answer_terms: list[str] = field(default_factory=list)


class EvalAnswerPipeline(Protocol):
    """Minimal answer pipeline behavior needed by evals."""

    async def answer(self, question: str, limit: int = 5) -> GeneratedAnswer:
        """Answer an eval question."""


PipelineFactory = Callable[[EvalCase, int, int], EvalAnswerPipeline]


@dataclass(frozen=True)
class EvalRunConfig:
    """Configuration for one eval run."""

    label: str
    chunk_size: int
    overlap: int = 0
    pipeline_factory: PipelineFactory | None = None


@dataclass(frozen=True)
class EvalResult:
    """Result for one eval case."""

    case_id: str
    answer: GeneratedAnswer
    answer_passed: bool
    citation_passed: bool
    refusal_passed: bool

    @property
    def passed(self) -> bool:
        return self.answer_passed and self.citation_passed and self.refusal_passed


@dataclass(frozen=True)
class EvalReport:
    """Aggregated eval report."""

    results: list[EvalResult]

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def passed(self) -> int:
        return sum(1 for result in self.results if result.passed)

    @property
    def failed(self) -> int:
        return self.total - self.passed

    @property
    def answer_passed(self) -> int:
        return sum(1 for result in self.results if result.answer_passed)

    @property
    def citation_passed(self) -> int:
        return sum(1 for result in self.results if result.citation_passed)

    @property
    def refusal_passed(self) -> int:
        return sum(1 for result in self.results if result.refusal_passed)


@dataclass(frozen=True)
class EvalComparisonReport:
    """Compare baseline and candidate eval reports."""

    baseline_label: str
    candidate_label: str
    baseline_report: EvalReport
    candidate_report: EvalReport
    changed_case_ids: list[str]

    @property
    def total(self) -> int:
        return self.baseline_report.total

    @property
    def passed_delta(self) -> int:
        return self.candidate_report.passed - self.baseline_report.passed

    @property
    def answer_passed_delta(self) -> int:
        return self.candidate_report.answer_passed - self.baseline_report.answer_passed

    @property
    def citation_passed_delta(self) -> int:
        return self.candidate_report.citation_passed - self.baseline_report.citation_passed

    @property
    def refusal_passed_delta(self) -> int:
        return self.candidate_report.refusal_passed - self.baseline_report.refusal_passed


def run_eval_cases(
    cases: list[EvalCase],
    chunk_size: int,
    overlap: int = 0,
) -> EvalReport:
    """Run local eval cases through LocalAnswerPipeline."""

    return run_eval_cases_with_pipeline_factory(
        cases,
        chunk_size=chunk_size,
        overlap=overlap,
    )


def run_eval_cases_with_pipeline_factory(
    cases: list[EvalCase],
    chunk_size: int,
    overlap: int = 0,
    pipeline_factory: PipelineFactory | None = None,
) -> EvalReport:
    """Run eval cases with a custom answer pipeline factory."""

    return asyncio.run(
        _run_eval_cases(
            cases,
            chunk_size=chunk_size,
            overlap=overlap,
            pipeline_factory=pipeline_factory,
        )
    )


def run_eval_cases_with_config(
    cases: list[EvalCase],
    config: EvalRunConfig,
) -> EvalReport:
    """Run eval cases from a named eval run config."""

    return run_eval_cases_with_pipeline_factory(
        cases,
        chunk_size=config.chunk_size,
        overlap=config.overlap,
        pipeline_factory=config.pipeline_factory,
    )


def compare_eval_reports(
    baseline_label: str,
    baseline_report: EvalReport,
    candidate_label: str,
    candidate_report: EvalReport,
) -> EvalComparisonReport:
    """Compare two eval reports by case id."""

    baseline_by_id = _results_by_case_id(baseline_report)
    candidate_by_id = _results_by_case_id(candidate_report)
    if set(baseline_by_id) != set(candidate_by_id):
        raise ValueError("Eval reports must contain the same case ids")

    changed_case_ids = [
        result.case_id
        for result in baseline_report.results
        if _result_changed(result, candidate_by_id[result.case_id])
    ]

    return EvalComparisonReport(
        baseline_label=baseline_label,
        candidate_label=candidate_label,
        baseline_report=baseline_report,
        candidate_report=candidate_report,
        changed_case_ids=changed_case_ids,
    )


async def _run_eval_cases(
    cases: list[EvalCase],
    chunk_size: int,
    overlap: int,
    pipeline_factory: PipelineFactory | None,
) -> EvalReport:
    results: list[EvalResult] = []
    for case in cases:
        pipeline = _build_pipeline(case, chunk_size, overlap, pipeline_factory)
        answer = await pipeline.answer(case.question)
        results.append(_evaluate_answer(case, answer))

    return EvalReport(results=results)


def _build_pipeline(
    case: EvalCase,
    chunk_size: int,
    overlap: int,
    pipeline_factory: PipelineFactory | None,
) -> EvalAnswerPipeline:
    if pipeline_factory is not None:
        return pipeline_factory(case, chunk_size, overlap)

    return LocalAnswerPipeline.from_documents(
        case.documents,
        chunk_size=chunk_size,
        overlap=overlap,
    )


def _evaluate_answer(case: EvalCase, answer: GeneratedAnswer) -> EvalResult:
    refusal_passed = answer.refused == case.expected_refused
    if case.expected_refused:
        answer_passed = True
        citation_passed = True
    else:
        answer_passed = _contains_all_terms(answer.text, case.required_answer_terms)
        citation_passed = all(
            citation in answer.citations
            for citation in case.expected_citations
        )

    return EvalResult(
        case_id=case.id,
        answer=answer,
        answer_passed=answer_passed,
        citation_passed=citation_passed,
        refusal_passed=refusal_passed,
    )


def _contains_all_terms(text: str, terms: list[str]) -> bool:
    normalized_text = text.lower()
    return all(term.lower() in normalized_text for term in terms)


def _results_by_case_id(report: EvalReport) -> dict[str, EvalResult]:
    results: dict[str, EvalResult] = {}
    for result in report.results:
        if result.case_id in results:
            raise ValueError(f"Duplicate eval case id: {result.case_id}")
        results[result.case_id] = result
    return results


def _result_changed(baseline: EvalResult, candidate: EvalResult) -> bool:
    return (
        baseline.passed != candidate.passed
        or baseline.answer_passed != candidate.answer_passed
        or baseline.citation_passed != candidate.citation_passed
        or baseline.refusal_passed != candidate.refusal_passed
        or baseline.answer.refused != candidate.answer.refused
        or baseline.answer.citations != candidate.answer.citations
    )


__all__ = [
    "EvalCase",
    "EvalComparisonReport",
    "EvalReport",
    "EvalResult",
    "EvalRunConfig",
    "compare_eval_reports",
    "run_eval_cases",
    "run_eval_cases_with_config",
    "run_eval_cases_with_pipeline_factory",
]
