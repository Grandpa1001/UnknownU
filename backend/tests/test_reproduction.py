from dataclasses import replace
from random import Random

from app.simulation.actions import reproduce
from app.simulation.constants import CHILD_ENERGY, REPRODUCE_COOLDOWN, REPRODUCE_COST
from app.simulation.genome import Genome, copy_genome, mutate_genome
from app.simulation.world import World


def _satiated(organism, energy: float) -> None:
    organism.energy = energy
    organism.energy_peak = energy


def _pair(world: World, energy: float = 1100.0):
    parent = world.organisms[0]
    mate = world.organisms[1]
    parent.x, parent.y = 80.0, 80.0
    mate.x, mate.y = 90.0, 80.0
    _satiated(parent, energy)
    _satiated(mate, energy)
    parent.genome = Genome(
        traits=replace(parent.genome.traits, reproduction_threshold=0.5),
        program=parent.genome.program,
        morphology=parent.genome.morphology,
    )
    mate.genome = Genome(
        traits=parent.genome.traits,
        program=parent.genome.program,
        morphology=parent.genome.morphology,
    )
    return parent, mate


def test_reproduce_costs_energy_and_spawns_child() -> None:
    world = World(seed=1, mutation_rate=0.0)
    parent, mate = _pair(world, 1100)
    start = len(world.organisms)
    child = reproduce(parent, world)
    assert child is not None
    assert len(world.organisms) == start + 1
    assert parent.energy == 1100 - REPRODUCE_COST
    assert mate.energy == 1100 - REPRODUCE_COST
    assert child.parent_id == parent.id
    assert child.other_parent_id == mate.id
    assert child.generation == parent.generation + 1
    assert child.energy == CHILD_ENERGY
    assert child.genome == parent.genome
    assert any(event.type == "BIRTH" for event in world.events)


def test_zero_mutation_rate_copies_mixed_genome() -> None:
    world = World(seed=3, mutation_rate=0.0)
    parent, _mate = _pair(world)
    original = copy_genome(parent.genome)
    child = reproduce(parent, world)
    assert child is not None
    assert child.genome == original
    assert not any(event.type == "MUTATION" for event in world.events)


def test_always_mutate_changes_one_field() -> None:
    world = World(seed=9, mutation_rate=1.0)
    parent, _mate = _pair(world)
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
    parent, _mate = _pair(world, energy=150)
    assert reproduce(parent, world) is None
    assert len(world.organisms) == 3


def test_cannot_reproduce_alone() -> None:
    world = World(seed=1, mutation_rate=0.0, initial_organisms=1)
    parent = world.organisms[0]
    _satiated(parent, 1100)
    assert reproduce(parent, world) is None
    assert len(world.organisms) == 1


def test_cannot_reproduce_without_nearby_partner() -> None:
    world = World(seed=1, mutation_rate=0.0, width=400, height=400)
    parent, mate = _pair(world, 1100)
    mate.x, mate.y = 300.0, 300.0
    assert reproduce(parent, world) is None


def test_reproduce_waits_for_cooldown() -> None:
    world = World(seed=1, mutation_rate=0.0)
    parent, _mate = _pair(world, energy=1400)
    world.current_tick = 10
    assert reproduce(parent, world) is not None
    assert parent.energy == 1200
    assert reproduce(parent, world) is None
    world.current_tick = 10 + REPRODUCE_COOLDOWN
    assert reproduce(parent, world) is not None
    assert parent.energy == 1000
