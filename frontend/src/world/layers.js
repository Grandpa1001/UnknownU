import { Container, Graphics, Sprite } from "pixi.js";
import {
  APPLE,
  CREATURE,
  FLOWER_COLORS,
  FOLIAGE,
  TERRAIN_COLORS,
  TRUNK,
} from "./config.js";

export function makeTerrainSprite(snapshot) {
  const tiles = snapshot.terrain;
  const tileSize = snapshot.tile_size || 16;
  const rows = tiles.length;
  const cols = tiles[0].length;
  const canvas = document.createElement("canvas");
  canvas.width = cols;
  canvas.height = rows;
  const ctx = canvas.getContext("2d");
  const image = ctx.createImageData(cols, rows);
  for (let y = 0; y < rows; y += 1) {
    for (let x = 0; x < cols; x += 1) {
      const color = TERRAIN_COLORS[tiles[y][x]] || TERRAIN_COLORS.grass;
      const index = (y * cols + x) * 4;
      image.data[index] = color[0];
      image.data[index + 1] = color[1];
      image.data[index + 2] = color[2];
      image.data[index + 3] = color[3];
    }
  }
  ctx.putImageData(image, 0, 0);
  const sprite = Sprite.from(canvas);
  sprite.scale.set(tileSize);
  sprite.eventMode = "none";
  return sprite;
}

export function makeFlowers(flowers) {
  const layer = new Container();
  layer.eventMode = "none";
  for (const flower of flowers) {
    const graphic = new Graphics();
    graphic.circle(0, 0, 3).fill(FLOWER_COLORS[flower.variant % FLOWER_COLORS.length]);
    graphic.position.set(flower.x, flower.y);
    graphic.eventMode = "none";
    layer.addChild(graphic);
  }
  return layer;
}

export function makeTrees(trees) {
  const layer = new Container();
  layer.eventMode = "none";
  for (const tree of trees) {
    const graphic = new Graphics();
    graphic.circle(0, 0, 18).fill(FOLIAGE);
    graphic.circle(0, 5, 6).fill(TRUNK);
    graphic.position.set(tree.x, tree.y);
    graphic.eventMode = "none";
    layer.addChild(graphic);
  }
  return layer;
}

export function drawApples(layer, apples) {
  layer.removeChildren();
  for (const apple of apples) {
    const graphic = new Graphics();
    graphic.circle(0, 0, 4).fill(APPLE);
    graphic.position.set(apple.x, apple.y);
    graphic.eventMode = "none";
    layer.addChild(graphic);
  }
}

export function organismRadius(organism) {
  return Math.max(14, (organism.size || 8) * 1.8);
}

export function hitOrganism(organisms, worldX, worldY, scale = 1) {
  let best = null;
  let bestDist = Infinity;
  const minRadius = 12 / Math.max(scale, 0.02);
  for (const organism of organisms) {
    const x = organism.position?.x ?? organism.x;
    const y = organism.position?.y ?? organism.y;
    const radius = Math.max(organismRadius(organism) + 4, minRadius);
    const dx = x - worldX;
    const dy = y - worldY;
    const dist = dx * dx + dy * dy;
    if (dist <= radius * radius && dist < bestDist) {
      best = organism;
      bestDist = dist;
    }
  }
  return best;
}

export function drawTags(layer, organisms, taggedIds) {
  layer.removeChildren();
  const tagged = new Set(taggedIds);
  for (const organism of organisms) {
    if (!tagged.has(organism.id)) {
      continue;
    }
    const radius = organismRadius(organism);
    const mark = new Graphics();
    mark.poly([0, 0, -5, 10, 5, 10]).fill(0xffd700);
    mark.position.set(
      organism.position?.x ?? organism.x,
      (organism.position?.y ?? organism.y) - radius - 12,
    );
    mark.eventMode = "none";
    layer.addChild(mark);
  }
}

export function syncOrganisms(layer, sprites, organisms) {
  const seen = new Set();
  for (const organism of organisms) {
    seen.add(organism.id);
    let graphic = sprites.get(organism.id);
    if (!graphic) {
      graphic = new Graphics();
      const radius = organismRadius(organism);
      graphic.circle(0, 0, radius + 2).fill(0xf2f6ff);
      graphic.circle(0, 0, radius).fill(CREATURE);
      graphic.eventMode = "none";
      layer.addChild(graphic);
      sprites.set(organism.id, graphic);
    }
    graphic.organismId = organism.id;
    const x = organism.position?.x ?? organism.x;
    const y = organism.position?.y ?? organism.y;
    graphic.position.set(x, y);
  }
  for (const [id, graphic] of sprites) {
    if (!seen.has(id)) {
      graphic.destroy();
      sprites.delete(id);
    }
  }
}
