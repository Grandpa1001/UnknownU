import { Sprite, Texture } from "pixi.js";
import {
  APPLE_SIZE,
  CREATURE_H,
  CREATURE_W,
  FLOWER_PETALS,
  FLOWER_SIZE,
  PALETTE,
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

function eye(ctx, x, y) {
  dot(ctx, x, y, PALETTE.eyeWhite, 2, 2);
  dot(ctx, x + 1, y + 1, PALETTE.eyeBlack);
}

function paintFeature(ctx, feature, facing, frame, bob) {
  if (feature === "antena") {
    const x = facing === "down" || facing === "up" ? 11 : 16;
    const tip = frame === 1 ? 1 : 0;
    dot(ctx, x + tip, 1 + bob, PALETTE.antena, 2, 4);
    dot(ctx, x + tip, 1 + bob, PALETTE.eyeWhite);
  } else if (feature === "rogi") {
    if (facing === "right") {
      dot(ctx, 4, 8 + bob, PALETTE.horn, 3, 3);
      dot(ctx, 19, 8 + bob, PALETTE.horn, 3, 3);
    } else {
      dot(ctx, 5, 6 + bob, PALETTE.horn, 3, 3);
      dot(ctx, 16, 6 + bob, PALETTE.horn, 3, 3);
    }
  } else if (feature === "guzki") {
    const fade = frame === 1 ? PALETTE.creatureLight : PALETTE.bump;
    dot(ctx, 7, 14 + bob, fade, 2, 2);
    dot(ctx, 12, 17 + bob, fade, 2, 2);
    dot(ctx, 16, 13 + bob, fade, 2, 2);
  } else if (feature === "skrzydła") {
    const lift = frame === 1 ? -2 : 0;
    const x1 = facing === "right" ? 1 : 3;
    const x2 = facing === "right" ? 21 : 19;
    dot(ctx, x1, 12 + bob + lift, PALETTE.wing, 2, 7);
    dot(ctx, x2, 12 + bob + lift, PALETTE.wing, 2, 7);
  }
}

function paintCreature(facing, frame, feature) {
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

  paintFeature(ctx, feature, facing, frame, bob);

  const spread = frame === 1 ? 2 : 0;
  const legColor = feature === "nogi" ? PALETTE.leg : PALETTE.creatureDark;
  const legH = feature === "nogi" ? 4 : 3;
  const legY = 26 + bob;
  if (facing === "right") {
    dot(ctx, 9, legY, legColor, 2, legH);
    dot(ctx, 15 + spread, legY, legColor, 2, legH);
  } else {
    dot(ctx, 8 - spread, legY, legColor, 2, legH);
    dot(ctx, 14 + spread, legY, legColor, 2, legH);
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
  const features = ["none", "antena", "rogi", "nogi", "guzki", "skrzydła"];
  const facings = ["down", "up", "right"];
  const creatures = {};
  for (const feature of features) {
    creatures[feature] = {};
    for (const facing of facings) {
      creatures[feature][facing] = [0, 1].map((frame) =>
        textureFrom(paintCreature(facing, frame, feature)),
      );
    }
  }
  return {
    terrain,
    tree: textureFrom(paintTree()),
    flowers: [0, 1, 2].map((variant) => textureFrom(paintFlower(variant))),
    apple: textureFrom(paintApple()),
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

export function creatureTexture(feature, facing, frame) {
  const key = facing === "left" ? "right" : facing;
  const bank = getAtlas().creatures[feature] ?? getAtlas().creatures.none;
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
