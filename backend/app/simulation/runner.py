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
    return parser.parse_args(argv)


def dump_world(world: World) -> str:
    lines = [
        (
            f"seed={world.seed} tick={world.current_tick} "
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


def run(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    world = World(
        seed=args.seed,
        width=args.width,
        height=args.height,
        initial_organisms=args.organisms,
    )
    for _ in range(args.ticks):
        world.tick()
        if args.print_every and world.current_tick % args.print_every == 0:
            print(dump_world(world))
            print("---")
    if args.do_print:
        print(dump_world(world))
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
