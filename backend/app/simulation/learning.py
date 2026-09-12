from __future__ import annotations

from app.simulation.constants import (
    CRITICAL_ENERGY,
    FOOD_TOUCH_RANGE,
    HUNGER_DROP_MIN,
    HUNGER_DROP_SPAN,
    LEARN_BAD_DELTA,
    LEARN_DOWN,
    LEARN_UP,
    REPRODUCE_COST,
    THINK_COST,
    THINK_TICKS,
    COMFORT_ENERGY,
)
from app.simulation.organism import Organism

SKIP_THRESHOLD = -0.25
THINK_GAIN = 0.25
BODY_ACTIONS = {"MOVE", "EAT", "WAIT", "REPRODUCE", "THINK", "ACCEL"}
HUNT_ACTIONS = ("MOVE", "ACCEL")


def _clamp_score(score: float) -> float:
    return max(-1.0, min(1.0, round(score, 3)))


def _bump(organism: Organism, action: str, amount: float) -> None:
    score = organism.prediction_score.get(action, 0.0) + amount
    organism.prediction_score[action] = _clamp_score(score)


def refresh_energy_peak(organism: Organism) -> None:
    if organism.energy > organism.energy_peak:
        organism.energy_peak = organism.energy


def needs_food(organism: Organism) -> bool:
    if organism.energy <= max(CRITICAL_ENERGY * 2.0, COMFORT_ENERGY):
        return True
    peak = max(organism.energy_peak, organism.energy, 1.0)
    drop_ratio = HUNGER_DROP_MIN + HUNGER_DROP_SPAN * organism.genome.traits.hunger_threshold
    return organism.energy <= peak * (1.0 - drop_ratio)


def energy_is_ok(organism: Organism) -> bool:
    return not needs_food(organism) and organism.energy >= REPRODUCE_COST


def apply_learning(organism: Organism, delta: float) -> None:
    action = organism.last_action
    if action not in BODY_ACTIONS:
        return
    organism.last_energy_delta = delta
    score = organism.prediction_score.get(action, 0.0)
    if action == "REPRODUCE":
        organism.prediction_score[action] = _clamp_score(score + LEARN_UP)
        return
    if delta > 0:
        score += LEARN_UP
    elif delta < LEARN_BAD_DELTA:
        score -= LEARN_DOWN
    organism.prediction_score[action] = _clamp_score(score)
    if action == "EAT" and delta > 0:
        for hunt in HUNT_ACTIONS:
            _bump(organism, hunt, LEARN_UP)
        organism.hunt_streak = 0
    elif action in HUNT_ACTIONS:
        organism.hunt_streak += 1
        if organism.hunt_streak >= 50:
            _bump(organism, action, -LEARN_DOWN * 0.5)
            organism.hunt_streak = 25


def action_score(organism: Organism, action: str, rng) -> float:
    learned = organism.prediction_score.get(action, 0.0)
    weight = 0.35 + 0.65 * organism.thinking_quality
    noise = (rng.random() - 0.5) * organism.genome.traits.stupidity
    return learned * weight + noise


def should_skip(organism: Organism, action: str, rng) -> bool:
    if action in HUNT_ACTIONS and needs_food(organism):
        return False
    if action == "REPRODUCE" and energy_is_ok(organism):
        return False
    return action_score(organism, action, rng) < SKIP_THRESHOLD


def start_think(organism: Organism) -> None:
    organism.thinking_ticks_left = THINK_TICKS
    organism.is_thinking = True


def think_step(organism: Organism) -> None:
    organism.is_thinking = True
    organism.last_action = "THINK"
    organism.energy = max(0.0, organism.energy - THINK_COST)
    organism.thinking_quality = min(1.0, round(organism.thinking_quality + THINK_GAIN, 3))
    organism.thinking_ticks_left -= 1
    if organism.thinking_ticks_left <= 0:
        organism.is_thinking = False


def maybe_start_think(organism: Organism, world: object, perception) -> bool:
    if organism.energy <= CRITICAL_ENERGY:
        return False
    if needs_food(organism):
        return False
    food_nearby = bool(perception and perception.food)
    food_touching = bool(food_nearby and perception.food[0].distance <= FOOD_TOUCH_RANGE)
    if food_touching:
        return False
    if needs_food(organism) and food_nearby:
        return False
    chance = 0.08 * (1.0 - organism.genome.traits.bravery)
    if not food_nearby and organism.food_memory is None:
        chance += 0.14 * organism.genome.traits.stress
    if world.rng.random() >= chance:
        return False
    start_think(organism)
    return True
