from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from app.simulation.constants import (
    APPLES_PER_TREE_MAX,
    APPLES_PER_TREE_MIN,
    FLOWER_COUNT_MAX,
    FLOWER_COUNT_MIN,
    FLOWER_MARGIN,
    FLOWER_MIN_DISTANCE,
    TREE_COUNT_MAX,
    TREE_COUNT_MIN,
    TREE_MARGIN,
    TREE_MIN_DISTANCE,
    WORLD_HEIGHT,
    WORLD_WIDTH,
)


@dataclass
class Apple:
    id: str
    tree_id: str
    x: float
    y: float


@dataclass
class Tree:
    id: str
    x: float
    y: float
    apples: list[Apple] = field(default_factory=list)


@dataclass
class Flower:
    id: str
    x: float
    y: float
    variant: int


def _scatter(
    rng: Random,
    count: int,
    width: int,
    height: int,
    min_dist: float,
    margin: float,
    max_attempts: int = 400,
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    min_x, max_x = margin, max(margin, width - margin)
    min_y, max_y = margin, max(margin, height - margin)
    dist_sq = min_dist * min_dist
    for _ in range(count):
        x = y = 0.0
        for _attempt in range(max_attempts):
            x = rng.uniform(min_x, max_x)
            y = rng.uniform(min_y, max_y)
            if all((x - px) ** 2 + (y - py) ** 2 >= dist_sq for px, py in points):
                break
        points.append((x, y))
    return points


def generate_trees(rng: Random, width: int = WORLD_WIDTH, height: int = WORLD_HEIGHT) -> list[Tree]:
    count = rng.randint(TREE_COUNT_MIN, TREE_COUNT_MAX)
    points = _scatter(rng, count, width, height, TREE_MIN_DISTANCE, TREE_MARGIN)
    trees: list[Tree] = []
    for index, (x, y) in enumerate(points, start=1):
        tree_id = f"tree_{index}"
        apple_count = rng.randint(APPLES_PER_TREE_MIN, APPLES_PER_TREE_MAX)
        apples = [
            Apple(
                id=f"apple_{index}_{apple_n}",
                tree_id=tree_id,
                x=x + rng.uniform(-18.0, 18.0),
                y=y + rng.uniform(-22.0, -4.0),
            )
            for apple_n in range(1, apple_count + 1)
        ]
        trees.append(Tree(id=tree_id, x=x, y=y, apples=apples))
    return trees


def generate_flowers(rng: Random, width: int = WORLD_WIDTH, height: int = WORLD_HEIGHT) -> list[Flower]:
    count = rng.randint(FLOWER_COUNT_MIN, FLOWER_COUNT_MAX)
    points = _scatter(rng, count, width, height, FLOWER_MIN_DISTANCE, FLOWER_MARGIN)
    return [
        Flower(id=f"flower_{index}", x=x, y=y, variant=rng.randint(0, 2))
        for index, (x, y) in enumerate(points, start=1)
    ]


def apple_count(trees: list[Tree]) -> int:
    return sum(len(tree.apples) for tree in trees)
