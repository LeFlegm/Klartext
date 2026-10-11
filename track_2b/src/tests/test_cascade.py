from types import SimpleNamespace

from klartext.services.pipeline import analyze_with_cascade


def fake_result(model, unverified):
    return SimpleNamespace(model_used=model, unverified_count=unverified, escalated=False, latency_ms=100)


def test_clean_small_answer_is_kept():
    calls = []

    def analyze(client, model, *args):
        calls.append(model)
        return fake_result(model, 0)

    result = analyze_with_cascade(None, "8b", "70b", "id", "f.pdf", "text", analyze=analyze)
    assert calls == ["8b"]
    assert result.escalated is False


def test_unverified_point_escalates_to_large_model():
    def analyze(client, model, *args):
        return fake_result(model, 2 if model == "8b" else 0)

    result = analyze_with_cascade(None, "8b", "70b", "id", "f.pdf", "text", analyze=analyze)
    assert result.model_used == "70b"
    assert result.escalated is True
    assert result.latency_ms == 200