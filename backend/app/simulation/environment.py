from __future__ import annotations

from dataclasses import dataclass, field
from random import Random

from app.simulation.constants import (
    APPLES_PER_TREE_MAX,
    APPLES_PER_TREE_MIN,
    BERRIES_PER_BUSH_MAX,
    BERRIES_PER_BUSH_MIN,
    BUSH_COUNT_MAX,
    BUSH_COUNT_MIN,
    BUSH_MARGIN,
    BUSH_MIN_DISTANCE,
    FLOWER_COUNT_MAX,
    FLOWER_COUNT_MIN,
    FLOWER_MARGIN,
    FLOWER_MIN_DISTANCE,
    PILLAR_CLEARING,
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


@dataclass
class Berry:
    id: str
    bush_id: str
    x: float
    y: float


@dataclass
class Bush:
    id: str
    x: float
    y: float
    berries: list[Berry] = field(default_factory=list)


def _away_from_pillar(x: float, y: float, width: int, height: int, clearing: float) -> tuple[float, float]:
    cx = width / 2.0
    cy = height / 2.0
    dx = x - cx
    dy = y - cy
    dist = (dx * dx + dy * dy) ** 0.5
    if dist >= clearing:
        return x, y
    if dist < 0.001:
        return cx + clearing, cy
    scale = clearing / dist
    return cx + dx * scale, cy + dy * scale


def _scatter(
    rng: Random,
    count: int,
    width: int,
    height: int,
    min_dist: float,
    margin: float,
    max_attempts: int = 400,
    avoid_radius: float = 0.0,
) -> list[tuple[float, float]]:
    points: list[tuple[float, float]] = []
    min_x, max_x = margin, max(margin, width - margin)
    min_y, max_y = margin, max(margin, height - margin)
    dist_sq = min_dist * min_dist
    avoid_sq = avoid_radius * avoid_radius
    cx = width / 2.0
    cy = height / 2.0
    for _ in range(count):
        x = y = 0.0
        for _attempt in range(max_attempts):
            x = rng.uniform(min_x, max_x)
            y = rng.uniform(min_y, max_y)
            if avoid_sq and (x - cx) ** 2 + (y - cy) ** 2 < avoid_sq:
                continue
            if all((x - px) ** 2 + (y - py) ** 2 >= dist_sq for px, py in points):
                break
        x, y = _away_from_pillar(x, y, width, height, avoid_radius) if avoid_radius else (x, y)
        points.append((x, y))
    return points


def generate_trees(rng: Random, width: int = WORLD_WIDTH, height: int = WORLD_HEIGHT) -> list[Tree]:
    count = rng.randint(TREE_COUNT_MIN, TREE_COUNT_MAX)
    points = _scatter(
        rng, count, width, height, TREE_MIN_DISTANCE, TREE_MARGIN, avoid_radius=PILLAR_CLEARING
    )
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
    points = _scatter(
        rng, count, width, height, FLOWER_MIN_DISTANCE, FLOWER_MARGIN, avoid_radius=PILLAR_CLEARING * 0.7
    )
    return [
        Flower(id=f"flower_{index}", x=x, y=y, variant=rng.randint(0, 2))
        for index, (x, y) in enumerate(points, start=1)
    ]


def generate_bushes(rng: Random, width: int = WORLD_WIDTH, height: int = WORLD_HEIGHT) -> list[Bush]:
    count = rng.randint(BUSH_COUNT_MIN, BUSH_COUNT_MAX)
    points = _scatter(
        rng, count, width, height, BUSH_MIN_DISTANCE, BUSH_MARGIN, avoid_radius=PILLAR_CLEARING
    )
    bushes: list[Bush] = []
    for index, (x, y) in enumerate(points, start=1):
        bush_id = f"bush_{index}"
        berry_count = rng.randint(BERRIES_PER_BUSH_MIN, BERRIES_PER_BUSH_MAX)
        berries = [
            Berry(
                id=f"berry_{index}_{berry_n}",
                bush_id=bush_id,
                x=x + rng.uniform(-10.0, 10.0),
                y=y + rng.uniform(-8.0, 4.0),
            )
            for berry_n in range(1, berry_count + 1)
        ]
        bushes.append(Bush(id=bush_id, x=x, y=y, berries=berries))
    return bushes


def spawn_berry_on_bush(rng: Random, bush: Bush, berry_id: str) -> Berry | None:
    if len(bush.berries) >= BERRIES_PER_BUSH_MAX:
        return None
    berry = Berry(
        id=berry_id,
        bush_id=bush.id,
        x=bush.x + rng.uniform(-10.0, 10.0),
        y=bush.y + rng.uniform(-8.0, 4.0),
    )
    bush.berries.append(berry)
    return berry


def spawn_apple_on_tree(rng: Random, tree: Tree, apple_id: str) -> Apple | None:
    if len(tree.apples) >= APPLES_PER_TREE_MAX:
        return None
    apple = Apple(
        id=apple_id,
        tree_id=tree.id,
        x=tree.x + rng.uniform(-18.0, 18.0),
        y=tree.y + rng.uniform(-22.0, -4.0),
    )
    tree.apples.append(apple)
    return apple


def apple_count(trees: list[Tree]) -> int:
    return sum(len(tree.apples) for tree in trees)


def berry_count(bushes: list[Bush]) -> int:
    return sum(len(bush.berries) for bush in bushes)
