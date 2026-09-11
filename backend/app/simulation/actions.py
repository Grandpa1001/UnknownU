from __future__ import annotations

import math
from dataclasses import dataclass, field

from app.simulation.constants import (
    CRITICAL_ENERGY,
    FOOD_TOUCH_RANGE,
    MOVE_COST,
    MOVE_STEP,
    SENSE_COST,
    SENSE_RADIUS,
    TURN_COST,
    TURN_RATE,
    WAIT_COST,
)
from app.simulation.organism import Organism


@dataclass(frozen=True)
class SenseHit:
    id: str
    kind: str
    distance: float
    direction: float


@dataclass
class Perception:
    food: list[SenseHit] = field(default_factory=list)
    organisms: list[SenseHit] = field(default_factory=list)


def wrap(value: float, size: float) -> float:
    return value % size


def torus_offset(ax: float, ay: float, bx: float, by: float, width: float, height: float) -> tuple[float, float]:
    dx = bx - ax
    dy = by - ay
    half_w = width / 2.0
    half_h = height / 2.0
    if dx > half_w:
        dx -= width
    elif dx < -half_w:
        dx += width
    if dy > half_h:
        dy -= height
    elif dy < -half_h:
        dy += height
    return dx, dy


def torus_distance(ax: float, ay: float, bx: float, by: float, width: float, height: float) -> float:
    dx, dy = torus_offset(ax, ay, bx, by, width, height)
    return math.hypot(dx, dy)


def _angle(dx: float, dy: float) -> float:
    return math.atan2(dy, dx)


def _angle_delta(current: float, target: float) -> float:
    return (target - current + math.pi) % (2.0 * math.pi) - math.pi


def _pay(organism: Organism, cost: float) -> None:
    organism.energy = max(0.0, organism.energy - cost)


def _move_step(organism: Organism) -> float:
    step = MOVE_STEP
    if organism.feature == "nogi":
        step *= 1.10
    return step


def _turn_rate(organism: Organism) -> float:
    rate = TURN_RATE
    if organism.feature == "rogi":
        rate *= 1.05
    return rate


def _sense_radius(organism: Organism) -> float:
    radius = SENSE_RADIUS
    if organism.feature in {"antena", "skrzydła"}:
        radius *= 1.10
    return radius


def sense(organism: Organism, world: object) -> Perception:
    radius = _sense_radius(organism)
    food: list[SenseHit] = []
    others: list[SenseHit] = []
    width = world.width
    height = world.height

    for tree in world.trees:
        for apple in tree.apples:
            distance = torus_distance(organism.x, organism.y, apple.x, apple.y, width, height)
            if distance <= radius:
                dx, dy = torus_offset(organism.x, organism.y, apple.x, apple.y, width, height)
                food.append(SenseHit(id=apple.id, kind="apple", distance=distance, direction=_angle(dx, dy)))

    for other in world.organisms:
        if other.id == organism.id:
            continue
        distance = torus_distance(organism.x, organism.y, other.x, other.y, width, height)
        if distance <= radius:
            dx, dy = torus_offset(organism.x, organism.y, other.x, other.y, width, height)
            others.append(
                SenseHit(id=other.id, kind="organism", distance=distance, direction=_angle(dx, dy))
            )

    food.sort(key=lambda hit: hit.distance)
    others.sort(key=lambda hit: hit.distance)
    _pay(organism, SENSE_COST)
    perception = Perception(food=food, organisms=others)
    organism.last_perception = perception
    organism.last_action = "SENSE"
    return perception


def turn(organism: Organism, delta: float) -> None:
    organism.direction = wrap(organism.direction + delta, 2.0 * math.pi)
    _pay(organism, TURN_COST)
    organism.last_action = "TURN"


def turn_towards(organism: Organism, target_direction: float) -> None:
    delta = _angle_delta(organism.direction, target_direction)
    max_turn = _turn_rate(organism)
    if delta > max_turn:
        delta = max_turn
    elif delta < -max_turn:
        delta = -max_turn
    turn(organism, delta)


def move(organism: Organism, world: object) -> None:
    step = _move_step(organism)
    organism.x = wrap(organism.x + math.cos(organism.direction) * step, world.width)
    organism.y = wrap(organism.y + math.sin(organism.direction) * step, world.height)
    _pay(organism, MOVE_COST)
    organism.last_action = "MOVE"


def wait(organism: Organism) -> None:
    _pay(organism, WAIT_COST)
    organism.last_action = "WAIT"


def _energy_is_critical(organism: Organism) -> bool:
    return organism.energy <= CRITICAL_ENERGY


def _food_touching(perception: Perception | None) -> bool:
    return bool(perception and perception.food and perception.food[0].distance <= FOOD_TOUCH_RANGE)


def wander(organism: Organism, world: object) -> None:
    jitter = (world.rng.random() - 0.5) * organism.genome.traits.stupidity * 0.9
    if abs(jitter) > 0.02:
        turn(organism, jitter)
    move(organism, world)


def execute_program(organism: Organism, world: object) -> None:
    perception: Perception | None = None
    acted = False
    for instruction in organism.genome.program:
        if instruction == "SENSE":
            perception = sense(organism, world)
            continue
        if acted:
            continue
        if instruction == "IF_FOOD_NEARBY->MOVE" and perception and perception.food:
            turn_towards(organism, perception.food[0].direction)
            move(organism, world)
            acted = True
        elif instruction == "IF_FOOD_TOUCH->EAT" and _food_touching(perception):
            # Jedzenie wchodzi w M3 — na razie zostań przy jabłku.
            wait(organism)
            acted = True
        elif instruction == "IF_ENERGY_LOW->WAIT" and _energy_is_critical(organism):
            wait(organism)
            acted = True
        elif instruction == "IF_ENERGY_HIGH->REPRODUCE":
            continue
    if not acted:
        wander(organism, world)
