import pytest
from fastapi.testclient import TestClient

from smi_index_review.api.config import Settings, get_settings
from smi_index_review.api.index import app
from smi_index_review.processing.smi_review import SmiReview


@pytest.fixture
def client(project):
    output = project / "output" / "smi_review.json"
    app.dependency_overrides[get_settings] = lambda: Settings(output_path=output)
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_smi_data_route(client):
    SmiReview().to_json()
    response = client.get("/smi/data")
    assert response.status_code == 200
    assert len(response.json()) == 20


def test_joiners_route(client):
    SmiReview().to_json()
    response = client.get("/joiners")
    assert [stock["id"] for stock in response.json()] == [17, 18]


def test_leavers_route(client):
    SmiReview().to_json()
    response = client.get("/leavers")
    assert [stock["id"] for stock in response.json()] == [23, 24]


def test_constituents_route(client):
    SmiReview().to_json()
    first = client.get("/constituents").json()[0]
    assert first["id"] == 1
    assert first["weights"]["capped_weight"] == pytest.approx(0.18)


def test_missing_output_file_returns_404(client):
    response = client.get("/smi/data")
    assert response.status_code == 404


def test_schema_route(client):
    response = client.get("/dataset/schema")
    assert response.status_code == 200
