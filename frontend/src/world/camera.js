export function attachCamera(app, world, host, options = {}) {
  const onInteract = typeof options === "function" ? options : options.onInteract;
  const hitTest = typeof options === "function" ? null : options.hitTest;
  const onSelect = typeof options === "function" ? null : options.onSelect;

  app.stage.eventMode = "static";
  app.stage.hitArea = app.screen;

  let dragging = false;
  let moved = false;
  let lastX = 0;
  let lastY = 0;
  let pendingSelect = null;

  const onDown = (event) => {
    lastX = event.global.x;
    lastY = event.global.y;
    moved = false;
    const local = event.getLocalPosition(world);
    pendingSelect = hitTest ? hitTest(local.x, local.y) : null;
    dragging = !pendingSelect;
    if (dragging) {
      onInteract?.();
    }
  };
  const onUp = () => {
    if (pendingSelect) {
      onSelect?.(pendingSelect);
      onInteract?.();
    } else if (!moved) {
      onSelect?.(null);
    }
    dragging = false;
    pendingSelect = null;
  };
  const onMove = (event) => {
    const dx = event.global.x - lastX;
    const dy = event.global.y - lastY;
    if (Math.abs(dx) + Math.abs(dy) > 3) {
      moved = true;
    }
    if (!dragging) {
      return;
    }
    world.x += dx;
    world.y += dy;
    lastX = event.global.x;
    lastY = event.global.y;
  };

  app.stage.on("pointerdown", onDown);
  app.stage.on("pointerup", onUp);
  app.stage.on("pointerupoutside", onUp);
  app.stage.on("pointermove", onMove);

  const onWheel = (event) => {
    event.preventDefault();
    const scale = world.scale.x;
    const next = Math.min(3.5, Math.max(0.06, scale * (event.deltaY > 0 ? 0.9 : 1.1)));
    const bounds = app.canvas.getBoundingClientRect();
    const px = event.clientX - bounds.left;
    const py = event.clientY - bounds.top;
    const worldX = (px - world.x) / scale;
    const worldY = (py - world.y) / scale;
    world.scale.set(next);
    world.x = px - worldX * next;
    world.y = py - worldY * next;
  };
  host.addEventListener("wheel", onWheel, { passive: false });

  return () => {
    app.stage.off("pointerdown", onDown);
    app.stage.off("pointerup", onUp);
    app.stage.off("pointerupoutside", onUp);
    app.stage.off("pointermove", onMove);
    host.removeEventListener("wheel", onWheel);
  };
}

export function focusOn(world, viewWidth, viewHeight, x, y, scale) {
  world.scale.set(scale);
  world.x = viewWidth / 2 - x * scale;
  world.y = viewHeight / 2 - y * scale;
}
