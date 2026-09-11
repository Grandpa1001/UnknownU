from app.simulation.constants import (
    APPLES_PER_TREE_MAX,
    APPLES_PER_TREE_MIN,
    FEATURES,
    FLOWER_COUNT_MAX,
    FLOWER_COUNT_MIN,
    ORGANISM_ENERGY_MAX,
    ORGANISM_ENERGY_MIN,
    TERRAIN_TYPES,
    TREE_COUNT_MAX,
    TREE_COUNT_MIN,
)
from app.simulation.world import World


def _tree_snapshot(world: World) -> list[tuple[str, float, float, int]]:
    return [(tree.id, tree.x, tree.y, len(tree.apples)) for tree in world.trees]


def test_same_seed_reproduces_trees_and_terrain() -> None:
    a = World(seed=1)
    b = World(seed=1)
    assert _tree_snapshot(a) == _tree_snapshot(b)
    assert a.terrain[0][0] == b.terrain[0][0]
    assert [(o.x, o.y, o.energy, o.feature) for o in a.organisms] == [
        (o.x, o.y, o.energy, o.feature) for o in b.organisms
    ]


def test_different_seed_changes_layout() -> None:
    a = World(seed=1)
    b = World(seed=2)
    assert _tree_snapshot(a) != _tree_snapshot(b)


def test_tick_increments_age() -> None:
    world = World(seed=1, initial_organisms=3)
    for _ in range(10):
        world.tick()
    assert world.current_tick == 10
    assert all(organism.age == 10 for organism in world.organisms)


def test_spawn_counts_and_apples_on_trees() -> None:
    world = World(seed=1, initial_organisms=3)
    assert 0 < len(world.organisms) <= 3
    assert TREE_COUNT_MIN <= len(world.trees) <= TREE_COUNT_MAX
    assert FLOWER_COUNT_MIN <= len(world.flowers) <= FLOWER_COUNT_MAX
    assert world.terrain[0][0] in TERRAIN_TYPES
    assert world.apple_count == sum(len(tree.apples) for tree in world.trees)
    for tree in world.trees:
        assert APPLES_PER_TREE_MIN <= len(tree.apples) <= APPLES_PER_TREE_MAX
        for apple in tree.apples:
            assert apple.tree_id == tree.id


def test_organisms_have_inspector_fields() -> None:
    world = World(seed=1, initial_organisms=3)
    assert len(world.organisms) == 3
    for organism in world.organisms:
        assert organism.id.startswith("org_")
        assert ORGANISM_ENERGY_MIN <= organism.energy <= ORGANISM_ENERGY_MAX
        assert organism.feature in FEATURES
        assert organism.genome.program
        assert organism.genome.traits.bravery >= 0
        assert organism.parent_id is None
        assert organism.generation == 1
