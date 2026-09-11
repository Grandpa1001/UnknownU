from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.persistence.serializer import genome_to_dict, world_from_dict, world_to_dict
from app.simulation.world import World

SCHEMA = """
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS worlds (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    current_tick INTEGER DEFAULT 0,
    seed INTEGER,
    status TEXT DEFAULT 'running',
    initial_organism_count INTEGER,
    max_tick INTEGER,
    snapshot_json TEXT
);

CREATE TABLE IF NOT EXISTS organisms (
    id TEXT PRIMARY KEY,
    world_id INTEGER NOT NULL,
    parent_id TEXT,
    born_at_tick INTEGER,
    died_at_tick INTEGER,
    generation INTEGER,
    genome TEXT,
    final_energy REAL,
    final_age INTEGER,
    FOREIGN KEY (world_id) REFERENCES worlds(id)
);

CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY,
    world_id INTEGER NOT NULL,
    tick INTEGER,
    type TEXT,
    organism_id TEXT,
    data TEXT,
    FOREIGN KEY (world_id) REFERENCES worlds(id)
);

CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY,
    world_id INTEGER NOT NULL,
    tick INTEGER,
    full_state_json TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (world_id) REFERENCES worlds(id)
);
"""


def reset_database(connection: sqlite3.Connection) -> None:
    connection.execute("DELETE FROM organisms")
    connection.execute("DELETE FROM events")
    connection.execute("DELETE FROM snapshots")
    connection.execute("DELETE FROM worlds")
    connection.commit()


def connect(path: str | Path) -> sqlite3.Connection:
    db_path = Path(path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(db_path)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA journal_mode=WAL")
    connection.executescript(SCHEMA)
    return connection


def save_world(connection: sqlite3.Connection, world: World) -> int:
    snapshot = json.dumps(world_to_dict(world))
    if world.db_id is None:
        cursor = connection.execute(
            """
            INSERT INTO worlds (name, current_tick, seed, status, initial_organism_count, max_tick, snapshot_json)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                world.name,
                world.current_tick,
                world.seed,
                world.status,
                world.initial_organism_count,
                world.max_tick,
                snapshot,
            ),
        )
        world.db_id = int(cursor.lastrowid)
    else:
        connection.execute(
            """
            UPDATE worlds
            SET current_tick = ?, status = ?, snapshot_json = ?, max_tick = ?
            WHERE id = ?
            """,
            (world.current_tick, world.status, snapshot, world.max_tick, world.db_id),
        )
    connection.execute("DELETE FROM events WHERE world_id = ?", (world.db_id,))
    connection.executemany(
        """
        INSERT INTO events (world_id, tick, type, organism_id, data)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (world.db_id, event.tick, event.type, event.organism_id, json.dumps(event.data))
            for event in world.events
        ],
    )
    connection.execute("DELETE FROM organisms WHERE world_id = ?", (world.db_id,))
    living = [
        (
            organism.id,
            world.db_id,
            organism.parent_id,
            organism.born_at_tick,
            None,
            organism.generation,
            json.dumps(genome_to_dict(organism.genome)),
            organism.energy,
            organism.age,
        )
        for organism in world.organisms
    ]
    dead = [
        (
            record["id"],
            world.db_id,
            record.get("parent_id"),
            record.get("born_at_tick"),
            record.get("died_at_tick"),
            record.get("generation"),
            json.dumps(record.get("genome")),
            record.get("final_energy"),
            record.get("final_age"),
        )
        for record in world.dead
    ]
    connection.executemany(
        """
        INSERT INTO organisms (id, world_id, parent_id, born_at_tick, died_at_tick, generation, genome, final_energy, final_age)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        living + dead,
    )
    connection.execute(
        "INSERT INTO snapshots (world_id, tick, full_state_json) VALUES (?, ?, ?)",
        (world.db_id, world.current_tick, snapshot),
    )
    connection.commit()
    return world.db_id


def load_world(connection: sqlite3.Connection, world_id: int | None = None) -> World:
    if world_id is None:
        row = connection.execute("SELECT id, snapshot_json FROM worlds ORDER BY id DESC LIMIT 1").fetchone()
    else:
        row = connection.execute("SELECT id, snapshot_json FROM worlds WHERE id = ?", (world_id,)).fetchone()
    if row is None:
        raise FileNotFoundError("no world snapshot in database")
    world = world_from_dict(json.loads(row["snapshot_json"]))
    world.db_id = int(row["id"])
    return world
