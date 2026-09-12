from __future__ import annotations

from dataclasses import dataclass, field, replace
from random import Random

from app.simulation.constants import (
    DEFAULT_PROGRAM,
    ORGANISM_SIZE_MAX,
    ORGANISM_SIZE_MIN,
)


@dataclass(frozen=True)
class Traits:
    bravery: float
    stress: float
    stupidity: float
    hunger_threshold: float
    reproduction_threshold: float


@dataclass(frozen=True)
class Morphology:
    size_base: int


@dataclass(frozen=True)
class Genome:
    traits: Traits
    program: tuple[str, ...] = field(default=DEFAULT_PROGRAM)
    morphology: Morphology = field(default_factory=lambda: Morphology(size_base=8))


def _unit(rng: Random) -> float:
    return round(rng.random(), 3)


def generate_genome(rng: Random) -> Genome:
    size_base = rng.randint(ORGANISM_SIZE_MIN, ORGANISM_SIZE_MAX)
    return Genome(
        traits=Traits(
            bravery=_unit(rng),
            stress=_unit(rng),
            stupidity=_unit(rng),
            hunger_threshold=_unit(rng),
            reproduction_threshold=round(rng.uniform(0.6, 1.0), 3),
        ),
        program=DEFAULT_PROGRAM,
        morphology=Morphology(size_base=size_base),
    )


def copy_genome(genome: Genome) -> Genome:
    return Genome(
        traits=replace(genome.traits),
        program=genome.program,
        morphology=replace(genome.morphology),
    )


def crossover_genome(mother: Genome, father: Genome, rng: Random) -> Genome:
    left, right = mother.traits, father.traits
    traits = Traits(
        bravery=rng.choice((left.bravery, right.bravery)),
        stress=rng.choice((left.stress, right.stress)),
        stupidity=rng.choice((left.stupidity, right.stupidity)),
        hunger_threshold=rng.choice((left.hunger_threshold, right.hunger_threshold)),
        reproduction_threshold=rng.choice((left.reproduction_threshold, right.reproduction_threshold)),
    )
    length = min(len(mother.program), len(father.program))
    program = tuple(rng.choice((mother.program[index], father.program[index])) for index in range(length))
    size_base = rng.choice((mother.morphology.size_base, father.morphology.size_base))
    return Genome(traits=traits, program=program, morphology=Morphology(size_base=size_base))


def _clamp01(value: float) -> float:
    return round(min(1.0, max(0.0, value)), 3)


def mutate_genome(genome: Genome, rng: Random) -> tuple[Genome, str]:
    for _ in range(12):
        mutated, note = _try_mutate(genome, rng)
        if mutated != genome:
            return mutated, note
    return genome, "none"


def _try_mutate(genome: Genome, rng: Random) -> tuple[Genome, str]:
    kind = rng.choice(("trait", "program", "size"))
    if kind == "trait":
        name = rng.choice(
            ("bravery", "stress", "stupidity", "hunger_threshold", "reproduction_threshold")
        )
        old = getattr(genome.traits, name)
        delta = rng.choice((-0.1, 0.1))
        new = _clamp01(old + delta)
        if new == old:
            new = _clamp01(old + 0.1 if old < 1.0 else old - 0.1)
        traits = replace(genome.traits, **{name: new})
        return replace(genome, traits=traits), f"trait.{name} {old:.2f}→{new:.2f}"
    if kind == "size":
        old = genome.morphology.size_base
        delta = rng.choice((-1, 1))
        new = min(ORGANISM_SIZE_MAX, max(ORGANISM_SIZE_MIN, old + delta))
        if new == old:
            new = old - 1 if old == ORGANISM_SIZE_MAX else old + 1
        morph = replace(genome.morphology, size_base=new)
        return replace(genome, morphology=morph), f"size {old}→{new}"
    index = rng.randrange(len(genome.program))
    old = genome.program[index]
    candidates = [item for item in DEFAULT_PROGRAM if item != old] or list(DEFAULT_PROGRAM)
    new_instr = rng.choice(candidates)
    program = list(genome.program)
    program[index] = new_instr
    return replace(genome, program=tuple(program)), f"program[{index}] {old}→{new_instr}"
