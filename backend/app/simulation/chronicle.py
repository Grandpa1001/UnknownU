from __future__ import annotations

from collections import Counter

from app.simulation.constants import POPULATION_CAP
from app.simulation.events import Event
from app.simulation.world import World

EVENT_LABELS = {
    "EAT": "posiłki",
    "PICKUP": "zbiory",
    "SHARE": "przekazania",
    "DROP": "złożenia",
    "BIRTH": "narodziny",
    "DEATH": "zgony",
    "MUTATION": "mutacje",
    "APPLE_RESPAWN": "odrosty jabłek",
    "BERRY_RESPAWN": "odrosty jagód",
    "POPULATION_CAP": "uderzenia w limit",
}


def build_chronicle(world: World) -> dict:
    counts = Counter(event.type for event in world.events)
    event_counts = {name: int(counts.get(name, 0)) for name in EVENT_LABELS}
    peak_population, peak_tick = _peak_population(world)
    last_eat = _last(world.events, "EAT")
    last_death = _last(world.events, "DEATH")
    last_birth = _last(world.events, "BIRTH")
    units = _units(world)
    cause = _diagnose(
        world,
        eats=event_counts["EAT"],
        births=event_counts["BIRTH"],
        deaths=event_counts["DEATH"],
        cap_hits=event_counts["POPULATION_CAP"],
        respawns=event_counts["APPLE_RESPAWN"],
        peak_population=peak_population,
        last_eat_tick=last_eat.tick if last_eat else None,
        last_death_tick=last_death.tick if last_death else None,
        last_birth_tick=last_birth.tick if last_birth else None,
    )
    return {
        "status": world.status,
        "tick": world.current_tick,
        "cause": cause,
        "journal": {
            "counts": event_counts,
            "peak_population": peak_population,
            "peak_tick": peak_tick,
            "highlights": _highlights(world.events),
        },
        "units": units,
    }


def world_chronicle(world: World) -> dict:
    key = (world.current_tick, world.status, len(world.events), len(world.organisms), len(world.dead))
    cached = getattr(world, "_chronicle_cache", None)
    if cached and cached[0] == key:
        return cached[1]
    payload = build_chronicle(world)
    world._chronicle_cache = (key, payload)
    return payload


def dump_chronicle(world: World) -> str:
    report = build_chronicle(world)
    cause = report["cause"]
    journal = report["journal"]
    units = report["units"]
    lines = [
        f"kronika status={report['status']} tick={report['tick']}",
        f"przyczyna {cause['code']}: {cause['headline']}",
        cause["text"],
        (
            f"jednostki {units['ever_lived']} · założyciele {units['founders']} · "
            f"max pokolenie {units['max_generation']}"
        ),
    ]
    for kind in units["kinds"]:
        lines.append(
            f"  {kind['label']} · {kind['count']} · pokolenie {kind['max_generation']}"
        )
    counts = journal["counts"]
    lines.append(
        "dziennik "
        + " · ".join(f"{EVENT_LABELS[name]} {counts[name]}" for name in EVENT_LABELS)
    )
    lines.append(f"szczyt populacji {journal['peak_population']} (tick {journal['peak_tick']})")
    for item in journal["highlights"]:
        lines.append(f"  tick {item['tick']} · {item['text']}")
    return "\n".join(lines)


def _peak_population(world: World) -> tuple[int, int]:
    population = world.initial_organism_count
    peak = population
    peak_tick = 0
    for event in world.events:
        if event.type == "BIRTH":
            population += 1
            if population > peak:
                peak = population
                peak_tick = event.tick
        elif event.type == "DEATH":
            population -= 1
    return peak, peak_tick


def _units(world: World) -> dict:
    people = _everyone(world)
    founders = world.initial_organism_count
    by_generation: dict[int, list[dict]] = {}
    max_generation = 0
    for person in people:
        generation = person["generation"]
        by_generation.setdefault(generation, []).append(person)
        max_generation = max(max_generation, generation)
    kinds = []
    for generation in sorted(by_generation):
        members = by_generation[generation]
        longest = max(members, key=lambda item: item["age"])
        kinds.append(
            {
                "id": f"gen-{generation}",
                "label": f"pokolenie {generation}",
                "count": len(members),
                "max_generation": generation,
                "longest_lived": {"id": longest["id"], "age": longest["age"]},
            }
        )
    return {
        "ever_lived": len(people),
        "founders": founders,
        "surviving": len(world.organisms),
        "max_generation": max_generation,
        "kinds": kinds,
    }


def _everyone(world: World) -> list[dict]:
    people = []
    for organism in world.organisms:
        people.append(
            {
                "id": organism.id,
                "generation": organism.generation,
                "age": organism.age,
            }
        )
    for record in world.dead:
        people.append(
            {
                "id": record.get("id"),
                "generation": record.get("generation") or 1,
                "age": record.get("final_age") or 0,
            }
        )
    return people


def _highlights(events: list[Event]) -> list[dict]:
    items: list[dict] = []
    specs = (
        ("EAT", "pierwszy posiłek", "ostatni posiłek", "posiłek"),
        ("PICKUP", "pierwszy zbiór", "ostatni zbiór", "zbiór"),
        ("SHARE", "pierwsze przekazanie", "ostatnie przekazanie", "przekazanie"),
        ("DROP", "pierwsze złożenie", "ostatnie złożenie", "złożenie"),
        ("BIRTH", "pierwsze narodziny", "ostatnie narodziny", "narodziny"),
        ("MUTATION", "pierwsza mutacja", "ostatnia mutacja", "mutacja"),
        ("DEATH", "pierwsza śmierć", "ostatnia śmierć", "śmierć"),
        ("POPULATION_CAP", "pierwszy limit populacji", "ostatni limit populacji", "limit populacji"),
    )
    for event_type, first_label, last_label, only_label in specs:
        matching = [event for event in events if event.type == event_type]
        if not matching:
            continue
        if len(matching) == 1:
            items.append(_highlight(matching[0], only_label))
            continue
        items.append(_highlight(matching[0], first_label))
        items.append(_highlight(matching[-1], last_label))
    items.sort(key=lambda item: item["tick"])
    return items


def _highlight(event: Event, label: str) -> dict:
    who = event.organism_id or event.data.get("apple_id") or event.data.get("description")
    text = f"{label} · {who}" if who else label
    return {"tick": event.tick, "text": text}


def _last(events: list[Event], event_type: str) -> Event | None:
    for event in reversed(events):
        if event.type == event_type:
            return event
    return None


def _diagnose(
    world: World,
    *,
    eats: int,
    births: int,
    deaths: int,
    cap_hits: int,
    respawns: int,
    peak_population: int,
    last_eat_tick: int | None,
    last_death_tick: int | None,
    last_birth_tick: int | None,
) -> dict:
    surviving = len(world.organisms)
    apples = world.apple_count
    gap = None
    if last_eat_tick is not None and last_death_tick is not None:
        gap = last_death_tick - last_eat_tick

    if world.status == "running":
        return {
            "code": "ongoing",
            "headline": "bieg trwa",
            "text": "Świat jeszcze żyje. Pełna kronika pojawi się po końcu.",
        }

    if world.status == "finished":
        return {
            "code": "tick_limit",
            "headline": "koniec czasu",
            "text": (
                f"Osiągnięto limit {world.max_tick} ticków. "
                f"Żyje jeszcze {surviving} osobników. Szczyt populacji: {peak_population}."
            ),
        }

    if eats == 0 and respawns == 0 and apples == 0:
        return {
            "code": "no_food",
            "headline": "brak pożywienia",
            "text": (
                f"W świecie nie pojawiło się żadne jabłko. "
                f"{world.initial_organism_count} założycieli zużyło energię startową i wymarło."
            ),
        }

    if eats == 0:
        return {
            "code": "never_ate",
            "headline": "jedzenie nietknięte",
            "text": (
                "Pożywienie było w świecie, ale nikt nie zjadł. "
                "Organizmy nie trafiły na jabłka, zanim energia spadła do zera."
            ),
        }

    if births == 0:
        return {
            "code": "no_reproduction",
            "headline": "brak potomstwa",
            "text": (
                f"Nikt się nie rozmnożył. {world.initial_organism_count} założycieli "
                f"zjadło {eats} razy, potem energia spadła do zera."
            ),
        }

    if cap_hits and peak_population >= int(POPULATION_CAP * 0.9):
        return {
            "code": "overpopulation",
            "headline": "przepełnienie",
            "text": (
                f"Populacja dochodziła do limitu ({peak_population} osobników). "
                f"Potem zabrakło energii — {deaths} zgonów, na końcu {apples} jabłek."
            ),
        }

    if apples == 0:
        last_meal = f"tick {last_eat_tick}" if last_eat_tick is not None else "nigdy"
        last_end = f"tick {last_death_tick}" if last_death_tick is not None else f"tick {world.current_tick}"
        return {
            "code": "food_depleted",
            "headline": "jabłka się skończyły",
            "text": (
                f"Pożywienie wyschło. Ostatni posiłek: {last_meal}, ostatnia śmierć: {last_end}. "
                f"Populacja spadła ze szczytu {peak_population} do zera."
            ),
        }

    if gap is not None and gap > 150:
        return {
            "code": "lost_food",
            "headline": "nie znaleźli jedzenia",
            "text": (
                f"Na końcu zostało {apples} jabłek, ale ostatnie osobniki ich nie znalazły. "
                f"Ostatni posiłek: tick {last_eat_tick}, wymarcie: tick {last_death_tick}."
            ),
        }

    birth_note = f"ostatnie narodziny: tick {last_birth_tick}. " if last_birth_tick is not None else ""
    return {
        "code": "energy_collapse",
        "headline": "energia nie wystarczyła",
        "text": (
            f"Koszt życia przeważył nad jedzeniem. {eats} posiłków, {births} narodzin, {deaths} zgonów. "
            f"{birth_note}Szczyt {peak_population} osobników, na końcu {apples} jabłek."
        ),
    }
