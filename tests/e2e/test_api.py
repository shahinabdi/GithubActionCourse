import os

import httpx
import pytest


@pytest.fixture
def base_url():
    return os.environ["E2E_BASE_URL"].rstrip("/")


@pytest.mark.e2e
def test_preproduction_todo_flow(base_url):
    with httpx.Client(base_url=base_url, timeout=10) as client:
        health = client.get("/api/v1/health")
        assert health.status_code == 200
        assert health.json()["status"] == "ok"

        created = client.post("/api/v1/todos", json={"title": "pre-production check"})
        assert created.status_code == 201
        todo_id = created.json()["id"]

        try:
            toggled = client.patch(f"/api/v1/todos/{todo_id}/toggle")
            assert toggled.status_code == 200
            assert toggled.json()["done"] is True
        finally:
            assert client.delete(f"/api/v1/todos/{todo_id}").status_code == 204
