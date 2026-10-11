import pytest
from fastapi.testclient import TestClient

from app.api import create_api_app


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv("APP_ENV", "dev")
    return TestClient(create_api_app(str(tmp_path / "test.db")))


@pytest.mark.unit
def test_health_reports_environment(client):
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "environment": "dev",
        "version": "dev",
    }


@pytest.mark.unit
def test_todo_lifecycle(client):
    created = client.post("/api/v1/todos", json={"title": "write tests"})
    todo_id = created.json()["id"]

    assert created.status_code == 201
    assert client.get("/api/v1/todos").json()[0]["title"] == "write tests"
    assert client.patch(f"/api/v1/todos/{todo_id}/toggle").json()["done"] is True
    assert client.delete(f"/api/v1/todos/{todo_id}").status_code == 204
    assert client.get("/api/v1/todos").json() == []
