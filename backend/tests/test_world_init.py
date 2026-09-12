from app.simulation.constants import (
    APPLES_PER_TREE_MAX,
    APPLES_PER_TREE_MIN,
    BERRIES_PER_BUSH_MAX,
    BERRIES_PER_BUSH_MIN,
    BUSH_COUNT_MAX,
    BUSH_COUNT_MIN,
    FLOWER_COUNT_MAX,
    FLOWER_COUNT_MIN,
    ORGANISM_ENERGY_MAX,
    ORGANISM_ENERGY_MIN,
    ORGANISM_SIZE_MAX,
    ORGANISM_SIZE_MIN,
    PILLAR_CLEARING,
    TERRAIN_DIRT,
    TERRAIN_TYPES,
    TILE_SIZE,
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
    assert [(o.x, o.y, o.energy, o.size) for o in a.organisms] == [
        (o.x, o.y, o.energy, o.size) for o in b.organisms
    ]


def test_different_seed_changes_layout() -> None:
    a = World(seed=1)
    b = World(seed=2)
    assert _tree_snapshot(a) != _tree_snapshot(b)


def test_tick_increments_age() -> None:
    world = World(seed=1, initial_organisms=3)
    founders = [organism.id for organism in world.organisms]
    for _ in range(10):
        world.tick()
    assert world.current_tick == 10
    living_founders = [organism for organism in world.organisms if organism.id in founders]
    assert living_founders
    assert all(organism.age == 10 for organism in living_founders)


def test_spawn_counts_and_apples_on_trees() -> None:
    world = World(seed=1, initial_organisms=3)
    assert 0 < len(world.organisms) <= 3
    assert TREE_COUNT_MIN <= len(world.trees) <= TREE_COUNT_MAX
    assert BUSH_COUNT_MIN <= len(world.bushes) <= BUSH_COUNT_MAX
    assert FLOWER_COUNT_MIN <= len(world.flowers) <= FLOWER_COUNT_MAX
    assert world.terrain[0][0] in TERRAIN_TYPES
    assert world.apple_count == sum(len(tree.apples) for tree in world.trees)
    for tree in world.trees:
        assert APPLES_PER_TREE_MIN <= len(tree.apples) <= APPLES_PER_TREE_MAX
        for apple in tree.apples:
            assert apple.tree_id == tree.id
    for bush in world.bushes:
        assert BERRIES_PER_BUSH_MIN <= len(bush.berries) <= BERRIES_PER_BUSH_MAX
        for berry in bush.berries:
            assert berry.bush_id == bush.id


def test_organisms_have_inspector_fields() -> None:
    world = World(seed=1, initial_organisms=3)
    assert len(world.organisms) == 3
    for organism in world.organisms:
        assert organism.id.startswith("org_")
        assert ORGANISM_ENERGY_MIN <= organism.energy <= ORGANISM_ENERGY_MAX
        assert ORGANISM_SIZE_MIN <= organism.size <= ORGANISM_SIZE_MAX
        assert organism.genome.program
        assert organism.genome.traits.bravery >= 0
        assert organism.parent_id is None
        assert organism.generation == 1


def test_pillar_stands_at_map_center() -> None:
    world = World(seed=1, initial_organisms=3)
    assert world.pillar_x == world.width / 2
    assert world.pillar_y == world.height / 2
    for tree in world.trees:
        dx = tree.x - world.pillar_x
        dy = tree.y - world.pillar_y
        assert dx * dx + dy * dy >= (PILLAR_CLEARING - 1) ** 2
    mid = int((world.height / TILE_SIZE) // 2)
    assert world.terrain[mid][mid] == TERRAIN_DIRT
