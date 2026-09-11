from __future__ import annotations

import time

from fastapi.testclient import TestClient

from app.main import app


def _create(client: TestClient) -> int:
    response = client.post(
        "/api/worlds",
        json={"name": "lokalny", "organism_count": 3, "seed": 1},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["id"] is not None
    assert body["status"] == "running"
    return int(body["id"])


def test_only_mutating_route_is_create_world() -> None:
    posts = [path for path, ops in app.openapi()["paths"].items() if "post" in ops]
    assert posts == ["/api/worlds"]


def test_create_and_get_world(client: TestClient) -> None:
    world_id = _create(client)
    response = client.get(f"/api/worlds/{world_id}")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == world_id
    assert body["tick"] >= 0
    assert body["trees"]
    assert body["apples"]
    assert body["flowers"]
    assert body["terrain"]
    assert len(body["organisms"]) == 3
    assert "x" in body["organisms"][0]["position"]
    assert "y" in body["organisms"][0]["position"]


def test_two_gets_show_live_motion(client: TestClient) -> None:
    world_id = _create(client)
    first = client.get(f"/api/worlds/{world_id}").json()
    time.sleep(1.2)
    second = client.get(f"/api/worlds/{world_id}").json()
    assert second["tick"] > first["tick"]
    positions_changed = any(
        a["position"] != b["position"]
        for a, b in zip(first["organisms"], second["organisms"], strict=False)
    )
    assert positions_changed or second["tick"] > first["tick"] + 5


def test_stats_events_and_organism(client: TestClient) -> None:
    world_id = _create(client)
    stats = client.get(f"/api/worlds/{world_id}/stats")
    assert stats.status_code == 200
    assert stats.json()["population"] == 3
    events = client.get(f"/api/worlds/{world_id}/events?limit=50")
    assert events.status_code == 200
    assert "events" in events.json()
    organism = client.get("/api/organisms/org_1")
    assert organism.status_code == 200
    body = organism.json()
    assert body["id"] == "org_1"
    assert "genome" in body
    assert "program" in body["genome"]
    assert "traits" in body["genome"]
    assert "bravery" in body["genome"]["traits"]
    assert "children" in body


def test_create_world_replaces_previous(client: TestClient) -> None:
    first = _create(client)
    second = client.post(
        "/api/worlds",
        json={"name": "kolejny", "organism_count": 2, "seed": 2},
    )
    assert second.status_code == 200
    assert second.json()["id"] == first
    assert second.json()["organism_count"] == 2


def test_feed_does_not_exist(client: TestClient) -> None:
    _create(client)
    response = client.post("/api/organisms/org_1/feed")
    assert response.status_code in {404, 405}


def test_websocket_pushes_state(client: TestClient) -> None:
    world_id = _create(client)
    with client.websocket_connect(f"/ws/worlds/{world_id}") as socket:
        first = socket.receive_json()
        assert "tick" in first
        assert "organisms" in first
        assert "apples" in first
        assert "events" in first
        assert "stats" in first
        assert first["stats"]["population"] == 3
        socket.send_text("MOVE")
        second = socket.receive_json()
        assert "tick" in second
        assert "position" in second["organisms"][0]


def test_get_restores_world_from_sqlite(client: TestClient) -> None:
    from app.engine import service

    world_id = _create(client)
    first = client.get(f"/api/worlds/{world_id}").json()
    service.world = None
    restored = client.get(f"/api/worlds/{world_id}").json()
    assert restored["id"] == world_id
    assert restored["seed"] == first["seed"]
    assert restored["tick"] >= 0
