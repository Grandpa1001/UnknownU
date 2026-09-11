import math

from app.simulation.actions import move, sense, torus_offset, wrap
from app.simulation.constants import MOVE_COST, SENSE_RADIUS
from app.simulation.environment import Apple, Tree
from app.simulation.genome import Genome, Morphology, Traits
from app.simulation.organism import Organism
from app.simulation.world import World


def _genome() -> Genome:
    return Genome(
        traits=Traits(
            bravery=0.5,
            stress=0.2,
            stupidity=0.1,
            hunger_threshold=0.4,
            reproduction_threshold=0.8,
        ),
        morphology=Morphology(size_base=8, feature="none", has_benefit=False),
    )


def _organism(**overrides: object) -> Organism:
    data = {
        "id": "org_test",
        "x": 100.0,
        "y": 100.0,
        "direction": 0.0,
        "energy": 500.0,
        "age": 0,
        "generation": 1,
        "genome": _genome(),
    }
    data.update(overrides)
    return Organism(**data)


def test_torus_wraps_past_right_edge() -> None:
    world = World(seed=1, width=4000, height=4000, initial_organisms=1)
    organism = _organism(x=3999.0, y=10.0, direction=0.0, energy=500.0)
    move(organism, world)
    assert organism.x < 20.0
    assert organism.energy == 500.0 - MOVE_COST


def test_torus_offset_picks_shortest_path() -> None:
    dx, dy = torus_offset(10, 10, 3990, 10, 4000, 4000)
    assert dx == -20
    assert dy == 0


def test_sense_finds_nearby_apple() -> None:
    world = World(seed=1, width=400, height=400, initial_organisms=1)
    organism = world.organisms[0]
    organism.x = 50.0
    organism.y = 50.0
    organism.energy = 500.0
    world.trees = [
        Tree(
            id="tree_1",
            x=50.0,
            y=50.0,
            apples=[Apple(id="apple_1_1", tree_id="tree_1", x=80.0, y=50.0)],
        )
    ]
    perception = sense(organism, world)
    assert perception.food
    assert perception.food[0].id == "apple_1_1"
    assert perception.food[0].distance < SENSE_RADIUS
    assert math.isclose(perception.food[0].direction, 0.0, abs_tol=0.05)


def test_sense_ignores_apple_outside_radius() -> None:
    world = World(seed=1, width=400, height=400, initial_organisms=1)
    organism = world.organisms[0]
    organism.x = 20.0
    organism.y = 20.0
    organism.energy = 500.0
    world.trees = [
        Tree(
            id="tree_1",
            x=300.0,
            y=300.0,
            apples=[Apple(id="apple_far", tree_id="tree_1", x=300.0, y=300.0)],
        )
    ]
    perception = sense(organism, world)
    assert perception.food == []


def test_organisms_move_on_their_own() -> None:
    world = World(seed=1, initial_organisms=3)
    start = [(o.id, o.x, o.y) for o in world.organisms]
    for _ in range(100):
        world.tick()
    moved = [(o.id, o.x, o.y) for o in world.organisms]
    assert moved != start
    assert any(o.last_action in {"MOVE", "TURN", "WAIT", "SENSE"} for o in world.organisms)


def test_wrap_helper() -> None:
    assert wrap(4005, 4000) == 5
    assert wrap(-1, 4000) == 3999
