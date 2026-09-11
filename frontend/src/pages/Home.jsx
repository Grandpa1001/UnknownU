import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE } from "../world/config.js";

export default function Home() {
  const navigate = useNavigate();
  const [name, setName] = useState("świat");
  const [count, setCount] = useState(3);
  const [autoSeed, setAutoSeed] = useState(true);
  const [seed, setSeed] = useState("1");
  const [maxTick, setMaxTick] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function onStart(event) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      const body = {
        name: name.trim() || "świat",
        organism_count: count,
      };
      if (!autoSeed) {
        body.seed = Number(seed);
      }
      if (maxTick !== "" && Number(maxTick) >= 1) {
        body.max_tick = Number(maxTick);
      }
      const response = await fetch(`${API_BASE}/api/worlds`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      if (!response.ok) {
        throw new Error("nie udało się utworzyć świata");
      }
      const created = await response.json();
      navigate(`/world/${created.id}`);
    } catch (err) {
      setError(err.message || "backend nie odpowiada");
      setBusy(false);
    }
  }

  return (
    <main className="shell start">
      <h1>UNKNOWN</h1>
      <p>Jedyne miejsce sprawczości. Potem tylko się patrzy.</p>
      <form className="start-form" onSubmit={onStart}>
        <label>
          nazwa
          <input
            type="text"
            value={name}
            onChange={(event) => setName(event.target.value)}
            maxLength={40}
          />
        </label>
        <label>
          organizmy: {count}
          <input
            type="range"
            min="1"
            max="20"
            value={count}
            onChange={(event) => setCount(Number(event.target.value))}
          />
        </label>
        <label className="check">
          <input
            type="checkbox"
            checked={autoSeed}
            onChange={(event) => setAutoSeed(event.target.checked)}
          />
          seed automatyczny
        </label>
        {autoSeed ? null : (
          <label>
            seed
            <input
              type="number"
              value={seed}
              onChange={(event) => setSeed(event.target.value)}
              required
            />
          </label>
        )}
        <label>
          limit ticków
          <input
            type="number"
            min="1"
            placeholder="puste = aż do wymarcia"
            value={maxTick}
            onChange={(event) => setMaxTick(event.target.value)}
          />
        </label>
        {error ? <p className="start-error">{error}</p> : null}
        <button type="submit" disabled={busy}>
          {busy ? "tworzę…" : "START"}
        </button>
      </form>
    </main>
  );
}
