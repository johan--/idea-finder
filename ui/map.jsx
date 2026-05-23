/* map.jsx — Editorial column layout. Single scroll, one role per row. */

function SelfMap({ roles, persona, selectedId, onSelect }) {
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

Object.assign(window, { SelfMap });
