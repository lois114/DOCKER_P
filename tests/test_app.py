import pytest
import json


@pytest.fixture(scope="module")
def client():
    from app import app
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_index_status_code(client):
    response = client.get("/")
    assert response.status_code == 200


def test_index_is_html(client):
    response = client.get("/")
    assert b"Projet DevOps" in response.data


def test_health_status_code(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_response_body(client):
    response = client.get("/health")
    data = json.loads(response.data)
    assert data["status"] == "ok"


def test_api_data_status_code(client):
    response = client.get("/api/data")
    assert response.status_code == 200


def test_api_data_has_data_key(client):
    response = client.get("/api/data")
    data = json.loads(response.data)
    assert "data" in data


def test_api_data_is_list(client):
    response = client.get("/api/data")
    data = json.loads(response.data)
    assert isinstance(data["data"], list)


def test_metrics_endpoint_accessible(client):
    client.get("/health")
    response = client.get("/metrics")
    assert response.status_code == 200
