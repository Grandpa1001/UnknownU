from app.simulation.actions import apply_wind, body_radius, collide_pillar, drop_carried, eat, resolve_physics, share_food, torus_distance
from app.simulation.constants import EAT_ENERGY, PILLAR_RADIUS, WELL_FED_ENERGY
from app.simulation.environment import Apple, Tree
from app.simulation.world import World


def _tree_with_apple(x: float, y: float, apple_id: str = "apple_1") -> Tree:
    return Tree(
        id="tree_1",
        x=x,
        y=y,
        apples=[Apple(id=apple_id, tree_id="tree_1", x=x, y=y)],
    )


def test_well_fed_reproduces_instead_of_picking_up() -> None:
    from app.simulation.actions import execute_program
    from app.simulation.genome import Genome
    from dataclasses import replace

    world = World(seed=1, width=400, height=400, initial_organisms=2, mutation_rate=0.0)
    organism, mate = world.organisms
    organism.x, organism.y = 50.0, 50.0
    mate.x, mate.y = 58.0, 50.0
    organism.direction = 0.0
    organism.energy = mate.energy = WELL_FED_ENERGY + 50
    organism.energy_peak = mate.energy_peak = WELL_FED_ENERGY + 50
    organism.genome = Genome(
        traits=replace(organism.genome.traits, bravery=1.0, stupidity=0.0),
        program=organism.genome.program,
        morphology=organism.genome.morphology,
    )
    mate.genome = organism.genome
    world.trees = [_tree_with_apple(50.0, 50.0)]
    world.bushes = []
    world.ground_apples = []
    start_pop = len(world.organisms)
    execute_program(organism, world)
    assert organism.last_action == "REPRODUCE"
    assert organism.carrying is None
    assert len(world.organisms) == start_pop + 1
    assert len(world.trees[0].apples) == 1


def test_hungry_still_eats() -> None:
    world = World(seed=1, width=400, height=400, initial_organisms=1)
    organism = world.organisms[0]
    organism.x = 50.0
    organism.y = 50.0
    organism.energy = 400.0
    world.trees = [_tree_with_apple(50.0, 50.0)]
    world.bushes = []
    assert eat(organism, world) is True
    assert organism.carrying is None
    assert organism.energy == 400.0 + EAT_ENERGY
    assert organism.last_action == "EAT"


def test_share_feeds_hungry_neighbor() -> None:
    world = World(seed=1, width=400, height=400, initial_organisms=2)
    carrier, hungry = world.organisms
    carrier.x, carrier.y = 40.0, 40.0
    hungry.x, hungry.y = 42.0, 40.0
    carrier.energy = WELL_FED_ENERGY + 10
    hungry.energy = 300.0
    carrier.carrying = Apple(id="apple_share", tree_id="tree_1", x=40.0, y=40.0)
    assert share_food(carrier, hungry, world) is True
    assert carrier.carrying is None
    assert hungry.energy == 300.0 + EAT_ENERGY
    assert world.events[-1].type == "SHARE"


def test_drop_builds_ground_cache() -> None:
    world = World(seed=1, width=400, height=400, initial_organisms=1)
    organism = world.organisms[0]
    organism.x, organism.y = world.cache_x, world.cache_y
    organism.carrying = Apple(id="apple_drop", tree_id="tree_1", x=organism.x, y=organism.y)
    assert drop_carried(organism, world, at_cache=True) is True
    assert organism.carrying is None
    assert len(world.ground_apples) == 1
    assert world.ground_apples[0].tree_id == "cache"
    assert world.apple_count == sum(len(tree.apples) for tree in world.trees) + 1


def test_hungry_eats_from_cache() -> None:
    world = World(seed=1, width=400, height=400, initial_organisms=1)
    organism = world.organisms[0]
    organism.x, organism.y = 80.0, 80.0
    organism.energy = 400.0
    world.trees = []
    world.bushes = []
    world.ground_apples = [Apple(id="apple_cache", tree_id="cache", x=80.0, y=80.0)]
    assert eat(organism, world) is True
    assert organism.energy == 400.0 + EAT_ENERGY
    assert world.ground_apples == []


def test_collision_pushes_overlapping_bodies_apart() -> None:
    world = World(seed=1, width=400, height=400, initial_organisms=2)
    left, right = world.organisms
    left.x, left.y = 100.0, 100.0
    right.x, right.y = 101.0, 100.0
    resolve_physics(world)
    distance = torus_distance(left.x, left.y, right.x, right.y, world.width, world.height)
    assert distance >= body_radius(left) + body_radius(right) - 0.05


def test_collision_bounces_heading_and_velocity() -> None:
    import math

    from app.simulation.genome import Genome, Morphology, Traits

    world = World(seed=1, width=400, height=400, initial_organisms=2)
    left, right = world.organisms
    traits = Traits(
        bravery=0.5,
        stress=0.2,
        stupidity=0.1,
        hunger_threshold=0.4,
        reproduction_threshold=0.8,
    )
    left.genome = Genome(traits=traits, morphology=Morphology(size_base=8), program=left.genome.program)
    right.genome = Genome(traits=traits, morphology=Morphology(size_base=8), program=right.genome.program)
    left.x, left.y = 100.0, 100.0
    right.x, right.y = 108.0, 100.0
    left.direction = 0.0
    right.direction = math.pi
    left.vx, left.vy = 6.0, 0.0
    right.vx, right.vy = -6.0, 0.0
    left.speed = right.speed = 6.0
    resolve_physics(world)
    distance = torus_distance(left.x, left.y, right.x, right.y, world.width, world.height)
    assert distance >= body_radius(left) + body_radius(right) - 0.05
    assert math.cos(left.direction) < 0
    assert math.cos(right.direction) > 0
    assert left.vx < 0
    assert right.vx > 0


def test_carrier_keeps_apple_until_cache_or_share() -> None:
    world = World(seed=1, width=400, height=400, initial_organisms=1)
    organism = world.organisms[0]
    organism.x, organism.y = 10.0, 10.0
    world.cache_x, world.cache_y = 300.0, 300.0
    organism.energy = WELL_FED_ENERGY - 20
    organism.carrying = Apple(id="apple_keep", tree_id="tree_1", x=10.0, y=10.0)
    from app.simulation.actions import execute_program

    execute_program(organism, world)
    assert organism.carrying is not None
    assert organism.last_action == "MOVE"


def test_death_drops_carried_apple() -> None:
    world = World(seed=1, width=400, height=400, initial_organisms=1)
    organism = world.organisms[0]
    organism.carrying = Apple(id="apple_dead", tree_id="tree_1", x=organism.x, y=organism.y)
    organism.energy = 0
    world.tick()
    assert world.status == "extinct"
    assert any(apple.id == "apple_dead" for apple in world.ground_apples)
    assert any(event.type == "DROP" for event in world.events)


def test_pillar_pushes_organism_out() -> None:
    world = World(seed=1, width=4000, height=4000, initial_organisms=1)
    organism = world.organisms[0]
    organism.x = world.pillar_x
    organism.y = world.pillar_y
    collide_pillar(organism, world)
    distance = torus_distance(
        organism.x, organism.y, world.pillar_x, world.pillar_y, world.width, world.height
    )
    assert distance >= PILLAR_RADIUS + body_radius(organism) - 0.05


def test_wind_sweeps_around_the_pillar() -> None:
    world = World(seed=1, width=4000, height=4000, initial_organisms=1, spawn_apples=False)
    organism = world.organisms[0]
    organism.x = world.pillar_x + 80.0
    organism.y = world.pillar_y
    organism.energy = 500.0
    apply_wind(world)
    assert organism.y > world.pillar_y
    assert organism.x >= world.pillar_x + 80.0


def test_wind_does_not_reach_far_corners() -> None:
    world = World(seed=1, width=400, height=400, initial_organisms=1)
    organism = world.organisms[0]
    organism.x = 8.0
    organism.y = 8.0
    start = (organism.x, organism.y)
    apply_wind(world)
    assert (organism.x, organism.y) == start
