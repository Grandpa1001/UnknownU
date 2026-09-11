import { useEffect, useRef } from "react";
import { Application, Container } from "pixi.js";
import { attachCamera, focusOn } from "./camera.js";
import { CANVAS_BG } from "./config.js";
import { drawApples, makeFlowers, makeTerrainSprite, makeTrees, syncOrganisms } from "./layers.js";

export default function WorldViewport({ snapshot, live }) {
  const hostRef = useRef(null);
  const sceneRef = useRef(null);
  const liveRef = useRef(live);
  liveRef.current = live;

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
      world.eventMode = "none";
      world.addChild(makeTerrainSprite(snapshot));
      world.addChild(makeFlowers(snapshot.flowers));
      world.addChild(makeTrees(snapshot.trees));
      const applesLayer = new Container();
      applesLayer.eventMode = "none";
      const organismsLayer = new Container();
      organismsLayer.eventMode = "none";
      world.addChild(applesLayer);
      world.addChild(organismsLayer);
      app.stage.addChild(world);

      let follow = true;
      const applyLive = (state) => {
        const organisms = state?.organisms ?? snapshot.organisms;
        const apples = state?.apples ?? snapshot.apples;
        syncOrganisms(organismsLayer, organismSprites, organisms);
        drawApples(applesLayer, apples);
        if (follow && organisms.length) {
          const target = organisms[0];
          focusOn(
            world,
            app.renderer.width,
            app.renderer.height,
            target.position?.x ?? target.x,
            target.position?.y ?? target.y,
            world.scale.x,
          );
        }
      };

      world.scale.set(0.8);
      applyLive(liveRef.current ?? { organisms: snapshot.organisms, apples: snapshot.apples });
      detachCamera = attachCamera(app, world, host, () => {
        follow = false;
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
  }, [live]);

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
