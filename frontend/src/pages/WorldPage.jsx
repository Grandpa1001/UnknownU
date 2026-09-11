import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";
import Inspector from "../world/Inspector.jsx";
import WorldViewport from "../world/WorldViewport.jsx";
import { loadTags, saveTags } from "../world/tags.js";
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

function TaggedList({ ids, organisms, selectedId, onSelect, ready }) {
  const living = new Set((organisms ?? []).map((item) => item.id));
  return (
    <section className="tagged" aria-label="otagowani">
      <h2>obserwowani</h2>
      {ids.length === 0 ? (
        <p className="tagged-empty">nikogo jeszcze nie otagowano</p>
      ) : (
        <ul className="tagged-list">
          {ids.map((orgId) => (
            <li key={orgId}>
              <button
                type="button"
                className={selectedId === orgId ? "is-selected" : ""}
                onClick={() => onSelect(orgId)}
              >
                {orgId}
                {ready && !living.has(orgId) ? " · martwy" : ""}
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function EndBanner({ status, stats }) {
  if (status !== "extinct" && status !== "finished") {
    return null;
  }
  const extinct = status === "extinct";
  return (
    <div className="end-overlay" role="status" data-testid="end-overlay">
      <h2>{extinct ? "wymarcie" : "koniec biegu"}</h2>
      <p>
        {extinct
          ? "Nikt już nie żyje. Możesz nadal oglądać archiwum."
          : "Osiągnięto limit ticków. Archiwum zostaje."}
      </p>
      <p className="end-overlay-meta">
        tick {stats?.tick ?? "—"} · zgony {stats?.deaths ?? "—"} · pokolenie {stats?.generation ?? "—"}
      </p>
      <Link to="/">nowy świat</Link>
    </div>
  );
}

export default function WorldPage() {
  const { id } = useParams();
  const { snapshot, live, error, loading } = useWorld(id);
  const [selectedId, setSelectedId] = useState(null);
  const [taggedIds, setTaggedIds] = useState(() => loadTags(id));
  const [followId, setFollowId] = useState(null);
  const [notice, setNotice] = useState("");
  const skipTagSave = useRef(true);
  const stats = live?.stats;
  const events = live?.events ?? [];
  const status = live?.status ?? snapshot?.status;

  useEffect(() => {
    setSelectedId(null);
    setFollowId(null);
    setNotice("");
    skipTagSave.current = true;
    setTaggedIds(loadTags(id));
  }, [id]);

  useEffect(() => {
    if (skipTagSave.current) {
      skipTagSave.current = false;
      return;
    }
    saveTags(id, taggedIds);
  }, [id, taggedIds]);

  useEffect(() => {
    if (!followId || !live) {
      return;
    }
    const alive = (live.organisms ?? []).some((item) => item.id === followId);
    if (!alive) {
      setFollowId(null);
      setNotice(`śledzony ${followId} umarł`);
    }
  }, [live, followId]);

  function toggleTag(organismId) {
    setTaggedIds((current) =>
      current.includes(organismId) ? current.filter((item) => item !== organismId) : [...current, organismId],
    );
  }

  function onFollowLost(reason) {
    if (reason === "camera") {
      setFollowId(null);
    }
  }

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
            <WorldViewport
              snapshot={snapshot}
              live={live}
              selectedId={selectedId}
              taggedIds={taggedIds}
              followId={followId}
              onSelect={setSelectedId}
              onFollowLost={onFollowLost}
            />
          ) : null}
          <EndBanner status={status} stats={stats} />
          {notice ? (
            <p className="follow-notice" role="status">
              {notice}
            </p>
          ) : null}
        </section>
        <aside className="observatory-side">
          <StatsPanel stats={stats} name={snapshot?.name} />
          <TaggedList
            ids={taggedIds}
            organisms={live?.organisms}
            selectedId={selectedId}
            onSelect={setSelectedId}
            ready={Boolean(live)}
          />
          <Inspector
            organismId={selectedId}
            live={live}
            tagged={selectedId ? taggedIds.includes(selectedId) : false}
            following={Boolean(selectedId && followId === selectedId)}
            onClose={() => setSelectedId(null)}
            onToggleTag={() => selectedId && toggleTag(selectedId)}
            onFollow={() => {
              if (!selectedId) {
                return;
              }
              setNotice("");
              setFollowId((current) => (current === selectedId ? null : selectedId));
            }}
          />
          <h2>dziennik</h2>
          <EventLog events={events} />
        </aside>
      </div>
    </main>
  );
}
