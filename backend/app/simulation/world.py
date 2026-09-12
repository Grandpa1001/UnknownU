from __future__ import annotations

import math
from random import Random

from app.simulation.actions import apply_wind, drop_carried, execute_program, resolve_physics, torus_distance, wrap
from app.simulation.constants import (
    APPLE_RESPAWN_INTERVAL,
    APPLES_PER_TREE_MAX,
    BERRIES_PER_BUSH_MAX,
    BERRY_RESPAWN_INTERVAL,
    CHILD_ENERGY,
    DEFAULT_ORGANISM_COUNT,
    EXISTENCE_COST,
    FERTILITY_DURATION,
    FERTILITY_RADIUS,
    MUTATION_CHANCE,
    ORGANISM_ENERGY_MAX,
    ORGANISM_ENERGY_MIN,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)
from app.simulation.environment import (
    Flower,
    Tree,
    apple_count,
    berry_count,
    generate_bushes,
    generate_flowers,
    generate_trees,
    spawn_apple_on_tree,
    spawn_berry_on_bush,
)
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
        mutation_rate: float = MUTATION_CHANCE,
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
        self.bushes = generate_bushes(self.rng, width, height)
        self.flowers: list[Flower] = generate_flowers(self.rng, width, height)
        self.organisms: list[Organism] = self._spawn_organisms(initial_organisms)
        self.events: list[Event] = []
        self.fertility: list[Fertility] = []
        self._apple_seq = 0
        self._berry_seq = 0
        self._org_seq = initial_organisms
        self.mutation_rate = mutation_rate
        self.name = "world"
        self.max_tick: int | None = None
        self.initial_organism_count = initial_organisms
        self.dead: list[dict] = []
        self.db_id: int | None = None
        self.ground_apples: list = []
        self.cache_x = sum(organism.x for organism in self.organisms) / len(self.organisms)
        self.cache_y = sum(organism.y for organism in self.organisms) / len(self.organisms)
        self.cache_established = False
        if not spawn_apples:
            for tree in self.trees:
                tree.apples.clear()
            for bush in self.bushes:
                bush.berries.clear()

    @property
    def apple_count(self) -> int:
        return apple_count(self.trees) + len(self.ground_apples)

    @property
    def berry_count(self) -> int:
        return berry_count(self.bushes)

    @property
    def pillar_x(self) -> float:
        return self.width / 2.0

    @property
    def pillar_y(self) -> float:
        return self.height / 2.0

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
        apply_wind(self)
        resolve_physics(self)
        self._resolve_deaths()
        self._respawn_apples()
        self._respawn_berries()
        self._expire_fertility()
        if self.max_tick is not None and self.current_tick >= self.max_tick and self.status == "running":
            self.status = "finished"

    def _resolve_deaths(self) -> None:
        still_alive: list[Organism] = []
        for organism in self.organisms:
            if organism.energy > 0:
                still_alive.append(organism)
                continue
            if organism.carrying is not None:
                drop_carried(organism, self, at_cache=False)
            self.dead.append(
                {
                    "id": organism.id,
                    "parent_id": organism.parent_id,
                    "other_parent_id": organism.other_parent_id,
                    "born_at_tick": organism.born_at_tick,
                    "died_at_tick": self.current_tick,
                    "generation": organism.generation,
                    "genome": {
                        "traits": organism.genome.traits.__dict__,
                        "program": list(organism.genome.program),
                        "morphology": organism.genome.morphology.__dict__,
                    },
                    "final_energy": organism.energy,
                    "final_age": organism.age,
                }
            )
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

    def _respawn_berries(self) -> None:
        if BERRY_RESPAWN_INTERVAL < 1 or self.current_tick % BERRY_RESPAWN_INTERVAL != 0:
            return
        candidates = [bush for bush in self.bushes if len(bush.berries) < BERRIES_PER_BUSH_MAX]
        if not candidates:
            return
        bush = self.rng.choice(candidates)
        self._berry_seq += 1
        berry = spawn_berry_on_bush(self.rng, bush, f"berry_r{self.current_tick}_{self._berry_seq}")
        if berry:
            self.record_event("BERRY_RESPAWN", None, {"berry_id": berry.id, "bush_id": bush.id})

    def spawn_child(self, parent: Organism, genome, mate: Organism | None = None) -> Organism:
        self._org_seq += 1
        angle = self.rng.uniform(0.0, 2.0 * math.pi)
        dist = self.rng.uniform(26.0, 42.0)
        origin_x, origin_y = parent.x, parent.y
        if mate is not None:
            origin_x = (parent.x + mate.x) / 2.0
            origin_y = (parent.y + mate.y) / 2.0
        child = Organism(
            id=f"org_{self._org_seq}",
            x=wrap(origin_x + math.cos(angle) * dist, self.width),
            y=wrap(origin_y + math.sin(angle) * dist, self.height),
            direction=angle,
            energy=CHILD_ENERGY,
            energy_peak=CHILD_ENERGY,
            age=0,
            generation=max(parent.generation, mate.generation if mate is not None else parent.generation) + 1,
            genome=genome,
            parent_id=parent.id,
            other_parent_id=mate.id if mate is not None else None,
            born_at_tick=self.current_tick,
            vx=math.cos(angle) * 5.0,
            vy=math.sin(angle) * 5.0,
        )
        parent.vx -= math.cos(angle) * 2.5
        parent.vy -= math.sin(angle) * 2.5
        if mate is not None:
            mate.vx -= math.cos(angle) * 2.5
            mate.vy -= math.sin(angle) * 2.5
        self.organisms.append(child)
        return child

    def _expire_fertility(self) -> None:
        self.fertility = [zone for zone in self.fertility if zone.expires_at >= self.current_tick]

    def _spawn_organisms(self, count: int) -> list[Organism]:
        organisms: list[Organism] = []
        margin = 24.0
        landmarks = list(self.trees) + list(self.bushes)
        anchor = self.rng.choice(landmarks) if landmarks else None
        for index in range(1, count + 1):
            genome = generate_genome(self.rng)
            if anchor is not None:
                angle = self.rng.uniform(0.0, 2.0 * math.pi)
                dist = self.rng.uniform(70.0, 180.0)
                x = wrap(anchor.x + math.cos(angle) * dist, self.width)
                y = wrap(anchor.y + math.sin(angle) * dist, self.height)
            else:
                x = self.rng.uniform(margin, self.width - margin)
                y = self.rng.uniform(margin, self.height - margin)
            energy = float(self.rng.randint(ORGANISM_ENERGY_MIN, ORGANISM_ENERGY_MAX))
            organisms.append(
                Organism(
                    id=f"org_{index}",
                    x=x,
                    y=y,
                    direction=self.rng.uniform(0.0, 6.283185307179586),
                    energy=energy,
                    energy_peak=energy,
                    age=0,
                    generation=1,
                    genome=genome,
                    born_at_tick=0,
                )
            )
        return organisms
