"""
PrivacyLens evaluation scorers.

Code-based scorers (exact, cheap, deterministic):
  retrieval_hit        did retrieval bring back the expected articles?
  citation_recall      did the answer cite the expected articles?
  citation_valid       was every cited article actually retrieved (no invented citations)?
  no_hedged_citation   did the answer avoid "[X] or [Y]" style hedges?
  refusal_correct      refused exactly when it should (traps), answered otherwise?

LLM-judge scorers (Databricks-hosted judges, separate from the Llama writer):
  grounded             is every claim supported by the retrieved text?
  correct              does the answer contain the expected key facts?

For trap questions, scorers that do not apply return "yes" with a rationale
saying so; read trap results through refusal_correct.
"""

import re
from mlflow.entities import Feedback, SpanType
from mlflow.genai.scorers import scorer
from mlflow.genai.judges import is_correct, is_grounded

REFUSAL = "I could not find this in the GDPR or DPDP Act text provided."
CITE_RE = re.compile(r"\[((?:GDPR Article|DPDP Section) \d+|DPDP Schedule)\]")
HEDGE_RE = re.compile(r"\]\s*or\s*\[", re.IGNORECASE)


def _answer(outputs):
    return (outputs or {}).get("answer") or ""


def _retrieved(outputs):
    raw = (outputs or {}).get("sources") or ""
    return {s.strip() for s in raw.split(";") if s.strip()}


def _cited(answer):
    return set(CITE_RE.findall(answer))


def _is_refusal(answer):
    return REFUSAL.lower() in answer.lower()


def _groups_covered(groups, found):
    """Each group is a list of acceptable citations; every group needs one match."""
    missing = [g for g in groups if not any(c in found for c in g)]
    return len(missing) == 0, missing


def _not_applicable():
    return Feedback(value="yes", rationale="Not applicable to trap questions.")


@scorer
def retrieval_hit(outputs, expectations):
    if expectations.get("should_refuse"):
        return _not_applicable()
    ok, missing = _groups_covered(expectations["expected_sources"], _retrieved(outputs))
    return Feedback(
        value="yes" if ok else "no",
        rationale="All expected articles retrieved." if ok else f"Not retrieved: {missing}",
    )


@scorer
def citation_recall(outputs, expectations):
    if expectations.get("should_refuse"):
        return _not_applicable()
    ok, missing = _groups_covered(expectations["expected_sources"], _cited(_answer(outputs)))
    return Feedback(
        value="yes" if ok else "no",
        rationale="All expected articles cited." if ok else f"Not cited: {missing}",
    )


@scorer
def citation_valid(outputs):
    invented = _cited(_answer(outputs)) - _retrieved(outputs)
    return Feedback(
        value="no" if invented else "yes",
        rationale=f"Cited but never retrieved: {sorted(invented)}" if invented
        else "Every citation was retrieved.",
    )


@scorer
def no_hedged_citation(outputs):
    hedged = bool(HEDGE_RE.search(_answer(outputs)))
    return Feedback(
        value="no" if hedged else "yes",
        rationale="Answer hedges between citations ('[X] or [Y]')." if hedged
        else "No hedged citations.",
    )


@scorer
def refusal_correct(outputs, expectations):
    refused = _is_refusal(_answer(outputs))
    should = bool(expectations.get("should_refuse"))
    ok = refused == should
    if should:
        why = "Correctly refused." if ok else "Should have refused but answered."
    else:
        why = "Correctly answered." if ok else "Refused a question it should answer."
    return Feedback(value="yes" if ok else "no", rationale=why)


@scorer
def grounded(inputs, outputs, trace):
    answer = _answer(outputs)
    if _is_refusal(answer):
        return Feedback(value="yes", rationale="Refusal makes no claims.")
    spans = trace.search_spans(span_type=SpanType.RETRIEVER)
    hits = spans[0].outputs if spans else []
    context = "\n\n".join(h.get("chunk_text", "") for h in (hits or []))
    return is_grounded(
        request=inputs["question"],
        response=answer,
        context=context,
        name="grounded",
    )


@scorer
def correct(inputs, outputs, expectations):
    if expectations.get("should_refuse"):
        return _not_applicable()
    return is_correct(
        request=inputs["question"],
        response=_answer(outputs),
        expected_facts=expectations["expected_facts"],
        name="correct",
    )


ALL_SCORERS = [
    retrieval_hit,
    citation_recall,
    citation_valid,
    no_hedged_citation,
    refusal_correct,
    grounded,
    correct,
]