import { useEffect, useRef } from "react";
import { Application, Container, Graphics } from "pixi.js";
import { attachCamera, focusOn, lerpToward } from "./camera.js";
import { CANVAS_BG } from "./config.js";
import {
  drawApples,
  drawTags,
  hitOrganism,
  makeFlowers,
  makeTerrainSprite,
  makeTrees,
  organismRadius,
  syncOrganisms,
} from "./layers.js";

export default function WorldViewport({ snapshot, live, selectedId, taggedIds, followId, onSelect, onFollowLost }) {
  const hostRef = useRef(null);
  const sceneRef = useRef(null);
  const liveRef = useRef(live);
  const selectedRef = useRef(selectedId);
  const taggedRef = useRef(taggedIds);
  const followRef = useRef(followId);
  const onSelectRef = useRef(onSelect);
  const onFollowLostRef = useRef(onFollowLost);
  liveRef.current = live;
  selectedRef.current = selectedId;
  taggedRef.current = taggedIds ?? [];
  onSelectRef.current = onSelect;
  onFollowLostRef.current = onFollowLost;

  useEffect(() => {
    followRef.current = followId;
  }, [followId]);

  useEffect(() => {
    const host = hostRef.current;
    if (!host || !snapshot) {
      return undefined;
    }
    let destroyed = false;
    let app;
    let detachCamera = () => {};
    const organismSprites = new Map();

    async function boot() {
      const instance = new Application();
      try {
        await instance.init({
          resizeTo: host,
          background: CANVAS_BG,
          antialias: false,
          autoDensity: true,
          resolution: window.devicePixelRatio || 1,
        });
      } catch (error) {
        instance.destroy(true);
        throw error;
      }
      if (destroyed) {
        instance.destroy(true);
        return;
      }
      app = instance;
      host.appendChild(app.canvas);
      app.canvas.style.display = "block";
      app.canvas.style.width = "100%";
      app.canvas.style.height = "100%";
      app.canvas.style.cursor = "grab";
      app.canvas.setAttribute("role", "application");
      app.canvas.setAttribute("aria-label", "mapa świata");

      const world = new Container();
      world.eventMode = "passive";
      world.addChild(makeTerrainSprite(snapshot));
      world.addChild(makeFlowers(snapshot.flowers));
      world.addChild(makeTrees(snapshot.trees));
      const applesLayer = new Container();
      applesLayer.eventMode = "none";
      const organismsLayer = new Container();
      organismsLayer.eventMode = "passive";
      const ring = new Graphics();
      ring.eventMode = "none";
      const tagsLayer = new Container();
      tagsLayer.eventMode = "none";
      world.addChild(applesLayer);
      world.addChild(organismsLayer);
      world.addChild(ring);
      world.addChild(tagsLayer);
      app.stage.addChild(world);

      const applyLive = (state) => {
        const organisms = state?.organisms ?? snapshot.organisms;
        const apples = state?.apples ?? snapshot.apples;
        syncOrganisms(organismsLayer, organismSprites, organisms);
        drawApples(applesLayer, apples);
        drawTags(tagsLayer, organisms, taggedRef.current);
        const selected = organisms.find((item) => item.id === selectedRef.current);
        ring.clear();
        if (selected) {
          const radius = organismRadius(selected) + 6;
          ring.circle(0, 0, radius).stroke({ width: 2, color: 0xf2f6ff });
          ring.position.set(selected.position?.x ?? selected.x, selected.position?.y ?? selected.y);
        }
      };

      world.scale.set(0.8);
      const start = snapshot.organisms[0];
      if (start) {
        focusOn(
          world,
          app.renderer.width,
          app.renderer.height,
          start.position?.x ?? start.x,
          start.position?.y ?? start.y,
          0.8,
        );
      } else {
        focusOn(world, app.renderer.width, app.renderer.height, snapshot.width / 2, snapshot.height / 2, 0.35);
      }
      applyLive(liveRef.current ?? { organisms: snapshot.organisms, apples: snapshot.apples });
      detachCamera = attachCamera(app, world, host, {
        onInteract: () => {
          followRef.current = null;
          onFollowLostRef.current?.("camera");
        },
        hitTest: (worldX, worldY) => {
          const organisms = liveRef.current?.organisms ?? snapshot.organisms;
          return hitOrganism(organisms, worldX, worldY, world.scale.x)?.id ?? null;
        },
        onSelect: (organismId) => onSelectRef.current?.(organismId),
      });
      app.ticker.add(() => {
        const id = followRef.current;
        if (!id) {
          return;
        }
        const organisms = liveRef.current?.organisms ?? snapshot.organisms;
        const target = organisms.find((item) => item.id === id);
        if (!target) {
          return;
        }
        lerpToward(
          world,
          app.renderer.width,
          app.renderer.height,
          target.position?.x ?? target.x,
          target.position?.y ?? target.y,
        );
      });
      sceneRef.current = { applyLive };
    }

    boot().catch((error) => {
      console.error("viewport boot failed", error);
    });
    return () => {
      destroyed = true;
      sceneRef.current = null;
      detachCamera();
      if (app) {
        app.destroy(true, { children: true });
        app = undefined;
      }
      host.replaceChildren();
    };
  }, [snapshot]);

  useEffect(() => {
    sceneRef.current?.applyLive(live);
  }, [live, selectedId, taggedIds]);

  return (
    <div className="viewport">
      <div
        ref={hostRef}
        className="viewport-canvas"
        data-testid="world-canvas"
        role="application"
        aria-label="mapa świata"
        tabIndex={0}
      />
    </div>
  );
}
