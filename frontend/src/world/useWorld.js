import { useEffect, useState } from "react";
import { API_BASE, WS_BASE } from "../world/config.js";

export function useWorld(worldId) {
  const [snapshot, setSnapshot] = useState(null);
  const [live, setLive] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    let socket;
    setSnapshot(null);
    setLive(null);
    setError(null);
    setLoading(true);

    async function boot() {
      const response = await fetch(`${API_BASE}/api/worlds/${worldId}`);
      if (cancelled) {
        return;
      }
      if (response.status === 404) {
        setError("missing");
        setLoading(false);
        return;
      }
      if (!response.ok) {
        setError("error");
        setLoading(false);
        return;
      }
      const data = await response.json();
      setSnapshot(data);
      setLive({
        tick: data.tick,
        status: data.status,
        organisms: data.organisms,
        apples: data.apples,
        events: [],
        stats: {
          tick: data.tick,
          status: data.status,
          population: data.organisms.length,
          generation: data.organisms.reduce((max, item) => Math.max(max, item.generation), 0),
          births: 0,
          deaths: 0,
          apples: data.apples.length,
        },
      });
      setLoading(false);
      socket = new WebSocket(`${WS_BASE}/ws/worlds/${worldId}`);
      socket.onmessage = (event) => {
        if (cancelled) {
          return;
        }
        setLive(JSON.parse(event.data));
      };
    }

    boot().catch(() => {
      if (!cancelled) {
        setError("error");
        setLoading(false);
      }
    });

    return () => {
      cancelled = true;
      socket?.close();
    };
  }, [worldId]);

  return { snapshot, live, error, loading };
}
