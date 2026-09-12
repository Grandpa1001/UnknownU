from __future__ import annotations

from dataclasses import asdict
from random import Random

from app.simulation.environment import Apple, Berry, Bush, Flower, Tree
from app.simulation.events import Event, Fertility
from app.simulation.genome import Genome, Morphology, Traits
from app.simulation.organism import Organism
from app.simulation.world import World


def _rng_to_dict(rng: Random) -> dict:
    version, data, gauss = rng.getstate()
    return {"version": version, "data": list(data), "gauss": gauss}


def _rng_from_dict(payload: dict) -> Random:
    rng = Random()
    rng.setstate((payload["version"], tuple(payload["data"]), payload["gauss"]))
    return rng


def genome_to_dict(genome: Genome) -> dict:
    return {
        "traits": asdict(genome.traits),
        "program": list(genome.program),
        "morphology": asdict(genome.morphology),
    }


def genome_from_dict(payload: dict) -> Genome:
    morphology = payload.get("morphology") or {}
    return Genome(
        traits=Traits(**payload["traits"]),
        program=tuple(payload["program"]),
        morphology=Morphology(size_base=int(morphology.get("size_base") or 8)),
    )


def organism_to_dict(organism: Organism) -> dict:
    return {
        "id": organism.id,
        "x": organism.x,
        "y": organism.y,
        "direction": organism.direction,
        "energy": organism.energy,
        "age": organism.age,
        "generation": organism.generation,
        "parent_id": organism.parent_id,
        "other_parent_id": organism.other_parent_id,
        "last_action": organism.last_action,
        "last_energy_delta": organism.last_energy_delta,
        "prediction_score": dict(organism.prediction_score),
        "is_thinking": organism.is_thinking,
        "thinking_ticks_left": organism.thinking_ticks_left,
        "thinking_quality": organism.thinking_quality,
        "born_at_tick": organism.born_at_tick,
        "vx": organism.vx,
        "vy": organism.vy,
        "speed": organism.speed,
        "food_memory": dict(organism.food_memory) if organism.food_memory else None,
        "planned_action": organism.planned_action,
        "hunt_streak": organism.hunt_streak,
        "last_reproduced_tick": organism.last_reproduced_tick,
        "energy_peak": organism.energy_peak,
        "genome": genome_to_dict(organism.genome),
        "carrying": None
        if organism.carrying is None
        else {"id": organism.carrying.id, "tree_id": organism.carrying.tree_id, "x": organism.carrying.x, "y": organism.carrying.y},
    }


def organism_from_dict(payload: dict) -> Organism:
    return Organism(
        id=payload["id"],
        x=payload["x"],
        y=payload["y"],
        direction=payload["direction"],
        energy=payload["energy"],
        age=payload["age"],
        generation=payload["generation"],
        genome=genome_from_dict(payload["genome"]),
        parent_id=payload.get("parent_id"),
        other_parent_id=payload.get("other_parent_id"),
        last_action=payload.get("last_action"),
        last_energy_delta=payload.get("last_energy_delta", 0.0),
        prediction_score=dict(payload.get("prediction_score") or {}),
        is_thinking=payload.get("is_thinking", False),
        thinking_ticks_left=payload.get("thinking_ticks_left", 0),
        thinking_quality=payload.get("thinking_quality", 0.0),
        born_at_tick=payload.get("born_at_tick", 0),
        vx=float(payload.get("vx") or 0.0),
        vy=float(payload.get("vy") or 0.0),
        speed=float(payload.get("speed") or 6.0),
        food_memory=dict(payload["food_memory"]) if payload.get("food_memory") else None,
        planned_action=payload.get("planned_action"),
        hunt_streak=int(payload.get("hunt_streak") or 0),
        last_reproduced_tick=payload.get("last_reproduced_tick"),
        energy_peak=float(payload.get("energy_peak") or payload.get("energy") or 0.0),
        carrying=Apple(**payload["carrying"]) if payload.get("carrying") else None,
    )


def world_to_dict(world: World) -> dict:
    return {
        "seed": world.seed,
        "name": world.name,
        "width": world.width,
        "height": world.height,
        "current_tick": world.current_tick,
        "status": world.status,
        "mutation_rate": world.mutation_rate,
        "max_tick": world.max_tick,
        "initial_organism_count": world.initial_organism_count,
        "apple_seq": world._apple_seq,
        "berry_seq": getattr(world, "_berry_seq", 0),
        "org_seq": world._org_seq,
        "rng": _rng_to_dict(world.rng),
        "terrain": world.terrain,
        "trees": [
            {
                "id": tree.id,
                "x": tree.x,
                "y": tree.y,
                "apples": [{"id": apple.id, "tree_id": apple.tree_id, "x": apple.x, "y": apple.y} for apple in tree.apples],
            }
            for tree in world.trees
        ],
        "flowers": [{"id": flower.id, "x": flower.x, "y": flower.y, "variant": flower.variant} for flower in world.flowers],
        "bushes": [
            {
                "id": bush.id,
                "x": bush.x,
                "y": bush.y,
                "berries": [
                    {"id": berry.id, "bush_id": berry.bush_id, "x": berry.x, "y": berry.y} for berry in bush.berries
                ],
            }
            for bush in getattr(world, "bushes", [])
        ],
        "organisms": [organism_to_dict(organism) for organism in world.organisms],
        "dead": list(world.dead),
        "ground_apples": [
            {"id": apple.id, "tree_id": apple.tree_id, "x": apple.x, "y": apple.y} for apple in world.ground_apples
        ],
        "cache_x": world.cache_x,
        "cache_y": world.cache_y,
        "cache_established": bool(getattr(world, "cache_established", False)),
        "events": [
            {"tick": event.tick, "type": event.type, "organism_id": event.organism_id, "data": event.data}
            for event in world.events
        ],
        "fertility": [{"x": zone.x, "y": zone.y, "expires_at": zone.expires_at} for zone in world.fertility],
    }


def world_from_dict(payload: dict) -> World:
    world = World.__new__(World)
    world.seed = payload["seed"]
    world.name = payload.get("name", "world")
    world.width = payload["width"]
    world.height = payload["height"]
    world.current_tick = payload["current_tick"]
    world.status = payload["status"]
    world.mutation_rate = payload["mutation_rate"]
    world.max_tick = payload.get("max_tick")
    world.initial_organism_count = payload.get("initial_organism_count", len(payload.get("organisms") or []))
    world._apple_seq = payload.get("apple_seq", 0)
    world._berry_seq = payload.get("berry_seq", 0)
    world._org_seq = payload.get("org_seq", 0)
    world.rng = _rng_from_dict(payload["rng"])
    world.terrain = payload["terrain"]
    world.trees = [
        Tree(
            id=tree["id"],
            x=tree["x"],
            y=tree["y"],
            apples=[Apple(**apple) for apple in tree["apples"]],
        )
        for tree in payload["trees"]
    ]
    world.flowers = [Flower(**flower) for flower in payload["flowers"]]
    world.bushes = [
        Bush(
            id=bush["id"],
            x=bush["x"],
            y=bush["y"],
            berries=[Berry(**berry) for berry in bush.get("berries") or []],
        )
        for bush in payload.get("bushes") or []
    ]
    world.organisms = [organism_from_dict(item) for item in payload["organisms"]]
    world.dead = list(payload.get("dead") or [])
    world.ground_apples = [Apple(**apple) for apple in payload.get("ground_apples") or []]
    if payload.get("cache_x") is None or payload.get("cache_y") is None:
        living = world.organisms
        world.cache_x = sum(item.x for item in living) / len(living) if living else payload["width"] / 2
        world.cache_y = sum(item.y for item in living) / len(living) if living else payload["height"] / 2
    else:
        world.cache_x = float(payload["cache_x"])
        world.cache_y = float(payload["cache_y"])
    world.cache_established = bool(payload.get("cache_established"))
    world.events = [
        Event(tick=item["tick"], type=item["type"], organism_id=item.get("organism_id"), data=item.get("data") or {})
        for item in payload.get("events") or []
    ]
    world.fertility = [Fertility(**zone) for zone in payload.get("fertility") or []]
    world.db_id = None
    return world
