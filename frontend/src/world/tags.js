function storageKey(worldId) {
  return `unknown:tags:${worldId}`;
}

export function loadTags(worldId) {
  if (worldId == null) {
    return [];
  }
  try {
    const parsed = JSON.parse(localStorage.getItem(storageKey(worldId)) || "[]");
    return Array.isArray(parsed) ? parsed.filter((id) => typeof id === "string") : [];
  } catch {
    return [];
  }
}

export function saveTags(worldId, ids) {
  if (worldId == null) {
    return;
  }
  localStorage.setItem(storageKey(worldId), JSON.stringify([...new Set(ids)]));
}
