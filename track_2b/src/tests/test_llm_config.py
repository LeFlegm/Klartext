import pytest

from klartext.adapters.llm import LLMConfigError, get_client


def test_missing_key_raises_clear_error(monkeypatch):
    monkeypatch.setenv("LLM_BASE_URL", "http://example.invalid/v1")
    monkeypatch.setenv("LLM_API_KEY", "")
    with pytest.raises(LLMConfigError):
        get_client()