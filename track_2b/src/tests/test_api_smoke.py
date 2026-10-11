from klartext.api.main import app


def test_app_imports_and_exposes_routes():
    paths = {route.path for route in app.routes}
    assert "/health" in paths
    assert "/documents/{doc_id}/extract" in paths
    assert "/letters" in paths