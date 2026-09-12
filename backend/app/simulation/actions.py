from __future__ import annotations

import math
from dataclasses import dataclass, field

from app.simulation.constants import (
    ACCEL_AMOUNT,
    APPLE_WIND_SCALE,
    BERRY_ENERGY,
    BODY_RADIUS_SCALE,
    BOUNCE_IMPULSE,
    BOUNCE_RESTITUTION,
    CACHE_DROP_RANGE,
    CRITICAL_ENERGY,
    EAT_ENERGY,
    ENERGY_MAX,
    FOOD_MEMORY_TICKS,
    FOOD_TOUCH_RANGE,
    MATE_RANGE,
    MAX_SPEED,
    MOVE_COST,
    MOVE_STEP,
    PILLAR_RADIUS,
    POPULATION_CAP,
    REPRODUCE_COOLDOWN,
    REPRODUCE_COST,
    SENSE_COST,
    SENSE_RADIUS,
    SHARE_TOUCH_RANGE,
    SPEED_DECAY,
    TURN_COST,
    TURN_RATE,
    WAIT_COST,
    WIND_COST_FACTOR,
    WIND_RADIUS_RATIO,
    WIND_STRENGTH,
)
from app.simulation.organism import Organism
from app.simulation.genome import crossover_genome, mutate_genome
from app.simulation.learning import (
    apply_learning,
    energy_is_ok,
    maybe_start_think,
    needs_food,
    refresh_energy_peak,
    should_skip,
    start_think,
    think_step,
)


@dataclass(frozen=True)
class SenseHit:
    id: str
    kind: str
    distance: float
    direction: float
    x: float = 0.0
    y: float = 0.0


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


def body_radius(organism: Organism) -> float:
    return float(organism.size) * BODY_RADIUS_SCALE


def is_hungry(organism: Organism) -> bool:
    return needs_food(organism)


def _decay_speed(organism: Organism) -> None:
    if organism.last_action == "ACCEL":
        return
    organism.speed = MOVE_STEP + (organism.speed - MOVE_STEP) * SPEED_DECAY
    if abs(organism.speed - MOVE_STEP) < 0.15:
        organism.speed = MOVE_STEP
    organism.vx *= SPEED_DECAY
    organism.vy *= SPEED_DECAY


def _remember_food(organism: Organism, world: object, perception: Perception) -> None:
    if perception.food:
        hit = _best_food(perception)
        organism.food_memory = {
            "id": hit.id,
            "x": hit.x,
            "y": hit.y,
            "tick": world.current_tick,
        }
        return
    memory = organism.food_memory
    if memory and world.current_tick - memory.get("tick", 0) > FOOD_MEMORY_TICKS:
        organism.food_memory = None


def _best_food(perception: Perception) -> SenseHit:
    foods = perception.food
    if len(foods) == 1:
        return foods[0]

    def score(hit: SenseHit) -> float:
        cluster = 0
        for other in foods:
            if other.id == hit.id:
                continue
            if abs(other.distance - hit.distance) < 55 and abs(_angle_delta(other.direction, hit.direction)) < 0.9:
                cluster += 1
        return hit.distance - cluster * 14.0

    return min(foods, key=score)


def _memory_hit(organism: Organism, world: object) -> SenseHit | None:
    memory = organism.food_memory
    if not memory:
        return None
    if world.current_tick - memory.get("tick", 0) > FOOD_MEMORY_TICKS:
        organism.food_memory = None
        return None
    dx, dy = torus_offset(organism.x, organism.y, memory["x"], memory["y"], world.width, world.height)
    distance = math.hypot(dx, dy)
    if distance < 10.0:
        organism.food_memory = None
        return None
    return SenseHit(
        id=memory["id"],
        kind="memory",
        distance=distance,
        direction=_angle(dx, dy),
        x=memory["x"],
        y=memory["y"],
    )


def _hunt_target(organism: Organism, perception: Perception | None, world: object) -> SenseHit | None:
    if perception and perception.food:
        return _best_food(perception)
    return _memory_hit(organism, world)


def sense(organism: Organism, world: object) -> Perception:
    radius = SENSE_RADIUS
    food: list[SenseHit] = []
    others: list[SenseHit] = []
    width = world.width
    height = world.height

    for tree in world.trees:
        for apple in tree.apples:
            distance = torus_distance(organism.x, organism.y, apple.x, apple.y, width, height)
            if distance <= radius:
                dx, dy = torus_offset(organism.x, organism.y, apple.x, apple.y, width, height)
                food.append(
                    SenseHit(
                        id=apple.id,
                        kind="apple",
                        distance=distance,
                        direction=_angle(dx, dy),
                        x=apple.x,
                        y=apple.y,
                    )
                )

    for apple in world.ground_apples:
        distance = torus_distance(organism.x, organism.y, apple.x, apple.y, width, height)
        if distance <= radius:
            dx, dy = torus_offset(organism.x, organism.y, apple.x, apple.y, width, height)
            food.append(
                SenseHit(
                    id=apple.id,
                    kind="cache",
                    distance=distance,
                    direction=_angle(dx, dy),
                    x=apple.x,
                    y=apple.y,
                )
                )

    for bush in getattr(world, "bushes", []):
        for berry in bush.berries:
            distance = torus_distance(organism.x, organism.y, berry.x, berry.y, width, height)
            if distance <= radius:
                dx, dy = torus_offset(organism.x, organism.y, berry.x, berry.y, width, height)
                food.append(
                    SenseHit(
                        id=berry.id,
                        kind="berry",
                        distance=distance,
                        direction=_angle(dx, dy),
                        x=berry.x,
                        y=berry.y,
                    )
                )

    for other in world.organisms:
        if other.id == organism.id:
            continue
        distance = torus_distance(organism.x, organism.y, other.x, other.y, width, height)
        if distance <= radius:
            dx, dy = torus_offset(organism.x, organism.y, other.x, other.y, width, height)
            others.append(
                SenseHit(
                    id=other.id,
                    kind="organism",
                    distance=distance,
                    direction=_angle(dx, dy),
                    x=other.x,
                    y=other.y,
                )
            )

    food.sort(key=lambda hit: hit.distance)
    others.sort(key=lambda hit: hit.distance)
    _pay(organism, SENSE_COST)
    perception = Perception(food=food, organisms=others)
    organism.last_perception = perception
    organism.last_action = "SENSE"
    _remember_food(organism, world, perception)
    return perception


def turn(organism: Organism, delta: float) -> None:
    organism.direction = wrap(organism.direction + delta, 2.0 * math.pi)
    _pay(organism, TURN_COST)
    organism.last_action = "TURN"


def turn_towards(organism: Organism, target_direction: float) -> None:
    delta = _angle_delta(organism.direction, target_direction)
    max_turn = TURN_RATE
    if delta > max_turn:
        delta = max_turn
    elif delta < -max_turn:
        delta = -max_turn
    turn(organism, delta)


def accelerate(organism: Organism) -> None:
    organism.speed = min(MAX_SPEED, organism.speed + ACCEL_AMOUNT)
    organism.last_action = "ACCEL"


def pillar_position(world: object) -> tuple[float, float]:
    return world.width / 2.0, world.height / 2.0


def wind_radius(world: object) -> float:
    return WIND_RADIUS_RATIO * min(float(world.width), float(world.height))


def wind_vector(world: object, x: float, y: float) -> tuple[float, float]:
    px, py = pillar_position(world)
    dx, dy = torus_offset(px, py, x, y, world.width, world.height)
    distance = math.hypot(dx, dy)
    radius = wind_radius(world)
    if distance < 0.5 or distance >= radius:
        return 0.0, 0.0
    falloff = (1.0 - distance / radius) ** 2
    inv = 1.0 / distance
    tx = -dy * inv
    ty = dx * inv
    radial = 0.22
    strength = WIND_STRENGTH * falloff
    return (tx + radial * dx * inv) * strength, (ty + radial * dy * inv) * strength


def move(organism: Organism, world: object) -> None:
    speed = max(MOVE_STEP * 0.5, min(MAX_SPEED, organism.speed))
    organism.vx = math.cos(organism.direction) * speed
    organism.vy = math.sin(organism.direction) * speed
    organism.x = wrap(organism.x + organism.vx, world.width)
    organism.y = wrap(organism.y + organism.vy, world.height)
    cost = MOVE_COST * (speed / MOVE_STEP)
    wx, wy = wind_vector(world, organism.x, organism.y)
    wind_speed = math.hypot(wx, wy)
    if wind_speed > 0.05:
        alignment = (organism.vx * wx + organism.vy * wy) / (speed * wind_speed)
        intensity = min(1.0, wind_speed / WIND_STRENGTH)
        cost *= 1.0 - alignment * WIND_COST_FACTOR * intensity
    _pay(organism, cost)
    if organism.last_action != "ACCEL":
        organism.last_action = "MOVE"


def apply_wind(world: object) -> None:
    for organism in world.organisms:
        if organism.energy <= 0:
            continue
        wx, wy = wind_vector(world, organism.x, organism.y)
        if wx == 0.0 and wy == 0.0:
            continue
        organism.x = wrap(organism.x + wx, world.width)
        organism.y = wrap(organism.y + wy, world.height)
        organism.vx += wx * 0.35
        organism.vy += wy * 0.35
    for apple in world.ground_apples:
        wx, wy = wind_vector(world, apple.x, apple.y)
        if wx == 0.0 and wy == 0.0:
            continue
        apple.x = wrap(apple.x + wx * APPLE_WIND_SCALE, world.width)
        apple.y = wrap(apple.y + wy * APPLE_WIND_SCALE, world.height)


def collide_pillar(organism: Organism, world: object) -> None:
    px, py = pillar_position(world)
    dx, dy = torus_offset(px, py, organism.x, organism.y, world.width, world.height)
    distance = math.hypot(dx, dy)
    minimum = PILLAR_RADIUS + body_radius(organism)
    if distance >= minimum:
        return
    if distance < 0.001:
        organism.x = wrap(px + minimum, world.width)
        organism.y = py
        organism.vx = abs(organism.vx) + BOUNCE_IMPULSE
        organism.vy = 0.0
        organism.direction = 0.0
        return
    nx = dx / distance
    ny = dy / distance
    push = minimum - distance
    organism.x = wrap(organism.x + nx * push, world.width)
    organism.y = wrap(organism.y + ny * push, world.height)
    vx, vy = _velocity_or_heading(organism)
    normal = vx * nx + vy * ny
    if normal < 0.0:
        organism.vx = vx - (1.0 + BOUNCE_RESTITUTION) * normal * nx
        organism.vy = vy - (1.0 + BOUNCE_RESTITUTION) * normal * ny
        bounced = math.hypot(organism.vx, organism.vy)
        if bounced > 0.05:
            organism.direction = math.atan2(organism.vy, organism.vx)
            step = min(bounced, BOUNCE_IMPULSE)
            organism.x = wrap(organism.x + (organism.vx / bounced) * step, world.width)
            organism.y = wrap(organism.y + (organism.vy / bounced) * step, world.height)


def _wants_accel(organism: Organism, world: object, distance: float) -> bool:
    if distance <= FOOD_TOUCH_RANGE * 1.4:
        return False
    if organism.energy <= CRITICAL_ENERGY * 1.6:
        return False
    if organism.speed >= MAX_SPEED - 0.05:
        return False
    if should_skip(organism, "ACCEL", world.rng):
        return False
    hunger = 1.0 - organism.energy / ENERGY_MAX
    drive = hunger * (0.45 + 0.55 * organism.genome.traits.hunger_threshold)
    drive += organism.genome.traits.bravery * 0.25
    return drive >= 0.22 or needs_food(organism)


def _chase(organism: Organism, world: object, target: SenseHit) -> None:
    turn_towards(organism, target.direction)
    boosted = False
    if _wants_accel(organism, world, target.distance):
        accelerate(organism)
        boosted = True
    move(organism, world)
    if boosted:
        organism.last_action = "ACCEL"


def wait(organism: Organism) -> None:
    _pay(organism, WAIT_COST)
    organism.last_action = "WAIT"


def _nearest_touching_food(organism: Organism, world: object):
    nearest = None
    source = None
    kind = None
    nearest_distance = FOOD_TOUCH_RANGE
    for tree in world.trees:
        for apple in tree.apples:
            distance = torus_distance(organism.x, organism.y, apple.x, apple.y, world.width, world.height)
            if distance <= nearest_distance:
                nearest = apple
                source = tree
                kind = "apple"
                nearest_distance = distance
    for apple in world.ground_apples:
        distance = torus_distance(organism.x, organism.y, apple.x, apple.y, world.width, world.height)
        if distance <= nearest_distance:
            nearest = apple
            source = None
            kind = "cache"
            nearest_distance = distance
    for bush in getattr(world, "bushes", []):
        for berry in bush.berries:
            distance = torus_distance(organism.x, organism.y, berry.x, berry.y, world.width, world.height)
            if distance <= nearest_distance:
                nearest = berry
                source = bush
                kind = "berry"
                nearest_distance = distance
    return nearest, source, kind


def _consume_food(organism: Organism, world: object, food, source, kind: str) -> bool:
    before = organism.energy
    gain = BERRY_ENERGY if kind == "berry" else EAT_ENERGY
    if kind == "berry":
        source.berries.remove(food)
        source_id = source.id
        food_key = "berry_id"
    elif source is None:
        world.ground_apples.remove(food)
        source_id = "cache"
        food_key = "apple_id"
    else:
        source.apples.remove(food)
        source_id = source.id
        food_key = "apple_id"
    organism.energy = min(ENERGY_MAX, organism.energy + gain)
    refresh_energy_peak(organism)
    organism.last_action = "EAT"
    if organism.food_memory and organism.food_memory.get("id") == food.id:
        organism.food_memory = None
    world.record_event(
        "EAT",
        organism.id,
        {food_key: food.id, "tree_id": source_id, "energy_before": before, "energy_after": organism.energy},
    )
    return True


def pickup(organism: Organism, world: object, apple, tree) -> bool:
    if organism.carrying is not None or tree is None:
        return False
    tree.apples.remove(apple)
    organism.carrying = apple
    organism.last_action = "PICKUP"
    world.record_event("PICKUP", organism.id, {"apple_id": apple.id, "tree_id": tree.id})
    return True


def eat(organism: Organism, world: object) -> bool:
    food, source, kind = _nearest_touching_food(organism, world)
    if food is None or not needs_food(organism) or can_reproduce(organism, world):
        return False
    return _consume_food(organism, world, food, source, kind or "apple")


def drop_carried(organism: Organism, world: object, at_cache: bool = True) -> bool:
    apple = organism.carrying
    if apple is None:
        return False
    organism.carrying = None
    if at_cache and getattr(world, "cache_established", False):
        apple.x = wrap(world.cache_x + world.rng.uniform(-10.0, 10.0), world.width)
        apple.y = wrap(world.cache_y + world.rng.uniform(-10.0, 10.0), world.height)
    else:
        apple.x = organism.x
        apple.y = organism.y
        world.cache_x = apple.x
        world.cache_y = apple.y
    apple.tree_id = "cache"
    world.ground_apples.append(apple)
    world.cache_established = True
    organism.last_action = "DROP"
    world.record_event("DROP", organism.id, {"apple_id": apple.id, "x": round(apple.x, 2), "y": round(apple.y, 2)})
    return True


def share_food(carrier: Organism, recipient: Organism, world: object) -> bool:
    apple = carrier.carrying
    if apple is None or not is_hungry(recipient):
        return False
    carrier.carrying = None
    before = recipient.energy
    recipient.energy = min(ENERGY_MAX, recipient.energy + EAT_ENERGY)
    refresh_energy_peak(recipient)
    carrier.last_action = "SHARE"
    world.record_event(
        "SHARE",
        carrier.id,
        {
            "apple_id": apple.id,
            "recipient_id": recipient.id,
            "energy_before": before,
            "energy_after": recipient.energy,
        },
    )
    return True


def _nearest_hungry(organism: Organism, world: object, reach: float) -> Organism | None:
    nearest = None
    nearest_distance = reach
    for other in world.organisms:
        if other.id == organism.id or not is_hungry(other):
            continue
        distance = torus_distance(organism.x, organism.y, other.x, other.y, world.width, world.height)
        if distance <= nearest_distance:
            nearest = other
            nearest_distance = distance
    return nearest


def _move_towards(organism: Organism, world: object, x: float, y: float) -> None:
    dx, dy = torus_offset(organism.x, organism.y, x, y, world.width, world.height)
    turn_towards(organism, _angle(dx, dy))
    move(organism, world)


def _nearest_other(organism: Organism, world: object) -> Organism | None:
    nearest = None
    nearest_distance = None
    for other in world.organisms:
        if other.id == organism.id:
            continue
        distance = torus_distance(organism.x, organism.y, other.x, other.y, world.width, world.height)
        if nearest_distance is None or distance < nearest_distance:
            nearest = other
            nearest_distance = distance
    return nearest


def _act_carrying(organism: Organism, world: object) -> bool:
    if organism.carrying is None:
        return False
    if can_reproduce(organism, world):
        return False
    if organism.energy <= CRITICAL_ENERGY:
        apple = organism.carrying
        organism.carrying = None
        before = organism.energy
        organism.energy = min(ENERGY_MAX, organism.energy + EAT_ENERGY)
        refresh_energy_peak(organism)
        organism.last_action = "EAT"
        world.record_event(
            "EAT",
            organism.id,
            {
                "apple_id": apple.id,
                "tree_id": "carried",
                "energy_before": before,
                "energy_after": organism.energy,
            },
        )
        return True
    hungry = _nearest_hungry(organism, world, SHARE_TOUCH_RANGE)
    if hungry is not None:
        share_food(organism, hungry, world)
        return True
    established = getattr(world, "cache_established", False)
    if established:
        cache_distance = torus_distance(organism.x, organism.y, world.cache_x, world.cache_y, world.width, world.height)
        if cache_distance <= CACHE_DROP_RANGE:
            drop_carried(organism, world, at_cache=True)
            return True
        _move_towards(organism, world, world.cache_x, world.cache_y)
        return True
    neighbor = _nearest_other(organism, world)
    if neighbor is not None:
        distance = torus_distance(organism.x, organism.y, neighbor.x, neighbor.y, world.width, world.height)
        if distance <= CACHE_DROP_RANGE:
            drop_carried(organism, world, at_cache=False)
            return True
        _move_towards(organism, world, neighbor.x, neighbor.y)
        return True
    wander(organism, world)
    return True


def _velocity_or_heading(organism: Organism) -> tuple[float, float]:
    speed = math.hypot(organism.vx, organism.vy)
    if speed >= 0.25:
        return organism.vx, organism.vy
    heading_speed = max(organism.speed, MOVE_STEP)
    return math.cos(organism.direction) * heading_speed, math.sin(organism.direction) * heading_speed


def _apply_bounce(left: Organism, right: Organism, nx: float, ny: float, world: object) -> None:
    lvx, lvy = _velocity_or_heading(left)
    rvx, rvy = _velocity_or_heading(right)
    mass_left = float(left.size)
    mass_right = float(right.size)
    mass_sum = mass_left + mass_right
    v1n = lvx * nx + lvy * ny
    v2n = rvx * nx + rvy * ny
    approaching = v1n - v2n
    if approaching > 0.05:
        restitution = BOUNCE_RESTITUTION
        new_v1n = (v1n * (mass_left - restitution * mass_right) + v2n * mass_right * (1.0 + restitution)) / mass_sum
        new_v2n = (v2n * (mass_right - restitution * mass_left) + v1n * mass_left * (1.0 + restitution)) / mass_sum
    else:
        impulse = BOUNCE_IMPULSE
        new_v1n = -impulse * mass_right / mass_sum
        new_v2n = impulse * mass_left / mass_sum
    left.vx = lvx + (new_v1n - v1n) * nx
    left.vy = lvy + (new_v1n - v1n) * ny
    right.vx = rvx + (new_v2n - v2n) * nx
    right.vy = rvy + (new_v2n - v2n) * ny
    left_speed = math.hypot(left.vx, left.vy)
    right_speed = math.hypot(right.vx, right.vy)
    if left_speed > 0.05:
        left.direction = math.atan2(left.vy, left.vx)
        step = min(left_speed, BOUNCE_IMPULSE)
        left.x = wrap(left.x + (left.vx / left_speed) * step, world.width)
        left.y = wrap(left.y + (left.vy / left_speed) * step, world.height)
    if right_speed > 0.05:
        right.direction = math.atan2(right.vy, right.vx)
        step = min(right_speed, BOUNCE_IMPULSE)
        right.x = wrap(right.x + (right.vx / right_speed) * step, world.width)
        right.y = wrap(right.y + (right.vy / right_speed) * step, world.height)


def resolve_physics(world: object) -> None:
    organisms = world.organisms
    count = len(organisms)
    for i in range(count):
        left = organisms[i]
        for j in range(i + 1, count):
            right = organisms[j]
            dx, dy = torus_offset(left.x, left.y, right.x, right.y, world.width, world.height)
            distance = math.hypot(dx, dy)
            minimum = body_radius(left) + body_radius(right)
            if distance < 0.001:
                nudge = world.rng.uniform(0.0, 2.0 * math.pi)
                left.x = wrap(left.x + math.cos(nudge), world.width)
                left.y = wrap(left.y + math.sin(nudge), world.height)
                continue
            if distance < minimum:
                push = (minimum - distance) / 2.0
                nx = dx / distance
                ny = dy / distance
                left.x = wrap(left.x - nx * push, world.width)
                left.y = wrap(left.y - ny * push, world.height)
                right.x = wrap(right.x + nx * push, world.width)
                right.y = wrap(right.y + ny * push, world.height)
                _apply_bounce(left, right, nx, ny, world)
            if distance <= SHARE_TOUCH_RANGE:
                if left.carrying is not None:
                    share_food(left, right, world)
                if right.carrying is not None:
                    share_food(right, left, world)
    for organism in organisms:
        collide_pillar(organism, world)


def _ready_to_mate(organism: Organism, world: object | None = None) -> bool:
    if not energy_is_ok(organism):
        return False
    last = organism.last_reproduced_tick
    tick = getattr(world, "current_tick", None) if world is not None else None
    if last is not None and tick is not None and tick - last < REPRODUCE_COOLDOWN:
        return False
    return True


def nearest_mate(organism: Organism, world: object, reach: float) -> Organism | None:
    nearest = None
    nearest_distance = reach
    for other in world.organisms:
        if other.id == organism.id or not _ready_to_mate(other, world):
            continue
        distance = torus_distance(organism.x, organism.y, other.x, other.y, world.width, world.height)
        if distance <= nearest_distance:
            nearest = other
            nearest_distance = distance
    return nearest


def _mate_target(organism: Organism, perception: Perception | None, world: object) -> SenseHit | None:
    if not _ready_to_mate(organism, world):
        return None
    if perception is None:
        return None
    for hit in perception.organisms:
        other = next((item for item in world.organisms if item.id == hit.id), None)
        if other is not None and _ready_to_mate(other, world):
            return hit
    return None


def can_reproduce(organism: Organism, world: object | None = None) -> bool:
    if world is None or not _ready_to_mate(organism, world):
        return False
    return nearest_mate(organism, world, MATE_RANGE) is not None


def reproduce(organism: Organism, world: object) -> object | None:
    if not can_reproduce(organism, world):
        return None
    mate = nearest_mate(organism, world, MATE_RANGE)
    if mate is None:
        return None
    if len(world.organisms) >= POPULATION_CAP:
        world.record_event("POPULATION_CAP", organism.id, {"population": len(world.organisms)})
        wait(organism)
        return None
    organism.energy -= REPRODUCE_COST
    mate.energy -= REPRODUCE_COST
    genome = crossover_genome(organism.genome, mate.genome, world.rng)
    mutation_note = None
    if world.rng.random() < world.mutation_rate:
        genome, mutation_note = mutate_genome(genome, world.rng)
        if mutation_note == "none":
            mutation_note = None
    child = world.spawn_child(organism, genome, mate)
    organism.last_action = "REPRODUCE"
    mate.last_action = "REPRODUCE"
    organism.last_reproduced_tick = world.current_tick
    mate.last_reproduced_tick = world.current_tick
    world.record_event(
        "BIRTH",
        child.id,
        {
            "parent_id": organism.id,
            "mate_id": mate.id,
            "generation": child.generation,
            "mutation": mutation_note,
        },
    )
    if mutation_note:
        world.record_event(
            "MUTATION",
            child.id,
            {"description": mutation_note, "parent_id": organism.id, "mate_id": mate.id},
        )
    return child


def _energy_is_critical(organism: Organism) -> bool:
    return organism.energy <= CRITICAL_ENERGY


def _food_touching(perception: Perception | None) -> bool:
    return bool(perception and perception.food and perception.food[0].distance <= FOOD_TOUCH_RANGE)


def wander(organism: Organism, world: object) -> None:
    jitter = (world.rng.random() - 0.5) * organism.genome.traits.stupidity * 0.9
    if abs(jitter) > 0.02:
        turn(organism, jitter)
    move(organism, world)


def forage(organism: Organism, world: object) -> None:
    memory = _memory_hit(organism, world)
    if memory is not None:
        _chase(organism, world, memory)
        return
    sign = 1.0 if sum(ord(char) for char in organism.id) % 2 == 0 else -1.0
    sweep = 0.09 + 0.07 * (1.0 - organism.genome.traits.stupidity)
    turn(organism, sign * sweep)
    move(organism, world)


def _decide_after_think(organism: Organism, world: object) -> None:
    perception = organism.last_perception if isinstance(organism.last_perception, Perception) else None
    if needs_food(organism):
        if _food_touching(perception):
            organism.planned_action = "EAT"
            return
        if _hunt_target(organism, perception, world) is not None:
            organism.planned_action = "HUNT"
            return
        organism.planned_action = "SEARCH"
        return
    if can_reproduce(organism, world):
        organism.planned_action = "REPRODUCE"
        return
    if _mate_target(organism, perception, world) is not None:
        organism.planned_action = "MATE"
        return
    organism.planned_action = "WANDER"


def _execute_plan(organism: Organism, world: object) -> bool:
    plan = organism.planned_action
    organism.planned_action = None
    if plan == "EAT":
        if eat(organism, world):
            return True
        target = _hunt_target(organism, organism.last_perception, world)
        if target is not None:
            _chase(organism, world, target)
            return True
        forage(organism, world)
        return True
    if plan == "HUNT":
        target = _hunt_target(organism, organism.last_perception, world)
        if target is not None:
            _chase(organism, world, target)
            return True
        forage(organism, world)
        return True
    if plan == "REPRODUCE":
        if reproduce(organism, world) is not None:
            return True
        target = _mate_target(organism, organism.last_perception, world)
        if target is not None:
            _chase(organism, world, target)
            return True
        wander(organism, world)
        return True
    if plan == "MATE":
        target = _mate_target(organism, organism.last_perception, world)
        if target is not None:
            _chase(organism, world, target)
            return True
        wander(organism, world)
        return True
    if plan == "SEARCH":
        forage(organism, world)
        return True
    if plan == "WANDER":
        wander(organism, world)
        return True
    return False


def execute_program(organism: Organism, world: object) -> None:
    refresh_energy_peak(organism)
    if organism.thinking_ticks_left > 0:
        before = organism.energy
        think_step(organism)
        apply_learning(organism, organism.energy - before)
        if organism.thinking_ticks_left > 0:
            return
        _decide_after_think(organism, world)
        body_energy_start = organism.energy
        if _execute_plan(organism, world):
            apply_learning(organism, organism.energy - body_energy_start)
        return

    _decay_speed(organism)
    perception: Perception | None = None
    acted = False
    body_energy_start = organism.energy
    rng = world.rng

    if _act_carrying(organism, world):
        apply_learning(organism, organism.energy - body_energy_start)
        return

    for instruction in organism.genome.program:
        if instruction == "SENSE":
            perception = sense(organism, world)
            body_energy_start = organism.energy
            if maybe_start_think(organism, world, perception):
                think_step(organism)
                apply_learning(organism, organism.energy - body_energy_start)
                return
            continue
        if acted:
            continue
        if instruction == "IF_FOOD_TOUCH->EAT" and needs_food(organism) and _food_touching(perception) and not can_reproduce(organism, world):
            eat(organism, world)
            acted = True
        elif instruction == "IF_ENERGY_HIGH->REPRODUCE" and _ready_to_mate(organism, world):
            if can_reproduce(organism, world) and not should_skip(organism, "REPRODUCE", rng):
                reproduce(organism, world)
                acted = True
            else:
                target = _mate_target(organism, perception, world)
                if target is not None and not should_skip(organism, "MOVE", rng):
                    _chase(organism, world, target)
                    acted = True
        elif instruction == "IF_FOOD_NEARBY->MOVE" and needs_food(organism) and not should_skip(organism, "MOVE", rng):
            target = _hunt_target(organism, perception, world)
            if target is not None:
                _chase(organism, world, target)
                acted = True
        elif instruction == "IF_ENERGY_LOW->WAIT" and _energy_is_critical(organism):
            wait(organism)
            acted = True
        elif instruction == "THINK":
            start_think(organism)
            think_step(organism)
            acted = True
    if not acted:
        if needs_food(organism):
            memory = _memory_hit(organism, world)
            if memory is not None and not should_skip(organism, "MOVE", rng):
                _chase(organism, world, memory)
            elif should_skip(organism, "MOVE", rng):
                wait(organism)
            else:
                forage(organism, world)
        else:
            target = _mate_target(organism, perception, world)
            if target is not None:
                _chase(organism, world, target)
            else:
                wander(organism, world)
    apply_learning(organism, organism.energy - body_energy_start)
