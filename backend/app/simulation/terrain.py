from __future__ import annotations

import math

from app.simulation.constants import (
    TERRAIN_DIRT,
    TERRAIN_GRASS,
    TERRAIN_HILLS,
    TERRAIN_MEADOW,
    TILE_SIZE,
)


def _u32(n: int) -> int:
    return n & 0xFFFFFFFF


def _hash(ix: int, iy: int, seed: int) -> float:
    n = _u32(ix * 374761393 + iy * 668265263 + seed * 0x9E3779B9)
    n = _u32((n ^ (n >> 13)) * 1274126177)
    n = _u32(n ^ (n >> 16))
    return n / 4294967295.0


def _smooth(t: float) -> float:
    return t * t * (3.0 - 2.0 * t)


def value_noise(x: float, y: float, seed: int) -> float:
    x0 = math.floor(x)
    y0 = math.floor(y)
    fx = _smooth(x - x0)
    fy = _smooth(y - y0)
    v00 = _hash(x0, y0, seed)
    v10 = _hash(x0 + 1, y0, seed)
    v01 = _hash(x0, y0 + 1, seed)
    v11 = _hash(x0 + 1, y0 + 1, seed)
    v0 = v00 * (1.0 - fx) + v10 * fx
    v1 = v01 * (1.0 - fx) + v11 * fx
    return v0 * (1.0 - fy) + v1 * fy


def fbm(x: float, y: float, seed: int, octaves: int = 4) -> float:
    amplitude = 1.0
    frequency = 1.0
    total = 0.0
    norm = 0.0
    for i in range(octaves):
        total += amplitude * value_noise(x * frequency, y * frequency, seed + i * 101)
        norm += amplitude
        amplitude *= 0.5
        frequency *= 2.0
    return total / norm if norm else 0.0


def noise_to_terrain(value: float) -> str:
    if value < 0.50:
        return TERRAIN_GRASS
    if value < 0.80:
        return TERRAIN_DIRT
    if value < 0.95:
        return TERRAIN_MEADOW
    return TERRAIN_HILLS


def generate_terrain(width: int, height: int, seed: int) -> list[list[str]]:
    cols = max(1, width // TILE_SIZE)
    rows = max(1, height // TILE_SIZE)
    tiles: list[list[str]] = []
    for ty in range(rows):
        row: list[str] = []
        for tx in range(cols):
            sample = fbm(tx / 8.0, ty / 8.0, seed)
            row.append(noise_to_terrain(sample))
        tiles.append(row)
    return tiles
