from app.simulation.chronicle import build_chronicle
from app.simulation.world import World


def test_chronicle_no_food_extinction() -> None:
    world = World(seed=1, initial_organisms=3, spawn_apples=False)
    for organism in world.organisms:
        organism.energy = 0
    world.tick()
    report = build_chronicle(world)
    assert report["status"] == "extinct"
    assert report["cause"]["code"] == "no_food"
    assert "jabłko" in report["cause"]["text"]
    assert report["units"]["ever_lived"] == 3
    assert report["units"]["surviving"] == 0
    assert report["units"]["founders"] == 3
    assert report["journal"]["counts"]["DEATH"] == 3
    assert report["journal"]["counts"]["EAT"] == 0
    assert report["journal"]["peak_population"] == 3
    assert any(item["text"].startswith("śmierć") or "śmierć" in item["text"] for item in report["journal"]["highlights"])


def test_chronicle_never_ate_when_apples_exist() -> None:
    world = World(seed=1, initial_organisms=1)
    world.organisms[0].energy = 0
    world.tick()
    report = build_chronicle(world)
    assert report["status"] == "extinct"
    assert report["cause"]["code"] == "never_ate"
    assert report["units"]["kinds"]


def test_chronicle_tick_limit_keeps_survivors() -> None:
    world = World(seed=1, initial_organisms=2, spawn_apples=False)
    for organism in world.organisms:
        organism.energy = 400
    world.max_tick = 2
    world.tick()
    world.tick()
    report = build_chronicle(world)
    assert report["status"] == "finished"
    assert report["cause"]["code"] == "tick_limit"
    assert report["units"]["surviving"] == 2
    assert report["units"]["ever_lived"] == 2


def test_chronicle_counts_generations_from_living_and_dead() -> None:
    world = World(seed=1, initial_organisms=2, spawn_apples=False)
    first, second = world.organisms
    first.energy = 0
    second.energy = 400
    world.tick()
    report = build_chronicle(world)
    kinds = {item["id"]: item["count"] for item in report["units"]["kinds"]}
    assert kinds["gen-1"] == 2
    assert report["units"]["ever_lived"] == 2
    assert report["units"]["surviving"] == 1
