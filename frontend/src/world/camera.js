export function attachCamera(app, world, host, onInteract) {
  app.stage.eventMode = "static";
  app.stage.hitArea = app.screen;

  let dragging = false;
  let lastX = 0;
  let lastY = 0;

  const onDown = (event) => {
    dragging = true;
    lastX = event.global.x;
    lastY = event.global.y;
    onInteract?.();
  };
  const onUp = () => {
    dragging = false;
  };
  const onMove = (event) => {
    if (!dragging) {
      return;
    }
    world.x += event.global.x - lastX;
    world.y += event.global.y - lastY;
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
