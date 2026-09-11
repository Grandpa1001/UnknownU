from __future__ import annotations

from random import Random

from app.simulation.actions import execute_program
from app.simulation.constants import (
    DEFAULT_ORGANISM_COUNT,
    ORGANISM_ENERGY_MAX,
    ORGANISM_ENERGY_MIN,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from app.simulation.environment import Flower, Tree, apple_count, generate_flowers, generate_trees
from app.simulation.genome import generate_genome
from app.simulation.organism import Organism
from app.simulation.terrain import generate_terrain


class World:
    def __init__(
        self,
        seed: int,
        width: int = WORLD_WIDTH,
        height: int = WORLD_HEIGHT,
        initial_organisms: int = DEFAULT_ORGANISM_COUNT,
    ) -> None:
        if initial_organisms < 1:
            raise ValueError("initial_organisms must be >= 1")
        self.seed = seed
        self.width = width
        self.height = height
        self.current_tick = 0
        self.status = "running"
        self.rng = Random(seed)
        self.terrain = generate_terrain(width, height, seed)
        self.trees: list[Tree] = generate_trees(self.rng, width, height)
        self.flowers: list[Flower] = generate_flowers(self.rng, width, height)
        self.organisms: list[Organism] = self._spawn_organisms(initial_organisms)

    @property
    def apple_count(self) -> int:
        return apple_count(self.trees)

    def tick(self) -> None:
        self.current_tick += 1
        for organism in self.organisms:
            organism.age += 1
            execute_program(organism, self)

    def _spawn_organisms(self, count: int) -> list[Organism]:
        organisms: list[Organism] = []
        margin = 24.0
        for index in range(1, count + 1):
            genome = generate_genome(self.rng)
            organisms.append(
                Organism(
                    id=f"org_{index}",
                    x=self.rng.uniform(margin, self.width - margin),
                    y=self.rng.uniform(margin, self.height - margin),
                    direction=self.rng.uniform(0.0, 6.283185307179586),
                    energy=float(self.rng.randint(ORGANISM_ENERGY_MIN, ORGANISM_ENERGY_MAX)),
                    age=0,
                    generation=1,
                    genome=genome,
                )
            )
        return organisms
