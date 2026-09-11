from __future__ import annotations

import argparse

from app.simulation.world import World


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="UNKNOWN headless world runner")
    parser.add_argument("--ticks", type=int, default=10)
    parser.add_argument("--seed", type=int, default=1)
    parser.add_argument("--organisms", type=int, default=3)
    parser.add_argument("--width", type=int, default=4000)
    parser.add_argument("--height", type=int, default=4000)
    parser.add_argument("--print", dest="do_print", action="store_true")
    parser.add_argument("--print-every", type=int, default=0)
    parser.add_argument("--print-events", action="store_true")
    parser.add_argument("--no-apples", action="store_true")
    parser.add_argument("--print-memory", default=None, metavar="ORG_ID")
    return parser.parse_args(argv)


def dump_world(world: World) -> str:
    lines = [
        (
            f"seed={world.seed} tick={world.current_tick} status={world.status} "
            f"organisms={len(world.organisms)} trees={len(world.trees)} "
            f"apples={world.apple_count} flowers={len(world.flowers)}"
        )
    ]
    for organism in world.organisms:
        lines.append(
            f"{organism.id} pos=({organism.x:.0f}, {organism.y:.0f}) "
            f"energy={organism.energy:.0f} feature={organism.feature} "
            f"age={organism.age} gen={organism.generation} "
            f"action={organism.last_action or '-'}"
        )
    lines.append(f"terrain[0][0]={world.terrain[0][0]}")
    return "\n".join(lines)


def dump_memory(world: World, organism_id: str) -> str:
    organism = next((item for item in world.organisms if item.id == organism_id), None)
    if organism is None:
        return f"{organism_id} not alive"
    scores = organism.prediction_score or {}
    parts = ", ".join(f"{action}={score:.2f}" for action, score in sorted(scores.items())) or "(empty)"
    return (
        f"{organism.id} thinking={organism.is_thinking} quality={organism.thinking_quality:.2f} "
        f"last_delta={organism.last_energy_delta:.1f} scores={{ {parts} }}"
    )


def run(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    world = World(
        seed=args.seed,
        width=args.width,
        height=args.height,
        initial_organisms=args.organisms,
        spawn_apples=not args.no_apples,
    )
    emit_events = args.print_events or args.print_every or args.do_print
    cursor = 0
    for _ in range(args.ticks):
        world.tick()
        if emit_events:
            for event in world.events[cursor:]:
                print(event.format())
            cursor = len(world.events)
        if args.print_every and world.current_tick % args.print_every == 0:
            print(dump_world(world))
            print("---")
        if args.print_memory and world.current_tick % 50 == 0:
            print(dump_memory(world, args.print_memory))
        if world.status != "running":
            break
    if args.do_print:
        print(dump_world(world))
    if args.print_memory:
        print(dump_memory(world, args.print_memory))
        if world.status == "extinct":
            # last known scores die with the organism; show events still ran
            print(f"(world {world.status}; memory exists only on living organisms)")
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
