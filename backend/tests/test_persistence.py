from app.persistence.database import connect, load_world, save_world
from app.simulation.world import World


def test_save_load_keeps_tick_and_positions(tmp_path) -> None:
    db_path = tmp_path / "world.db"
    world = World(seed=1, initial_organisms=3)
    for _ in range(20):
        world.tick()
    snapshot = [(o.id, o.x, o.y, o.energy, o.age) for o in world.organisms]
    tick = world.current_tick
    connection = connect(db_path)
    save_world(connection, world)
    connection.close()

    loaded = load_world(connect(db_path))
    assert loaded.current_tick == tick
    assert loaded.seed == 1
    assert [(o.id, o.x, o.y, o.energy, o.age) for o in loaded.organisms] == snapshot
    assert loaded.terrain[0][0] == world.terrain[0][0]


def test_resume_continues_from_saved_tick(tmp_path) -> None:
    db_path = tmp_path / "world.db"
    world = World(seed=2, initial_organisms=2)
    for _ in range(15):
        world.tick()
    saved_tick = world.current_tick
    connection = connect(db_path)
    save_world(connection, world)
    connection.close()

    resumed = load_world(connect(db_path))
    for _ in range(10):
        resumed.tick()
    assert resumed.current_tick == saved_tick + 10


def test_extinct_status_persists(tmp_path) -> None:
    db_path = tmp_path / "extinct.db"
    world = World(seed=1, initial_organisms=2, spawn_apples=False)
    for _ in range(5000):
        world.tick()
        if world.status == "extinct":
            break
    assert world.status == "extinct"
    connection = connect(db_path)
    save_world(connection, world)
    row = connection.execute("SELECT status, current_tick FROM worlds").fetchone()
    assert row["status"] == "extinct"
    assert row["current_tick"] == world.current_tick
    events = connection.execute("SELECT type, COUNT(*) AS n FROM events GROUP BY type").fetchall()
    types = {item["type"]: item["n"] for item in events}
    assert "DEATH" in types
    connection.close()
    loaded = load_world(connect(db_path))
    assert loaded.status == "extinct"
    assert loaded.organisms == []


def test_max_tick_marks_finished() -> None:
    world = World(seed=1, initial_organisms=1)
    world.max_tick = 5
    for _ in range(20):
        world.tick()
    assert world.current_tick == 5
    assert world.status == "finished"


def test_runner_without_db_still_works() -> None:
    from app.simulation.runner import run

    assert run(["--ticks", "5", "--seed", "1"]) == 0
