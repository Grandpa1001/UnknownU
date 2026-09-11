import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Inspector from "../world/Inspector.jsx";
import WorldViewport from "../world/WorldViewport.jsx";
import { useWorld } from "../world/useWorld.js";

function StatsPanel({ stats, name }) {
  const rows = [
    ["świat", name ?? "—"],
    ["tick", stats?.tick ?? "—"],
    ["status", stats?.status ?? "—"],
    ["populacja", stats?.population ?? "—"],
    ["pokolenie", stats?.generation ?? "—"],
    ["narodziny", stats?.births ?? "—"],
    ["zgony", stats?.deaths ?? "—"],
    ["jabłka", stats?.apples ?? "—"],
  ];
  return (
    <dl className="stats">
      {rows.map(([label, value]) => (
        <div key={label} className="stats-row">
          <dt>{label}</dt>
          <dd>{value}</dd>
        </div>
      ))}
    </dl>
  );
}

function EventLog({ events }) {
  const ref = useRef(null);
  useEffect(() => {
    const node = ref.current;
    if (node) {
      node.scrollTop = node.scrollHeight;
    }
  }, [events]);
  return (
    <ol className="event-log" ref={ref} aria-label="dziennik zdarzeń">
      {(events ?? []).map((line, index) => (
        <li key={`${index}-${line}`}>{line}</li>
      ))}
    </ol>
  );
}

export default function WorldPage() {
  const { id } = useParams();
  const { snapshot, live, error, loading } = useWorld(id);
  const [selectedId, setSelectedId] = useState(null);
  const stats = live?.stats;
  const events = live?.events ?? [];

  return (
    <main className="observatory">
      <header className="observatory-bar">
        <span className="observatory-title">UNKNOWN</span>
        <span className="observatory-meta">
          {snapshot?.name ?? "…"} · tick {stats?.tick ?? "—"} · {stats?.status ?? "ładowanie"}
        </span>
      </header>
      <div className="observatory-body">
        <section className="observatory-view" aria-label="świat">
          {loading ? <p className="viewport-msg">Ładowanie świata…</p> : null}
          {error === "missing" ? (
            <p className="viewport-msg">
              Nie ma świata {id}. Wróć do <Link to="/">START</Link>.
            </p>
          ) : null}
          {error === "error" ? <p className="viewport-msg">Backend nie odpowiada.</p> : null}
          {snapshot ? (
            <WorldViewport snapshot={snapshot} live={live} selectedId={selectedId} onSelect={setSelectedId} />
          ) : null}
        </section>
        <aside className="observatory-side">
          <StatsPanel stats={stats} name={snapshot?.name} />
          <Inspector organismId={selectedId} live={live} onClose={() => setSelectedId(null)} />
          <h2>dziennik</h2>
          <EventLog events={events} />
        </aside>
      </div>
    </main>
  );
}
