import { Sprite, Texture } from "pixi.js";
import {
  APPLE_SIZE,
  BERRY_SIZE,
  BUSH_H,
  BUSH_W,
  CREATURE_H,
  CREATURE_W,
  FLOWER_PETALS,
  FLOWER_SIZE,
  PALETTE,
  PILLAR_H,
  PILLAR_W,
  SPINNER_SIZE,
  TILE_ART,
  TREE_SIZE,
} from "./config.js";

let atlas = null;

function canvas(width, height) {
  const node = document.createElement("canvas");
  node.width = width;
  node.height = height;
  const ctx = node.getContext("2d");
  ctx.imageSmoothingEnabled = false;
  return { node, ctx };
}

function dot(ctx, x, y, color, w = 1, h = 1) {
  ctx.fillStyle = color;
  ctx.fillRect(x, y, w, h);
}

function ellipse(ctx, cx, cy, rx, ry, color) {
  ctx.fillStyle = color;
  const rx2 = rx * rx;
  const ry2 = ry * ry;
  for (let y = -ry; y <= ry; y += 1) {
    for (let x = -rx; x <= rx; x += 1) {
      if (x * x * ry2 + y * y * rx2 <= rx2 * ry2) {
        ctx.fillRect(cx + x, cy + y, 1, 1);
      }
    }
  }
}

function textureFrom(node) {
  const texture = Texture.from(node);
  if (texture.source) {
    texture.source.scaleMode = "nearest";
  }
  return texture;
}

function paintTile(kind, variant) {
  const { node, ctx } = canvas(TILE_ART, TILE_ART);
  if (kind === "dirt") {
    ctx.fillStyle = PALETTE.dirt;
    ctx.fillRect(0, 0, TILE_ART, TILE_ART);
    for (let i = 0; i < 5; i += 1) {
      const x = (variant * 3 + i * 5) % 14;
      const y = (variant * 5 + i * 3) % 14;
      dot(ctx, x, y, PALETTE.dirtDark, 2, 1);
    }
    dot(ctx, 1 + (variant % 3), 1, PALETTE.dirtLight, 2, 2);
    return node;
  }
  if (kind === "meadow") {
    ctx.fillStyle = PALETTE.meadow;
    ctx.fillRect(0, 0, TILE_ART, TILE_ART);
    const petals = FLOWER_PETALS;
    for (let i = 0; i < 5; i += 1) {
      const x = (2 + variant * 2 + i * 4) % 14;
      const y = (3 + i * 3 + variant) % 14;
      dot(ctx, x, y, petals[(i + variant) % petals.length]);
    }
    return node;
  }
  if (kind === "hills") {
    ctx.fillStyle = PALETTE.hillsLight;
    ctx.fillRect(0, 0, TILE_ART, TILE_ART);
    ctx.fillStyle = PALETTE.hills;
    for (let y = 8; y < TILE_ART; y += 1) {
      ctx.fillRect(0, y, TILE_ART, 1);
    }
    dot(ctx, 2 + variant, 3, PALETTE.grassLight, 3, 2);
    dot(ctx, 9, 11, PALETTE.dirtDark, 2, 2);
    return node;
  }
  ctx.fillStyle = PALETTE.grass;
  ctx.fillRect(0, 0, TILE_ART, TILE_ART);
  const spots = [
    [2 + (variant % 3), 3, 2, 2],
    [9, 5 + (variant % 2), 3, 2],
    [4, 11, 2, 3],
    [12, 12, 2, 2],
  ];
  for (const [x, y, w, h] of spots) {
    dot(ctx, x, y, PALETTE.grassDark, w, h);
  }
  dot(ctx, 1, 1, PALETTE.grassLight, 2, 1);
  return node;
}

function paintTree() {
  const { node, ctx } = canvas(TREE_SIZE, TREE_SIZE);
  ellipse(ctx, 24, 42, 14, 3, PALETTE.grassDark);
  ctx.globalAlpha = 0.45;
  ellipse(ctx, 24, 42, 14, 3, PALETTE.grassDark);
  ctx.globalAlpha = 1;
  dot(ctx, 20, 28, PALETTE.trunk, 8, 16);
  dot(ctx, 26, 28, PALETTE.trunkLight, 2, 16);
  ellipse(ctx, 24, 18, 16, 14, PALETTE.foliage);
  ellipse(ctx, 16, 20, 10, 9, PALETTE.foliage);
  ellipse(ctx, 32, 20, 10, 9, PALETTE.foliage);
  ellipse(ctx, 28, 14, 7, 6, PALETTE.foliageMid);
  return node;
}

function paintPillar() {
  const { node, ctx } = canvas(PILLAR_W, PILLAR_H);
  const cx = 18;
  ellipse(ctx, cx, 66, 14, 4, PALETTE.grassDark);
  ctx.globalAlpha = 0.4;
  ellipse(ctx, cx, 66, 16, 5, PALETTE.stoneDark);
  ctx.globalAlpha = 1;
  dot(ctx, 6, 62, PALETTE.stoneDark, 24, 6);
  dot(ctx, 8, 61, PALETTE.stone, 20, 4);
  dot(ctx, 11, 18, PALETTE.stoneDark, 14, 44);
  dot(ctx, 12, 16, PALETTE.stone, 12, 46);
  dot(ctx, 14, 16, PALETTE.stoneLight, 3, 46);
  dot(ctx, 11, 30, PALETTE.stoneDark, 14, 3);
  dot(ctx, 11, 46, PALETTE.stoneDark, 14, 2);
  dot(ctx, 13, 22, PALETTE.moss, 2, 3);
  dot(ctx, 21, 38, PALETTE.moss, 2, 2);
  dot(ctx, 15, 52, PALETTE.moss, 3, 2);
  dot(ctx, 13, 8, PALETTE.stoneDark, 10, 10);
  dot(ctx, 14, 6, PALETTE.stone, 8, 12);
  dot(ctx, 16, 6, PALETTE.stoneLight, 3, 8);
  dot(ctx, 16, 4, PALETTE.stoneLight, 4, 3);
  return node;
}

function paintFlower(variant) {
  const { node, ctx } = canvas(FLOWER_SIZE, FLOWER_SIZE);
  const petal = FLOWER_PETALS[variant % FLOWER_PETALS.length];
  const cx = 4;
  const cy = 4;
  const arms = [
    [0, -2],
    [2, 0],
    [0, 2],
    [-2, 0],
    [1, -1],
    [-1, 1],
  ];
  for (const [dx, dy] of arms) {
    dot(ctx, cx + dx, cy + dy, petal, 2, 2);
  }
  dot(ctx, cx, cy, PALETTE.flowerCenter, 2, 2);
  return node;
}

function paintApple() {
  const { node, ctx } = canvas(APPLE_SIZE, APPLE_SIZE);
  ellipse(ctx, 3, 3, 2, 2, PALETTE.apple);
  dot(ctx, 2, 4, PALETTE.appleDark);
  dot(ctx, 2, 1, PALETTE.eyeWhite);
  dot(ctx, 3, 0, PALETTE.trunk, 1, 2);
  return node;
}

function paintBerry() {
  const { node, ctx } = canvas(BERRY_SIZE, BERRY_SIZE);
  ellipse(ctx, 3, 3, 2, 2, PALETTE.berry);
  dot(ctx, 1, 1, PALETTE.berryLight);
  return node;
}

function paintBush() {
  const { node, ctx } = canvas(BUSH_W, BUSH_H);
  ellipse(ctx, 18, 24, 16, 4, PALETTE.grassDark);
  ellipse(ctx, 18, 16, 16, 10, PALETTE.foliage);
  ellipse(ctx, 9, 18, 9, 8, PALETTE.foliageMid);
  ellipse(ctx, 27, 18, 9, 8, PALETTE.foliage);
  ellipse(ctx, 18, 10, 11, 8, PALETTE.foliageMid);
  ellipse(ctx, 12, 12, 6, 5, PALETTE.foliage);
  ellipse(ctx, 24, 11, 6, 5, PALETTE.foliage);
  dot(ctx, 10, 12, PALETTE.berry, 3, 3);
  dot(ctx, 17, 8, PALETTE.berryLight, 3, 3);
  dot(ctx, 25, 13, PALETTE.berry, 3, 3);
  dot(ctx, 14, 17, PALETTE.berryLight, 2, 2);
  dot(ctx, 22, 18, PALETTE.berry, 2, 2);
  return node;
}

function eye(ctx, x, y) {
  dot(ctx, x, y, PALETTE.eyeWhite, 2, 2);
  dot(ctx, x + 1, y + 1, PALETTE.eyeBlack);
}

function paintCreature(facing, frame) {
  const { node, ctx } = canvas(CREATURE_W, CREATURE_H);
  const bob = frame === 1 ? -1 : 0;
  const cx = 12;
  const cy = 16 + bob;
  ellipse(ctx, cx, cy + 1, 9, 12, PALETTE.creatureDark);
  ellipse(ctx, cx, cy, 8, 11, PALETTE.creature);
  ellipse(ctx, cx + 2, cy - 4, 3, 4, PALETTE.creatureLight);

  if (facing === "up") {
    dot(ctx, 8, 8 + bob, PALETTE.creatureLight, 2, 1);
    dot(ctx, 14, 8 + bob, PALETTE.creatureLight, 2, 1);
  } else if (facing === "down") {
    eye(ctx, 8, 10 + bob);
    eye(ctx, 14, 10 + bob);
  } else {
    eye(ctx, 13, 10 + bob);
    eye(ctx, 17, 10 + bob);
  }

  const spread = frame === 1 ? 2 : 0;
  const legY = 26 + bob;
  if (facing === "right") {
    dot(ctx, 9, legY, PALETTE.creatureDark, 2, 3);
    dot(ctx, 15 + spread, legY, PALETTE.creatureDark, 2, 3);
  } else {
    dot(ctx, 8 - spread, legY, PALETTE.creatureDark, 2, 3);
    dot(ctx, 14 + spread, legY, PALETTE.creatureDark, 2, 3);
  }
  return node;
}

function paintSpinner(frame) {
  const { node, ctx } = canvas(SPINNER_SIZE, SPINNER_SIZE);
  const cx = 3.5;
  const cy = 3.5;
  const angle = (frame / 8) * Math.PI * 2;
  const x = Math.round(cx + Math.cos(angle) * 3);
  const y = Math.round(cy + Math.sin(angle) * 3);
  dot(ctx, 3, 3, PALETTE.spinner);
  dot(ctx, x, y, PALETTE.spinner, 2, 2);
  return node;
}

function buildAtlas() {
  const terrain = {};
  for (const kind of ["grass", "dirt", "meadow", "hills"]) {
    terrain[kind] = [0, 1, 2, 3].map((variant) => paintTile(kind, variant));
  }
  const facings = ["down", "up", "right"];
  const creatures = {};
  for (const facing of facings) {
    creatures[facing] = [0, 1].map((frame) => textureFrom(paintCreature(facing, frame)));
  }
  return {
    terrain,
    tree: textureFrom(paintTree()),
    pillar: textureFrom(paintPillar()),
    flowers: [0, 1, 2].map((variant) => textureFrom(paintFlower(variant))),
    apple: textureFrom(paintApple()),
    berry: textureFrom(paintBerry()),
    bush: textureFrom(paintBush()),
    spinner: [0, 1, 2, 3, 4, 5, 6, 7].map((frame) => textureFrom(paintSpinner(frame))),
    creatures,
  };
}

export function getAtlas() {
  if (!atlas) {
    atlas = buildAtlas();
  }
  return atlas;
}

export function facingFromDirection(radians) {
  const tau = Math.PI * 2;
  const angle = ((radians % tau) + tau) % tau;
  if (angle >= Math.PI * 1.75 || angle < Math.PI * 0.25) {
    return "right";
  }
  if (angle < Math.PI * 0.75) {
    return "down";
  }
  if (angle < Math.PI * 1.25) {
    return "left";
  }
  return "up";
}

export function creatureTexture(facing, frame) {
  const key = facing === "left" ? "right" : facing;
  const bank = getAtlas().creatures;
  return bank[key][frame] ?? bank[key][0];
}

export function makeTerrainSprite(snapshot) {
  const tiles = snapshot.terrain;
  const tileSize = snapshot.tile_size || TILE_ART;
  const rows = tiles.length;
  const cols = tiles[0].length;
  const bake = 4;
  const { node, ctx } = canvas(cols * bake, rows * bake);
  const sheets = getAtlas().terrain;
  for (let y = 0; y < rows; y += 1) {
    for (let x = 0; x < cols; x += 1) {
      const kind = tiles[y][x];
      const variant = (x * 13 + y * 7) % 4;
      const tile = (sheets[kind] || sheets.grass)[variant];
      ctx.drawImage(tile, 0, 0, TILE_ART, TILE_ART, x * bake, y * bake, bake, bake);
    }
  }
  const sprite = Sprite.from(node);
  if (sprite.texture?.source) {
    sprite.texture.source.scaleMode = "nearest";
  }
  sprite.scale.set(tileSize / bake);
  sprite.eventMode = "none";
  sprite.roundPixels = true;
  return sprite;
}

export function pixelSprite(texture, anchorX = 0.5, anchorY = 0.5) {
  const sprite = new Sprite(texture);
  sprite.anchor.set(anchorX, anchorY);
  sprite.eventMode = "none";
  sprite.roundPixels = true;
  return sprite;
}
