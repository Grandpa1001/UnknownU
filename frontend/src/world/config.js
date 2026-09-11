export const API_BASE = import.meta.env.VITE_API_BASE ?? "http://127.0.0.1:8000";
export const WS_BASE = import.meta.env.VITE_WS_BASE ?? "ws://127.0.0.1:8000";

export const TERRAIN_COLORS = {
  grass: [74, 124, 89, 255],
  dirt: [139, 111, 71, 255],
  meadow: [164, 197, 149, 255],
  hills: [45, 80, 22, 255],
};

export const FLOWER_COLORS = [0xffb4d6, 0xffd700, 0xb19cd9, 0xff69b4, 0xffeb3b];
export const FOLIAGE = 0x2d5016;
export const TRUNK = 0x6b4423;
export const APPLE = 0xe63946;
export const CREATURE = 0x2b5aa0;
export const CANVAS_BG = 0x2a4a2a;
