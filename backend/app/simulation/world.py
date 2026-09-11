from __future__ import annotations

import math
from random import Random

from app.simulation.actions import execute_program, torus_distance, wrap
from app.simulation.constants import (
    APPLE_RESPAWN_INTERVAL,
    APPLES_PER_TREE_MAX,
    DEFAULT_ORGANISM_COUNT,
    EXISTENCE_COST,
    FERTILITY_DURATION,
    FERTILITY_RADIUS,
    ORGANISM_ENERGY_MAX,
    ORGANISM_ENERGY_MIN,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from app.simulation.environment import Flower, Tree, apple_count, generate_flowers, generate_trees, spawn_apple_on_tree
from app.simulation.events import Event, Fertility
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
        spawn_apples: bool = True,
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
        self.events: list[Event] = []
        self.fertility: list[Fertility] = []
        self._apple_seq = 0
        if not spawn_apples:
            for tree in self.trees:
                tree.apples.clear()

    @property
    def apple_count(self) -> int:
        return apple_count(self.trees)

    def record_event(self, event_type: str, organism_id: str | None = None, data: dict | None = None) -> Event:
        event = Event(
            tick=self.current_tick,
            type=event_type,
            organism_id=organism_id,
            data=data or {},
        )
        self.events.append(event)
        return event

    def tick(self) -> None:
        if self.status != "running":
            return
        self.current_tick += 1
        for organism in list(self.organisms):
            organism.age += 1
            organism.energy = max(0.0, organism.energy - EXISTENCE_COST)
            if organism.energy <= 0:
                continue
            execute_program(organism, self)
        self._resolve_deaths()
        self._respawn_apples()
        self._expire_fertility()

    def _resolve_deaths(self) -> None:
        still_alive: list[Organism] = []
        for organism in self.organisms:
            if organism.energy > 0:
                still_alive.append(organism)
                continue
            self.fertility.append(
                Fertility(x=organism.x, y=organism.y, expires_at=self.current_tick + FERTILITY_DURATION)
            )
            self.record_event("DEATH", organism.id, {"age": organism.age, "x": organism.x, "y": organism.y})
        self.organisms = still_alive
        if not self.organisms:
            self.status = "extinct"

    def _fertile_trees(self) -> list[Tree]:
        active = [zone for zone in self.fertility if zone.expires_at >= self.current_tick]
        if not active:
            return []
        fertile: list[Tree] = []
        for tree in self.trees:
            if any(
                torus_distance(tree.x, tree.y, zone.x, zone.y, self.width, self.height) <= FERTILITY_RADIUS
                for zone in active
            ):
                fertile.append(tree)
        return fertile

    def _respawn_apples(self) -> None:
        fertile = self._fertile_trees()
        interval = APPLE_RESPAWN_INTERVAL // 2 if fertile else APPLE_RESPAWN_INTERVAL
        if interval < 1 or self.current_tick % interval != 0:
            return
        self._spawn_apple(fertile or self.trees)
        if fertile:
            self._spawn_apple(self.trees)

    def _spawn_apple(self, trees: list[Tree]) -> None:
        candidates = [tree for tree in trees if len(tree.apples) < APPLES_PER_TREE_MAX]
        if not candidates:
            return
        tree = self.rng.choice(candidates)
        self._apple_seq += 1
        apple = spawn_apple_on_tree(self.rng, tree, f"apple_r{self.current_tick}_{self._apple_seq}")
        if apple:
            self.record_event("APPLE_RESPAWN", None, {"apple_id": apple.id, "tree_id": tree.id})

    def _expire_fertility(self) -> None:
        self.fertility = [zone for zone in self.fertility if zone.expires_at >= self.current_tick]

    def _spawn_organisms(self, count: int) -> list[Organism]:
        organisms: list[Organism] = []
        margin = 24.0
        for index in range(1, count + 1):
            genome = generate_genome(self.rng)
            if self.trees:
                tree = self.rng.choice(self.trees)
                angle = self.rng.uniform(0.0, 2.0 * math.pi)
                dist = self.rng.uniform(24.0, 80.0)
                x = wrap(tree.x + math.cos(angle) * dist, self.width)
                y = wrap(tree.y + math.sin(angle) * dist, self.height)
            else:
                x = self.rng.uniform(margin, self.width - margin)
                y = self.rng.uniform(margin, self.height - margin)
            organisms.append(
                Organism(
                    id=f"org_{index}",
                    x=x,
                    y=y,
                    direction=self.rng.uniform(0.0, 6.283185307179586),
                    energy=float(self.rng.randint(ORGANISM_ENERGY_MIN, ORGANISM_ENERGY_MAX)),
                    age=0,
                    generation=1,
                    genome=genome,
                )
            )
        return organisms
