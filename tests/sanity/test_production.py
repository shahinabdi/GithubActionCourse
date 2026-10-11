import os

import httpx
import pytest


@pytest.mark.sanity
def test_production_health():
    base_url = os.environ["PRODUCTION_BASE_URL"].rstrip("/")
    response = httpx.get(f"{base_url}/api/v1/health", timeout=10)

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
