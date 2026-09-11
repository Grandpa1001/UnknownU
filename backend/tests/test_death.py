from app.simulation.world import World


def test_zero_energy_removes_organism() -> None:
    world = World(seed=1, initial_organisms=1)
    organism = world.organisms[0]
    organism.energy = 0.0
    world.tick()
    assert world.organisms == []
    assert world.status == "extinct"
    assert world.events[-1].type == "DEATH"
    assert world.fertility


def test_world_goes_extinct_without_apples() -> None:
    world = World(seed=1, initial_organisms=3, spawn_apples=False)
    for _ in range(5000):
        world.tick()
        if world.status == "extinct":
            break
    assert world.status == "extinct"
    assert world.organisms == []
    assert any(event.type == "DEATH" for event in world.events)
