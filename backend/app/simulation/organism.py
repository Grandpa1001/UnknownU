from __future__ import annotations

from dataclasses import dataclass, field

from app.simulation.genome import Genome


@dataclass
class Organism:
    id: str
    x: float
    y: float
    direction: float
    energy: float
    age: int
    generation: int
    genome: Genome
    parent_id: str | None = None
    last_action: str | None = None
    last_perception: object | None = None
    last_energy_delta: float = 0.0
    prediction_score: dict[str, float] = field(default_factory=dict)
    is_thinking: bool = False
    thinking_ticks_left: int = 0
    thinking_quality: float = 0.0

    @property
    def size(self) -> int:
        return self.genome.morphology.size_base

    @property
    def feature(self) -> str:
        return self.genome.morphology.feature
