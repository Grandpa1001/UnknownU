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
    born_at_tick: int = 0
    carrying: object | None = None
    vx: float = 0.0
    vy: float = 0.0
    speed: float = 6.0
    food_memory: dict | None = None
    planned_action: str | None = None
    hunt_streak: int = 0
    last_reproduced_tick: int | None = None
    energy_peak: float = 0.0
    other_parent_id: str | None = None

    @property
    def size(self) -> int:
        return self.genome.morphology.size_base
