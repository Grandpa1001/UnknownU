from app.simulation.actions import eat
from app.simulation.constants import EAT_ENERGY
from app.simulation.environment import Apple, Tree
from app.simulation.world import World


def test_eat_gives_energy_and_removes_apple() -> None:
    world = World(seed=1, width=400, height=400, initial_organisms=1)
    organism = world.organisms[0]
    organism.x = 50.0
    organism.y = 50.0
    organism.energy = 400.0
    world.trees = [
        Tree(
            id="tree_1",
            x=50.0,
            y=50.0,
            apples=[Apple(id="apple_1_1", tree_id="tree_1", x=50.0, y=50.0)],
        )
    ]
    assert eat(organism, world) is True
    assert organism.energy == 400.0 + EAT_ENERGY
    assert world.trees[0].apples == []
    assert organism.last_action == "EAT"
    assert world.events[-1].type == "EAT"


def test_eat_requires_being_near_tree_apple() -> None:
    world = World(seed=1, width=400, height=400, initial_organisms=1)
    organism = world.organisms[0]
    organism.x = 10.0
    organism.y = 10.0
    organism.energy = 400.0
    world.trees = [
        Tree(
            id="tree_1",
            x=300.0,
            y=300.0,
            apples=[Apple(id="apple_far", tree_id="tree_1", x=300.0, y=300.0)],
        )
    ]
    assert eat(organism, world) is False
    assert organism.energy == 400.0
    assert len(world.trees[0].apples) == 1


def test_apples_can_respawn() -> None:
    world = World(seed=1, width=400, height=400, initial_organisms=1)
    for tree in world.trees:
        tree.apples.clear()
    world.current_tick = 200
    world._respawn_apples()
    assert world.apple_count == 1
    assert world.events[-1].type == "APPLE_RESPAWN"
