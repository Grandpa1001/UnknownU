from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.engine import service
from app.main import app


@pytest.fixture
def client(tmp_path):
    service.db_path = tmp_path / "unknown.db"
    service.world = None
    with TestClient(app) as test_client:
        yield test_client
    service.stop()
    service.world = None
