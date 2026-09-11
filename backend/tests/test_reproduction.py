from dataclasses import replace
from random import Random

from app.simulation.actions import reproduce
from app.simulation.constants import CHILD_ENERGY, REPRODUCE_COST
from app.simulation.genome import Genome, copy_genome, mutate_genome
from app.simulation.world import World


def _ready(world: World, energy: float = 900.0):
    parent = world.organisms[0]
    parent.energy = energy
    parent.genome = Genome(
        traits=replace(parent.genome.traits, reproduction_threshold=0.5),
        program=parent.genome.program,
        morphology=parent.genome.morphology,
    )
    return parent


def test_reproduce_costs_energy_and_spawns_child() -> None:
    world = World(seed=1, mutation_rate=0.0)
    parent = _ready(world, 900)
    start = len(world.organisms)
    child = reproduce(parent, world)
    assert child is not None
    assert len(world.organisms) == start + 1
    assert parent.energy == 900 - REPRODUCE_COST
    assert child.parent_id == parent.id
    assert child.generation == parent.generation + 1
    assert child.energy == CHILD_ENERGY
    assert child.genome == parent.genome
    assert any(event.type == "BIRTH" for event in world.events)


def test_zero_mutation_rate_copies_genome() -> None:
    world = World(seed=3, mutation_rate=0.0)
    parent = _ready(world)
    original = copy_genome(parent.genome)
    child = reproduce(parent, world)
    assert child is not None
    assert child.genome == original
    assert not any(event.type == "MUTATION" for event in world.events)


def test_always_mutate_changes_one_field() -> None:
    world = World(seed=9, mutation_rate=1.0)
    parent = _ready(world)
    original = copy_genome(parent.genome)
    child = reproduce(parent, world)
    assert child is not None
    assert child.genome != original
    assert any(event.type == "MUTATION" for event in world.events)


def test_mutate_genome_is_single_change() -> None:
    world = World(seed=4)
    genome = world.organisms[0].genome
    mutated, note = mutate_genome(genome, Random(11))
    assert mutated != genome
    assert note != "none"
    trait_diff = mutated.traits != genome.traits
    program_diff = mutated.program != genome.program
    morph_diff = mutated.morphology != genome.morphology
    assert [trait_diff, program_diff, morph_diff].count(True) == 1


def test_cannot_reproduce_without_energy() -> None:
    world = World(seed=1, mutation_rate=0.0)
    parent = _ready(world, energy=150)
    assert reproduce(parent, world) is None
    assert len(world.organisms) == 3
