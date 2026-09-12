from __future__ import annotations

import random
import threading
from pathlib import Path

from app.persistence.database import connect, load_world, reset_database, save_world
from app.simulation.chronicle import world_chronicle
from app.simulation.constants import SNAPSHOT_INTERVAL, TILE_SIZE, PILLAR_RADIUS
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
        "size": organism.size,
        "carrying": organism.carrying is not None,
        "is_thinking": organism.is_thinking,
        "last_action": organism.last_action,
        "speed": round(float(organism.speed), 2),
        "parent_id": organism.parent_id,
        "other_parent_id": organism.other_parent_id,
    }


def _apple_public(apple) -> dict:
    return {"id": apple.id, "tree_id": apple.tree_id, "x": round(apple.x, 2), "y": round(apple.y, 2)}


def world_apples(world: World) -> list[dict]:
    hanging = [_apple_public(apple) for tree in world.trees for apple in tree.apples]
    ground = [_apple_public(apple) for apple in world.ground_apples]
    return hanging + ground


def _berry_public(berry) -> dict:
    return {"id": berry.id, "bush_id": berry.bush_id, "x": round(berry.x, 2), "y": round(berry.y, 2)}


def world_berries(world: World) -> list[dict]:
    return [_berry_public(berry) for bush in getattr(world, "bushes", []) for berry in bush.berries]


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
        self.restore()
        self._stop.clear()
        self._thread = threading.Thread(target=self._loop, name="unknown-tick", daemon=True)
        self._thread.start()

    def restore(self) -> None:
        if self.world is not None or self.db_path is None:
            return
        path = Path(self.db_path)
        if not path.exists():
            return
        try:
            connection = connect(path)
            world = load_world(connection)
            connection.close()
        except FileNotFoundError:
            return
        with self.lock:
            if self.world is None:
                self.world = world

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
        next_id = 1
        if self.db_path is not None:
            connection = connect(self.db_path)
            row = connection.execute("SELECT COALESCE(MAX(id), 0) FROM worlds").fetchone()
            next_id = int(row[0]) + 1
            reset_database(connection)
            world.db_id = next_id
            save_world(connection, world)
            connection.close()
        else:
            previous = self.world.db_id if self.world is not None else 0
            world.db_id = int(previous or 0) + 1
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
        if self.world is None:
            self.restore()
        with self.lock:
            return self.world_payload(self._locked_world(world_id))

    def stats_for(self, world_id: int) -> dict:
        if self.world is None:
            self.restore()
        with self.lock:
            return self.stats(self._locked_world(world_id))

    def events_for(self, world_id: int, limit: int = 50) -> dict:
        if self.world is None:
            self.restore()
        with self.lock:
            world = self._locked_world(world_id)
            events = world.events[-limit:]
            return {"events": [event.format() for event in events]}

    def chronicle_for(self, world_id: int) -> dict:
        if self.world is None:
            self.restore()
        with self.lock:
            return world_chronicle(self._locked_world(world_id))

    def live_for(self, world_id: int) -> dict:
        if self.world is None:
            self.restore()
        with self.lock:
            return self.live_payload(self._locked_world(world_id))

    def organism_for(self, organism_id: str) -> dict:
        with self.lock:
            if self.world is None:
                raise KeyError(organism_id)
            payload = self.organism_payload(self.world, organism_id)
            if payload is None:
                raise KeyError(organism_id)
            return payload

    def world_payload(self, world: World, include_terrain: bool = True) -> dict:
        payload = {
            "id": world.db_id,
            "name": world.name,
            "seed": world.seed,
            "tick": world.current_tick,
            "status": world.status,
            "width": world.width,
            "height": world.height,
            "tile_size": TILE_SIZE,
            "cache": {"x": round(world.cache_x, 2), "y": round(world.cache_y, 2)},
            "pillar": {
                "x": round(world.pillar_x, 2),
                "y": round(world.pillar_y, 2),
                "radius": PILLAR_RADIUS,
            },
            "trees": [
                {"id": tree.id, "x": round(tree.x, 2), "y": round(tree.y, 2), "apples": len(tree.apples)}
                for tree in world.trees
            ],
            "apples": world_apples(world),
            "bushes": [
                {"id": bush.id, "x": round(bush.x, 2), "y": round(bush.y, 2), "berries": len(bush.berries)}
                for bush in getattr(world, "bushes", [])
            ],
            "berries": world_berries(world),
            "flowers": [
                {"id": flower.id, "x": round(flower.x, 2), "y": round(flower.y, 2), "variant": flower.variant}
                for flower in world.flowers
            ],
            "organisms": [organism_public(organism) for organism in world.organisms],
        }
        if include_terrain:
            payload["terrain"] = world.terrain
        if world.status != "running":
            payload["chronicle"] = world_chronicle(world)
        return payload

    def live_payload(self, world: World) -> dict:
        payload = {
            "tick": world.current_tick,
            "status": world.status,
            "organisms": [organism_public(organism) for organism in world.organisms],
            "apples": world_apples(world),
            "berries": world_berries(world),
            "cache": {"x": round(world.cache_x, 2), "y": round(world.cache_y, 2)},
            "events": [event.format() for event in world.events[-50:]],
            "stats": self.stats(world),
        }
        if world.status != "running":
            payload["chronicle"] = world_chronicle(world)
        return payload

    def stats(self, world: World) -> dict:
        births = sum(1 for event in world.events if event.type == "BIRTH")
        deaths = sum(1 for event in world.events if event.type == "DEATH")
        generation = max((organism.generation for organism in world.organisms), default=0)
        if world.dead:
            generation = max(generation, max((record.get("generation") or 0) for record in world.dead))
        variants = {organism.size for organism in world.organisms}
        return {
            "tick": world.current_tick,
            "status": world.status,
            "population": len(world.organisms),
            "generation": generation,
            "births": births,
            "deaths": deaths,
            "apples": world.apple_count,
            "berries": world.berry_count,
            "variants": len(variants),
        }

    def organism_payload(self, world: World, organism_id: str) -> dict | None:
        organism = next((item for item in world.organisms if item.id == organism_id), None)
        if organism is not None:
            payload = organism_public(organism)
            payload["alive"] = True
            payload["genome"] = {
                "traits": organism.genome.traits.__dict__,
                "program": list(organism.genome.program),
                "morphology": organism.genome.morphology.__dict__,
            }
            payload["prediction_score"] = dict(organism.prediction_score)
            payload["thinking_quality"] = organism.thinking_quality
            payload["speed"] = round(float(organism.speed), 2)
            payload["children"] = self._children_of(world, organism_id)
            return payload
        record = next((item for item in world.dead if item.get("id") == organism_id), None)
        if record is None:
            return None
        genome = record.get("genome") or {}
        morphology = genome.get("morphology") or {}
        return {
            "id": record["id"],
            "alive": False,
            "energy": record.get("final_energy"),
            "age": record.get("final_age"),
            "generation": record.get("generation"),
            "size": morphology.get("size_base"),
            "carrying": False,
            "parent_id": record.get("parent_id"),
            "other_parent_id": record.get("other_parent_id"),
            "died_at_tick": record.get("died_at_tick"),
            "born_at_tick": record.get("born_at_tick"),
            "genome": genome,
            "prediction_score": {},
            "children": self._children_of(world, organism_id),
            "is_thinking": False,
            "last_action": None,
        }

    def _children_of(self, world: World, organism_id: str) -> list[str]:
        living = [
            item.id
            for item in world.organisms
            if item.parent_id == organism_id or item.other_parent_id == organism_id
        ]
        dead = [
            item["id"]
            for item in world.dead
            if item.get("parent_id") == organism_id or item.get("other_parent_id") == organism_id
        ]
        return living + dead

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
                ended = world.status != "running"
                if self.db_path is not None and (ended or world.current_tick % SNAPSHOT_INTERVAL == 0):
                    connection = connect(self.db_path)
                    save_world(connection, world)
                    connection.close()


service = SimulationService()
