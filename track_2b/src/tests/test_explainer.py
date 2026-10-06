from klartext.domain.models import Extraction, LetterResult
from klartext.services.explainer import facts_from


def test_unverified_points_never_reach_the_explanation():
    extraction = Extraction(
        document_type="tax",
        sender={"value": "Morges tax office", "source_span": "x", "verified": True},
        consequences=[
            {"value": "Official assessment", "source_span": "x", "verified": True},
            {"value": "Fine of CHF 500", "source_span": "x", "verified": False},
        ],
    )
    result = LetterResult(id="1", filename="a.pdf", extraction=extraction, model_used="m", latency_ms=0)

    facts = facts_from(result)
    assert "Official assessment" in facts
    assert "CHF 500" not in facts