import { Container, Graphics } from "pixi.js";
import { PALETTE } from "./config.js";
import {
  CREATURE_H,
  DEATH_FADE_MS,
  SELECT_RING,
  SPINNER_FRAME_MS,
  TAG_GOLD,
  WALK_FRAME_MS,
} from "./config.js";
import {
  creatureTexture,
  facingFromDirection,
  getAtlas,
  makeTerrainSprite,
  pixelSprite,
} from "./sprites.js";

export { makeTerrainSprite };

export function organismRadius(organism) {
  return Math.max(13, (organism.size || 8) * 1.6);
}

export function hitOrganism(organisms, worldX, worldY, scale = 1) {
  let best = null;
  let bestDist = Infinity;
  const minRadius = 12 / Math.max(scale, 0.02);
  for (const organism of organisms) {
    const x = organism.position?.x ?? organism.x;
    const y = organism.position?.y ?? organism.y;
    const radius = Math.max(organismRadius(organism) + 8, minRadius);
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

export function makeFlowers(flowers) {
  const layer = new Container();
  layer.eventMode = "none";
  const atlas = getAtlas();
  for (const flower of flowers) {
    const sprite = pixelSprite(atlas.flowers[flower.variant % atlas.flowers.length]);
    sprite.position.set(flower.x, flower.y);
    layer.addChild(sprite);
  }
  return layer;
}

export function makeTrees(trees) {
  const layer = new Container();
  layer.eventMode = "none";
  const atlas = getAtlas();
  for (const tree of trees) {
    const sprite = pixelSprite(atlas.tree, 0.5, 0.72);
    sprite.position.set(tree.x, tree.y);
    layer.addChild(sprite);
  }
  return layer;
}

export function makeBushes(bushes) {
  const layer = new Container();
  layer.eventMode = "none";
  const atlas = getAtlas();
  for (const bush of bushes ?? []) {
    const sprite = pixelSprite(atlas.bush, 0.5, 0.78);
    sprite.position.set(bush.x, bush.y);
    layer.addChild(sprite);
  }
  return layer;
}

export function makePillar(pillar) {
  const layer = new Container();
  layer.eventMode = "none";
  const x = pillar.x;
  const y = pillar.y;
  const radius = pillar.radius || 22;
  const plaza = new Graphics();
  plaza.circle(0, 0, radius + 20).fill({
    color: Number.parseInt(PALETTE.dirtDark.slice(1), 16),
    alpha: 0.38,
  });
  plaza.circle(0, 0, radius + 8).stroke({
    width: 2,
    color: Number.parseInt(PALETTE.stoneDark.slice(1), 16),
    alpha: 0.8,
  });
  plaza.position.set(x, y);
  layer.addChild(plaza);
  const sprite = pixelSprite(getAtlas().pillar, 0.5, 0.86);
  sprite.position.set(x, y);
  layer.addChild(sprite);
  return layer;
}

export function syncApples(layer, sprites, apples) {
  const seen = new Set();
  const atlas = getAtlas();
  for (const apple of apples) {
    seen.add(apple.id);
    let sprite = sprites.get(apple.id);
    if (!sprite) {
      sprite = pixelSprite(atlas.apple);
      layer.addChild(sprite);
      sprites.set(apple.id, sprite);
    }
    sprite.position.set(apple.x, apple.y);
  }
  for (const [id, sprite] of sprites) {
    if (!seen.has(id)) {
      sprite.destroy();
      sprites.delete(id);
    }
  }
}

export function syncBerries(layer, sprites, berries) {
  const seen = new Set();
  const atlas = getAtlas();
  for (const berry of berries ?? []) {
    seen.add(berry.id);
    let sprite = sprites.get(berry.id);
    if (!sprite) {
      sprite = pixelSprite(atlas.berry);
      layer.addChild(sprite);
      sprites.set(berry.id, sprite);
    }
    sprite.position.set(berry.x, berry.y);
  }
  for (const [id, sprite] of sprites) {
    if (!seen.has(id)) {
      sprite.destroy();
      sprites.delete(id);
    }
  }
}

function createOrganismVisual(organism) {
  const atlas = getAtlas();
  const body = pixelSprite(creatureTexture("down", 0), 0.5, 0.72);
  const held = pixelSprite(atlas.apple);
  held.position.set(8, -10);
  held.visible = Boolean(organism.carrying);
  const spinner = pixelSprite(atlas.spinner[0]);
  spinner.position.set(0, -Math.round(CREATURE_H * 0.55));
  spinner.visible = false;
  const container = new Container();
  container.eventMode = "none";
  container.addChild(body);
  container.addChild(held);
  container.addChild(spinner);
  return {
    container,
    body,
    held,
    spinner,
    organism,
    dying: false,
    diedAt: 0,
  };
}

function pose(organism, now) {
  const facing = facingFromDirection(organism.direction ?? 0);
  const walking = organism.last_action === "MOVE" || organism.last_action === "ACCEL";
  const frameMs = organism.last_action === "ACCEL" ? Math.max(80, WALK_FRAME_MS / 2) : WALK_FRAME_MS;
  const frame = walking ? Math.floor(now / frameMs) % 2 : 0;
  return { facing, frame };
}

function applyOrganismPose(visual, organism, now) {
  const { facing, frame } = pose(organism, now);
  visual.body.texture = creatureTexture(facing, frame);
  visual.body.scale.x = facing === "left" ? -1 : 1;
  const size = organism.size || 8;
  const scale = 1.15 + size / 40;
  visual.container.scale.set(scale);
  visual.held.visible = Boolean(organism.carrying);
  visual.held.position.set(facing === "left" ? -8 : 8, -10);
  visual.spinner.visible = Boolean(organism.is_thinking);
  if (visual.spinner.visible) {
    const spin = Math.floor(now / SPINNER_FRAME_MS) % 8;
    visual.spinner.texture = getAtlas().spinner[spin];
  }
}

export function syncOrganisms(layer, sprites, organisms, now) {
  const seen = new Set();
  for (const organism of organisms) {
    seen.add(organism.id);
    let visual = sprites.get(organism.id);
    if (!visual) {
      visual = createOrganismVisual(organism);
      layer.addChild(visual.container);
      sprites.set(organism.id, visual);
    }
    visual.organism = organism;
    visual.dying = false;
    visual.container.alpha = 1;
    visual.container.position.set(organism.position?.x ?? organism.x, organism.position?.y ?? organism.y);
    applyOrganismPose(visual, organism, now);
  }
  for (const [id, visual] of sprites) {
    if (!seen.has(id) && !visual.dying) {
      visual.dying = true;
      visual.diedAt = now;
      visual.spinner.visible = false;
    }
  }
}

export function tickOrganisms(sprites, now) {
  for (const [id, visual] of sprites) {
    if (visual.dying) {
      const t = (now - visual.diedAt) / DEATH_FADE_MS;
      if (t >= 1) {
        visual.container.destroy({ children: true });
        sprites.delete(id);
      } else {
        visual.container.alpha = Math.max(0, 1 - t);
      }
      continue;
    }
    applyOrganismPose(visual, visual.organism, now);
  }
}

export function drawTags(layer, organisms, taggedIds) {
  for (const child of layer.removeChildren()) {
    child.destroy();
  }
  const tagged = new Set(taggedIds);
  for (const organism of organisms) {
    if (!tagged.has(organism.id)) {
      continue;
    }
    const radius = organismRadius(organism);
    const mark = new Graphics();
    mark.rect(-1, 0, 2, 8).fill(TAG_GOLD);
    mark.poly([0, 0, -4, 7, 4, 7]).fill(TAG_GOLD);
    mark.position.set(
      organism.position?.x ?? organism.x,
      (organism.position?.y ?? organism.y) - radius - 14,
    );
    mark.eventMode = "none";
    layer.addChild(mark);
  }
}

export function drawCache(mark, cache) {
  mark.clear();
  if (!cache) {
    return;
  }
  mark.circle(0, 0, 16).stroke({ width: 2, color: Number.parseInt(PALETTE.cacheRing.slice(1), 16) });
  mark.circle(0, 0, 5).fill(Number.parseInt(PALETTE.cache.slice(1), 16));
  mark.position.set(cache.x, cache.y);
}

export function drawSelectRing(ring, organism) {
  ring.clear();
  if (!organism) {
    return;
  }
  const radius = organismRadius(organism) + 6;
  ring.rect(-radius, -radius, radius * 2, 2).fill(SELECT_RING);
  ring.rect(-radius, radius - 2, radius * 2, 2).fill(SELECT_RING);
  ring.rect(-radius, -radius, 2, radius * 2).fill(SELECT_RING);
  ring.rect(radius - 2, -radius, 2, radius * 2).fill(SELECT_RING);
  ring.position.set(organism.position?.x ?? organism.x, organism.position?.y ?? organism.y);
}
