from __future__ import annotations

from dataclasses import dataclass, field, replace
from random import Random

from app.simulation.constants import (
    DEFAULT_PROGRAM,
    FEATURES,
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
    feature: str
    has_benefit: bool


@dataclass(frozen=True)
class Genome:
    traits: Traits
    program: tuple[str, ...] = field(default=DEFAULT_PROGRAM)
    morphology: Morphology = field(
        default_factory=lambda: Morphology(size_base=8, feature="none", has_benefit=False)
    )


def _unit(rng: Random) -> float:
    return round(rng.random(), 3)


def generate_genome(rng: Random) -> Genome:
    feature = rng.choice(FEATURES)
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
        morphology=Morphology(
            size_base=size_base,
            feature=feature,
            has_benefit=feature != "none",
        ),
    )


def copy_genome(genome: Genome) -> Genome:
    return Genome(
        traits=replace(genome.traits),
        program=genome.program,
        morphology=replace(genome.morphology),
    )


def _clamp01(value: float) -> float:
    return round(min(1.0, max(0.0, value)), 3)


def mutate_genome(genome: Genome, rng: Random) -> tuple[Genome, str]:
    for _ in range(12):
        mutated, note = _try_mutate(genome, rng)
        if mutated != genome:
            return mutated, note
    return genome, "none"


def _try_mutate(genome: Genome, rng: Random) -> tuple[Genome, str]:
    kind = rng.choice(("trait", "program", "size", "feature"))
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
    if kind == "feature":
        options = [item for item in FEATURES if item != genome.morphology.feature]
        new_feature = rng.choice(options)
        morph = replace(
            genome.morphology,
            feature=new_feature,
            has_benefit=new_feature != "none",
        )
        return replace(genome, morphology=morph), f"feature {genome.morphology.feature}→{new_feature}"
    index = rng.randrange(len(genome.program))
    old = genome.program[index]
    candidates = [item for item in DEFAULT_PROGRAM if item != old] or list(DEFAULT_PROGRAM)
    new_instr = rng.choice(candidates)
    program = list(genome.program)
    program[index] = new_instr
    return replace(genome, program=tuple(program)), f"program[{index}] {old}→{new_instr}"
