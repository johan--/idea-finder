/* map.jsx — three layout variations of the self-map:
   - orbital:   concentric rings around the center (default)
   - column:    editorial single-column list
   - constellation: hand-placed positions linked by hairlines
*/

function SelfMap({ layout, roles, persona, selectedId, onSelect, accent }) {
  if (layout === "column") {
    return <ColumnMap roles={roles} persona={persona} selectedId={selectedId} onSelect={onSelect} />;
  }
  if (layout === "constellation") {
    return <ConstellationMap roles={roles} persona={persona} selectedId={selectedId} onSelect={onSelect} accent={accent} />;
  }
  return <OrbitalMap roles={roles} persona={persona} selectedId={selectedId} onSelect={onSelect} accent={accent} />;
}

/* ── 1. ORBITAL ─────────────────────────────────────────────────────────── */

function OrbitalMap({ roles, persona, selectedId, onSelect, accent }) {
  // Radii expressed as percentages of container — keeps everything in sync
  // when the container scales for smaller viewports.
  const INNER_PCT = 26.5;
  const OUTER_PCT = 41.5;
  return (
    <div className="orbital">
      {/* hairline rings */}
      <svg className="orbital-rings" viewBox="-50 -50 100 100" aria-hidden="true" preserveAspectRatio="none">
        <circle cx="0" cy="0" r={INNER_PCT} />
        <circle cx="0" cy="0" r={OUTER_PCT} />
      </svg>

      {/* center self */}
      <div className="orbital-center">
        <div className="orbital-center-name">{persona.name}</div>
        <div className="orbital-center-meta">
          <span>age {persona.age}</span>
        </div>
        <div className="orbital-center-loc">{persona.location}</div>
      </div>

      {/* role nodes */}
      {roles.map((r) => {
        const radiusPct = r.orbit === 1 ? INNER_PCT : OUTER_PCT;
        const rad = (r.angle * Math.PI) / 180;
        const xPct = Math.cos(rad) * radiusPct;
        const yPct = -Math.sin(rad) * radiusPct;
        const active = selectedId === r.id;
        const dim = selectedId && !active;
        return (
          <button
            key={r.id}
            className={`orbital-node ${active ? "is-active" : ""} ${dim ? "is-dim" : ""}`}
            style={{
              left: `${50 + xPct}%`,
              top: `${50 + yPct}%`,
              ["--accent"]: accent,
            }}
            onClick={() => onSelect(r.id)}
            aria-label={`Open ${r.label}`}
          >
            <span className="orbital-node-label">{r.shortLabel || r.label}</span>
          </button>
        );
      })}

      {/* epigraph floats below the rings */}
      <blockquote className="orbital-epigraph">
        &ldquo;{persona.epigraph}&rdquo;
      </blockquote>
    </div>
  );
}

/* ── 2. EDITORIAL COLUMN ─────────────────────────────────────────────────── */

function ColumnMap({ roles, persona, selectedId, onSelect }) {
  return (
    <div className="column-map">
      <header className="column-map-head">
        <div className="column-map-eyebrow">A self-map of</div>
        <h1 className="column-map-name">{persona.name}</h1>
        <blockquote className="column-map-epigraph">
          &ldquo;{persona.epigraph}&rdquo;
        </blockquote>
      </header>

      <ol className="column-map-list">
        {roles.map((r, i) => {
          const active = selectedId === r.id;
          return (
            <li key={r.id} className={active ? "column-row is-active" : "column-row"}>
              <button onClick={() => onSelect(r.id)} className="column-row-btn">
                <span className="column-row-num">{String(i + 1).padStart(2, "0")}</span>
                <div className="column-row-text">
                  <div className="column-row-label">{r.label}</div>
                  <div className="column-row-sub">{r.sublabel}</div>
                </div>
                <span className="column-row-goal">{r.goal}</span>
                <span className="column-row-arrow" aria-hidden="true">→</span>
              </button>
            </li>
          );
        })}
      </ol>
    </div>
  );
}

/* ── 3. CONSTELLATION ───────────────────────────────────────────────────── */

// Hand-placed (x%, y%) so the layout has the asymmetry of a real constellation.
const CONSTELLATION_POSITIONS = {
  father:        { x: 32, y: 30 },
  designer:      { x: 68, y: 26 },
  trader:        { x: 78, y: 56 },
  motorcyclist:  { x: 60, y: 78 },
  cyclist:       { x: 28, y: 70 },
  snowboarder:   { x: 14, y: 46 },
};
const CONSTELLATION_SELF = { x: 50, y: 50 };

function ConstellationMap({ roles, persona, selectedId, onSelect, accent }) {
  return (
    <div className="constellation">
      <svg className="constellation-lines" viewBox="0 0 100 100" preserveAspectRatio="none" aria-hidden="true">
        {roles.map((r) => {
          const p = CONSTELLATION_POSITIONS[r.id];
          if (!p) return null;
          const active = selectedId === r.id;
          return (
            <line
              key={r.id}
              x1={CONSTELLATION_SELF.x}
              y1={CONSTELLATION_SELF.y}
              x2={p.x}
              y2={p.y}
              stroke={active ? accent : "currentColor"}
              strokeWidth={active ? 0.18 : 0.08}
              strokeDasharray={active ? "0" : "0.4 0.6"}
              vectorEffect="non-scaling-stroke"
              opacity={selectedId && !active ? 0.25 : 0.7}
            />
          );
        })}
      </svg>

      <div
        className="constellation-self"
        style={{ left: `${CONSTELLATION_SELF.x}%`, top: `${CONSTELLATION_SELF.y}%` }}
      >
        <div className="constellation-self-name">{persona.name}</div>
        <div className="constellation-self-meta">age {persona.age}</div>
      </div>

      {roles.map((r) => {
        const p = CONSTELLATION_POSITIONS[r.id];
        if (!p) return null;
        const active = selectedId === r.id;
        const dim = selectedId && !active;
        return (
          <button
            key={r.id}
            className={`constellation-node ${active ? "is-active" : ""} ${dim ? "is-dim" : ""}`}
            style={{ left: `${p.x}%`, top: `${p.y}%`, ["--accent"]: accent }}
            onClick={() => onSelect(r.id)}
            aria-label={`Open ${r.label}`}
          >
            <span className="constellation-node-dot" aria-hidden="true" />
            <span className="constellation-node-label">{r.label}</span>
            <span className="constellation-node-sub">{r.sublabel}</span>
          </button>
        );
      })}

      <div className="constellation-epigraph">
        &ldquo;{persona.epigraph}&rdquo;
      </div>
    </div>
  );
}

Object.assign(window, { SelfMap });
