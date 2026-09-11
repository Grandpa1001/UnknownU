from __future__ import annotations

from app.simulation.constants import (
    CRITICAL_ENERGY,
    FOOD_TOUCH_RANGE,
    LEARN_BAD_DELTA,
    LEARN_DOWN,
    LEARN_UP,
    THINK_COST,
    THINK_TICKS,
)
from app.simulation.organism import Organism

SKIP_THRESHOLD = -0.25
THINK_GAIN = 0.25
BODY_ACTIONS = {"MOVE", "EAT", "WAIT", "REPRODUCE", "THINK"}


def apply_learning(organism: Organism, delta: float) -> None:
    action = organism.last_action
    if action not in BODY_ACTIONS:
        return
    organism.last_energy_delta = delta
    score = organism.prediction_score.get(action, 0.0)
    if delta > 0:
        score += LEARN_UP
    elif delta < LEARN_BAD_DELTA:
        score -= LEARN_DOWN
    organism.prediction_score[action] = max(-1.0, min(1.0, round(score, 3)))


def action_score(organism: Organism, action: str, rng) -> float:
    learned = organism.prediction_score.get(action, 0.0)
    weight = 0.35 + 0.65 * organism.thinking_quality
    noise = (rng.random() - 0.5) * organism.genome.traits.stupidity
    return learned * weight + noise


def should_skip(organism: Organism, action: str, rng) -> bool:
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
    if perception and perception.food and perception.food[0].distance <= FOOD_TOUCH_RANGE:
        return False
    chance = 0.10 * (1.0 - organism.genome.traits.bravery)
    if world.rng.random() >= chance:
        return False
    start_think(organism)
    return True
