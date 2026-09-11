export function attachCamera(app, world, host, options = {}) {
  const onInteract = typeof options === "function" ? options : options.onInteract;
  const hitTest = typeof options === "function" ? null : options.hitTest;
  const onSelect = typeof options === "function" ? null : options.onSelect;

  let dragging = false;
  let moved = false;
  let lastX = 0;
  let lastY = 0;
  let pendingSelect = null;

  const worldPos = (clientX, clientY) => {
    const bounds = app.canvas.getBoundingClientRect();
    const px = clientX - bounds.left;
    const py = clientY - bounds.top;
    const scale = world.scale.x;
    return {
      x: (px - world.x) / scale,
      y: (py - world.y) / scale,
    };
  };

  const onDown = (event) => {
    if (event.button !== 0) {
      return;
    }
    lastX = event.clientX;
    lastY = event.clientY;
    moved = false;
    const local = worldPos(event.clientX, event.clientY);
    pendingSelect = hitTest ? hitTest(local.x, local.y) : null;
    dragging = !pendingSelect;
    if (dragging) {
      onInteract?.();
      host.style.cursor = "grabbing";
    }
  };
  const onUp = () => {
    if (pendingSelect) {
      onSelect?.(pendingSelect);
    } else if (!moved) {
      onSelect?.(null);
    }
    dragging = false;
    pendingSelect = null;
    host.style.cursor = "grab";
  };
  const onMove = (event) => {
    const dx = event.clientX - lastX;
    const dy = event.clientY - lastY;
    if (Math.abs(dx) + Math.abs(dy) > 3) {
      moved = true;
    }
    if (!dragging) {
      return;
    }
    world.x += dx;
    world.y += dy;
    lastX = event.clientX;
    lastY = event.clientY;
  };

  host.addEventListener("pointerdown", onDown);
  window.addEventListener("pointerup", onUp);
  window.addEventListener("pointermove", onMove);

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
    onInteract?.();
  };
  host.addEventListener("wheel", onWheel, { passive: false });

  return () => {
    host.removeEventListener("pointerdown", onDown);
    window.removeEventListener("pointerup", onUp);
    window.removeEventListener("pointermove", onMove);
    host.removeEventListener("wheel", onWheel);
  };
}

export function focusOn(world, viewWidth, viewHeight, x, y, scale) {
  world.scale.set(scale);
  world.x = viewWidth / 2 - x * scale;
  world.y = viewHeight / 2 - y * scale;
}

export function lerpToward(world, viewWidth, viewHeight, x, y, alpha = 0.14) {
  const scale = world.scale.x;
  const targetX = viewWidth / 2 - x * scale;
  const targetY = viewHeight / 2 - y * scale;
  world.x += (targetX - world.x) * alpha;
  world.y += (targetY - world.y) * alpha;
}
