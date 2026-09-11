import { useEffect, useRef, useState } from "react";
import { Application, Container } from "pixi.js";
import { attachCamera, focusOn } from "./camera.js";
import { API_BASE, CANVAS_BG, WS_BASE } from "./config.js";
import { drawApples, makeFlowers, makeTerrainSprite, makeTrees, syncOrganisms } from "./layers.js";

export default function WorldViewport({ worldId }) {
  const hostRef = useRef(null);
  const hudRef = useRef(null);
  const [status, setStatus] = useState("loading");

  useEffect(() => {
    const host = hostRef.current;
    let destroyed = false;
    let app;
    let socket;
    let detachCamera = () => {};
    const organismSprites = new Map();

    async function boot() {
      const response = await fetch(`${API_BASE}/api/worlds/${worldId}`);
      if (response.status === 404) {
        if (!destroyed) {
          setStatus("missing");
        }
        return;
      }
      if (!response.ok) {
        if (!destroyed) {
          setStatus("error");
        }
        return;
      }
      const snapshot = await response.json();
      if (destroyed) {
        return;
      }

      app = new Application();
      await app.init({
        resizeTo: host,
        background: CANVAS_BG,
        antialias: false,
        autoDensity: true,
        resolution: window.devicePixelRatio || 1,
      });
      if (destroyed) {
        app.destroy();
        return;
      }
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

      let latestOrganisms = snapshot.organisms;

      drawApples(applesLayer, snapshot.apples);
      syncOrganisms(organismsLayer, organismSprites, snapshot.organisms);

      let follow = true;
      const followTarget = () => {
        if (!follow || !latestOrganisms.length) {
          return;
        }
        const target = latestOrganisms[0];
        focusOn(
          world,
          app.renderer.width,
          app.renderer.height,
          target.position?.x ?? target.x,
          target.position?.y ?? target.y,
          world.scale.x,
        );
      };

      world.scale.set(0.8);
      followTarget();
      detachCamera = attachCamera(app, world, host, () => {
        follow = false;
      });
      writeHud(snapshot.tick, snapshot.organisms);
      setStatus("ready");

      socket = new WebSocket(`${WS_BASE}/ws/worlds/${worldId}`);
      socket.onmessage = (event) => {
        const message = JSON.parse(event.data);
        latestOrganisms = message.organisms;
        syncOrganisms(organismsLayer, organismSprites, message.organisms);
        if (message.apples) {
          drawApples(applesLayer, message.apples);
        }
        followTarget();
        writeHud(message.tick, message.organisms);
      };
    }

    function writeHud(tick, organisms) {
      if (!hudRef.current) {
        return;
      }
      hudRef.current.textContent = `tick ${tick} · ${organisms.length} organizmów`;
      hudRef.current.dataset.tick = String(tick);
    }

    boot().catch(() => {
      if (!destroyed) {
        setStatus("error");
      }
    });

    return () => {
      destroyed = true;
      detachCamera();
      socket?.close();
      if (app) {
        app.destroy(true, { children: true });
      }
      host.replaceChildren();
    };
  }, [worldId]);

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
      <div ref={hudRef} className="viewport-hud" hidden={status !== "ready"} />
      {status === "loading" ? <p className="viewport-msg">Ładowanie świata…</p> : null}
      {status === "missing" ? (
        <p className="viewport-msg">
          Nie ma jeszcze świata {worldId}. Utwórz go przez POST /api/worlds, potem odśwież.
        </p>
      ) : null}
      {status === "error" ? <p className="viewport-msg">Backend nie odpowiada.</p> : null}
    </div>
  );
}
