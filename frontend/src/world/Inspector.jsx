import { useEffect, useState } from "react";
import { API_BASE } from "./config.js";

function fmt(value) {
  if (typeof value === "number") {
    return Number.isInteger(value) ? String(value) : value.toFixed(3);
  }
  return value ?? "—";
}

export default function Inspector({ organismId, live, onClose }) {
  const [file, setFile] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!organismId) {
      setFile(null);
      setError("");
      return undefined;
    }
    let cancelled = false;
    setError("");
    fetch(`${API_BASE}/api/organisms/${organismId}`)
      .then((response) => {
        if (response.status === 404) {
          throw new Error("nie ma już tego organizmu");
        }
        if (!response.ok) {
          throw new Error("nie udało się pobrać kartoteki");
        }
        return response.json();
      })
      .then((data) => {
        if (!cancelled) {
          setFile(data);
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setFile(null);
          setError(err.message);
        }
      });
    return () => {
      cancelled = true;
    };
  }, [organismId]);

  if (!organismId) {
    return null;
  }

  const liveBody = live?.organisms?.find((item) => item.id === organismId);
  const body = { ...file, ...liveBody };
  const traits = file?.genome?.traits ?? {};
  const program = file?.genome?.program ?? [];
  const children = file?.children ?? [];

  return (
    <section className="inspector" aria-label="kartoteka organizmu">
      <header className="inspector-head">
        <h2>kartoteka</h2>
        <button type="button" className="inspector-close" onClick={onClose} aria-label="zamknij kartotekę">
          ×
        </button>
      </header>
      {error ? <p className="inspector-error">{error}</p> : null}
      {!file && !error ? <p>wczytuję…</p> : null}
      {file ? (
        <dl className="inspector-dl">
          <div><dt>id</dt><dd>{body.id}</dd></div>
          <div><dt>cecha</dt><dd>{body.feature ?? file.feature}</dd></div>
          <div><dt>energia</dt><dd>{fmt(body.energy)}</dd></div>
          <div><dt>wiek</dt><dd>{fmt(body.age)}</dd></div>
          <div><dt>pokolenie</dt><dd>{fmt(body.generation)}</dd></div>
          <div><dt>rodzic</dt><dd>{body.parent_id ?? "—"}</dd></div>
          <div><dt>dzieci</dt><dd>{children.length ? children.join(", ") : "—"}</dd></div>
          <div><dt>akcja</dt><dd>{body.last_action ?? "—"}</dd></div>
          <div><dt>myśli</dt><dd>{body.is_thinking ? "tak" : "nie"}</dd></div>
          <div><dt>bravery</dt><dd>{fmt(traits.bravery)}</dd></div>
          <div><dt>stress</dt><dd>{fmt(traits.stress)}</dd></div>
          <div><dt>stupidity</dt><dd>{fmt(traits.stupidity)}</dd></div>
          <div><dt>głód</dt><dd>{fmt(traits.hunger_threshold)}</dd></div>
          <div><dt>rozród</dt><dd>{fmt(traits.reproduction_threshold)}</dd></div>
        </dl>
      ) : null}
      {program.length ? (
        <ol className="inspector-program">
          {program.map((step) => (
            <li key={step}>{step}</li>
          ))}
        </ol>
      ) : null}
    </section>
  );
}
