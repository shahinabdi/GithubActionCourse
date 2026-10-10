import pytest

from app import create_app


@pytest.fixture
def client(tmp_path):
    app = create_app(str(tmp_path / "test.db"))
    return app.test_client()


def test_health(client):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json["status"] == "ok"


def test_add_toggle_delete(client):
    client.post("/add", data={"title": "write tests"})
    assert b"write tests" in client.get("/").data

    client.post("/toggle/1")
    assert b'class="done"' in client.get("/").data

    client.post("/delete/1")
    assert b"write tests" not in client.get("/").data
