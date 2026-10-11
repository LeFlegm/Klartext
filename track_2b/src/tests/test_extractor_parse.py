from klartext.services.extractor import _parse


def test_empty_deadline_object_becomes_none():
    raw = (
        '{"document_type": "other", '
        '"sender": {"value": "A", "source_span": "A"}, '
        '"deadline": {"value": null, "source_span": null}, '
        '"actions": [], "consequences": []}'
    )
    assert _parse(raw).deadline is None