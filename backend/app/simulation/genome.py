from __future__ import annotations

from dataclasses import dataclass, field
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
