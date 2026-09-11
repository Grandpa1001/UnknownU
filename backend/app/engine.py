from __future__ import annotations

import random
import threading
from pathlib import Path

from app.persistence.database import connect, reset_database, save_world
from app.simulation.constants import SNAPSHOT_INTERVAL, TILE_SIZE
from app.simulation.world import World

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DB = ROOT / "data" / "unknown.db"
TICK_SECONDS = 0.1


def organism_public(organism) -> dict:
    x = round(organism.x, 2)
    y = round(organism.y, 2)
    return {
        "id": organism.id,
        "x": x,
        "y": y,
        "position": {"x": x, "y": y},
        "direction": organism.direction,
        "energy": organism.energy,
        "age": organism.age,
        "generation": organism.generation,
        "feature": organism.feature,
        "size": organism.size,
        "is_thinking": organism.is_thinking,
        "last_action": organism.last_action,
        "parent_id": organism.parent_id,
    }


class SimulationService:
    def __init__(self, db_path: Path | None = DEFAULT_DB) -> None:
        self.db_path = db_path
        self.world: World | None = None
        self.lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="unknown-tick", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def create_world(
        self,
        name: str,
        organism_count: int,
        seed: int | None,
        max_tick: int | None,
    ) -> dict:
        if seed is None:
            seed = random.randint(1, 1_000_000)
        world = World(seed=seed, initial_organisms=organism_count)
        world.name = name
        world.max_tick = max_tick
        if self.db_path is not None:
            connection = connect(self.db_path)
            reset_database(connection)
            world.db_id = None
            save_world(connection, world)
            connection.close()
        else:
            world.db_id = 1
        with self.lock:
            self.world = world
        return self.world_summary(world)

    def advance(self, ticks: int = 1) -> None:
        with self.lock:
            if self.world is None:
                return
            for _ in range(ticks):
                self.world.tick()

    def require_world(self, world_id: int) -> World:
        with self.lock:
            return self._locked_world(world_id)

    def _locked_world(self, world_id: int) -> World:
        if self.world is None or self.world.db_id != world_id:
            raise KeyError(world_id)
        return self.world

    def snapshot(self, world_id: int) -> dict:
        with self.lock:
            return self.world_payload(self._locked_world(world_id))

    def stats_for(self, world_id: int) -> dict:
        with self.lock:
            return self.stats(self._locked_world(world_id))

    def events_for(self, world_id: int, limit: int = 50) -> dict:
        with self.lock:
            world = self._locked_world(world_id)
            events = world.events[-limit:]
            return {"events": [event.format() for event in events]}

    def organism_for(self, organism_id: str) -> dict:
        with self.lock:
            if self.world is None:
                raise KeyError(organism_id)
            payload = self.organism_payload(self.world, organism_id)
            if payload is None:
                raise KeyError(organism_id)
            return payload

    def live_for(self, world_id: int) -> dict:
        with self.lock:
            return self.live_payload(self._locked_world(world_id))

    def world_payload(self, world: World, include_terrain: bool = True) -> dict:
        apples = [
            {"id": apple.id, "tree_id": apple.tree_id, "x": round(apple.x, 2), "y": round(apple.y, 2)}
            for tree in world.trees
            for apple in tree.apples
        ]
        payload = {
            "id": world.db_id,
            "name": world.name,
            "seed": world.seed,
            "tick": world.current_tick,
            "status": world.status,
            "width": world.width,
            "height": world.height,
            "tile_size": TILE_SIZE,
            "trees": [
                {"id": tree.id, "x": round(tree.x, 2), "y": round(tree.y, 2), "apples": len(tree.apples)}
                for tree in world.trees
            ],
            "apples": apples,
            "flowers": [
                {"id": flower.id, "x": round(flower.x, 2), "y": round(flower.y, 2), "variant": flower.variant}
                for flower in world.flowers
            ],
            "organisms": [organism_public(organism) for organism in world.organisms],
        }
        if include_terrain:
            payload["terrain"] = world.terrain
        return payload

    def live_payload(self, world: World) -> dict:
        return {
            "tick": world.current_tick,
            "status": world.status,
            "organisms": [organism_public(organism) for organism in world.organisms],
            "apples": [
                {"id": apple.id, "tree_id": apple.tree_id, "x": round(apple.x, 2), "y": round(apple.y, 2)}
                for tree in world.trees
                for apple in tree.apples
            ],
            "events": [event.format() for event in world.events[-8:]],
        }

    def stats(self, world: World) -> dict:
        births = sum(1 for event in world.events if event.type == "BIRTH")
        deaths = sum(1 for event in world.events if event.type == "DEATH")
        generation = max((organism.generation for organism in world.organisms), default=0)
        variants = {organism.feature for organism in world.organisms}
        return {
            "tick": world.current_tick,
            "status": world.status,
            "population": len(world.organisms),
            "generation": generation,
            "births": births,
            "deaths": deaths,
            "apples": world.apple_count,
            "variants": len(variants),
        }

    def organism_payload(self, world: World, organism_id: str) -> dict | None:
        organism = next((item for item in world.organisms if item.id == organism_id), None)
        if organism is None:
            return None
        payload = organism_public(organism)
        payload["genome"] = {
            "traits": organism.genome.traits.__dict__,
            "program": list(organism.genome.program),
            "morphology": organism.genome.morphology.__dict__,
        }
        payload["prediction_score"] = dict(organism.prediction_score)
        payload["thinking_quality"] = organism.thinking_quality
        return payload

    def world_summary(self, world: World) -> dict:
        return {
            "id": world.db_id,
            "name": world.name,
            "seed": world.seed,
            "tick": world.current_tick,
            "status": world.status,
            "organism_count": len(world.organisms),
        }

    def _loop(self) -> None:
        while not self._stop.wait(TICK_SECONDS):
            with self.lock:
                world = self.world
                if world is None or world.status != "running":
                    continue
                world.tick()
                if self.db_path is not None and world.current_tick % SNAPSHOT_INTERVAL == 0:
                    connection = connect(self.db_path)
                    save_world(connection, world)
                    connection.close()


service = SimulationService()
