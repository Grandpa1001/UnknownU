export const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";
export const WS_BASE = import.meta.env.VITE_WS_BASE ?? "ws://127.0.0.1:8000";

export const CANVAS_BG = 0x2a4a2a;
export const SELECT_RING = 0xf2f6ff;
export const TAG_GOLD = 0xffd700;

export const PALETTE = {
  grass: "#4a7c59",
  grassDark: "#2d5016",
  grassLight: "#6ba75a",
  dirt: "#8b6f47",
  dirtDark: "#6b4423",
  dirtLight: "#c4a57b",
  meadow: "#a4c595",
  hills: "#2d5016",
  hillsLight: "#4a7c59",
  trunk: "#6b4423",
  trunkLight: "#8b5a3c",
  foliage: "#2d5016",
  foliageMid: "#3d6b1f",
  apple: "#e63946",
  appleDark: "#b22a34",
  flowerCenter: "#ffeb3b",
  creature: "#2b5aa0",
  creatureDark: "#1e4073",
  creatureLight: "#4a7cba",
  eyeWhite: "#ffffff",
  eyeBlack: "#000000",
  spinner: "#ffd700",
  cache: "#6b4423",
  cacheRing: "#c4a57b",
  stone: "#8a8680",
  stoneDark: "#4d4a45",
  stoneLight: "#c4c0b6",
  moss: "#3d6b1f",
  berry: "#7b2d8e",
  berryLight: "#c05cd6",
};

export const FLOWER_PETALS = ["#ffb4d6", "#ffd700", "#b19cd9"];

export const CREATURE_W = 24;
export const CREATURE_H = 32;
export const TREE_SIZE = 48;
export const PILLAR_W = 36;
export const PILLAR_H = 72;
export const BUSH_W = 36;
export const BUSH_H = 28;
export const BERRY_SIZE = 6;
export const FLOWER_SIZE = 8;
export const APPLE_SIZE = 6;
export const SPINNER_SIZE = 8;
export const TILE_ART = 16;
export const DEATH_FADE_MS = 900;
export const WALK_FRAME_MS = 125;
export const SPINNER_FRAME_MS = 100;
