/* tabs.jsx — Network, Opportunities, Open Questions. */

/* ── NETWORK ────────────────────────────────────────────────────────────── */

function NetworkTab({ persona, network, roles, onSelectRole }) {
  const roleLabel = (id) => roles.find((r) => r.id === id)?.label ?? id;
  return (
    <div className="tab-wrap network">
      <header className="tab-head">
        <div className="tab-eyebrow">02 / Network</div>
        <h2 className="tab-title">Six people who would pick up at three in the morning.</h2>
        <p className="tab-lede">
          The close circle, drawn as {persona.name} described it — distance one is the
          inner ring, distance two the next out. Hover a friend to see which
          of their roles they touch.
        </p>
      </header>

      <ol className="network-list">
        {network.map((f) =>
        <li key={f.id} className="network-row">
            <div className="network-row-left">
              <div className="network-row-name">{f.name}</div>
              <div className="network-row-rel">{f.relation}</div>
            </div>
            <div className="network-row-mid">
              <div className="network-row-roles">
                {f.roles.map((r, i) =>
              <span key={i} className="network-role-chip">{r}</span>
              )}
              </div>
              <p className="network-row-note">{f.note}</p>
            </div>
            <div className="network-row-right">
              <div className="network-row-overlap-label">Touches</div>
              <div className="network-row-overlap">
                {f.overlapsWith.map((id, i) =>
              <button
                key={i}
                className="network-overlap-link"
                onClick={() => onSelectRole(id)}>
                
                    {roleLabel(id)}
                  </button>
              )}
              </div>
            </div>
          </li>
        )}
      </ol>
    </div>);

}

/* ── OPPORTUNITIES ──────────────────────────────────────────────────────── */

function OpportunitiesTab({ roles, accent }) {
  // Filter: 'all' or a specific role id.
  const [filter, setFilter] = React.useState("all");
  const visibleRoles = filter === "all" ? roles : roles.filter((r) => r.id === filter);

  return (
    <div className="tab-wrap opportunities">
      <header className="tab-head">
        <div className="tab-eyebrow">03 / Opportunities lens</div>
        <h2 className="tab-title">
          Where the problems and the new shapes are looking at each other.
        </h2>
        <p className="tab-lede">
          A lens — not a list of solutions. Each row pairs a real problem with
          a narrative already moving through the field. The connection is for
          you to make. The map will not draw it for you.
        </p>
      </header>

      <div className="opp-filter">
        <span className="opp-filter-label">Filter by role</span>
        <div className="opp-filter-pills">
          <button
            className={`opp-filter-pill ${filter === "all" ? "is-on" : ""}`}
            onClick={() => setFilter("all")}>
            
            All ({roles.length})
          </button>
          {roles.map((r) =>
          <button
            key={r.id}
            className={`opp-filter-pill ${filter === r.id ? "is-on" : ""}`}
            onClick={() => setFilter(r.id)}>
            
              {r.label}
            </button>
          )}
        </div>
      </div>

      <div className="opp-grid">
        {visibleRoles.map((r) => {
          // For each role, build pairings. We pair problems and narratives by
          // index so the column lengths line up cleanly. Extras land in their
          // own row alone.
          const probs = [
          ...r.problems.personal.map((t) => ({ kind: "personal", text: t })),
          ...r.problems.researched.map((c) => ({ kind: "researched", text: c.text, source: c.source }))];

          const narrs = r.narratives;
          const rows = Math.max(probs.length, narrs.length);
          return (
            <section key={r.id} className="opp-block">
              <header className="opp-block-head">
                <div className="opp-block-eyebrow">Role</div>
                <h3 className="opp-block-title">{r.label}</h3>
              </header>
              <div className="opp-block-col-heads">
                <div>Problem</div>
                <div className="opp-block-col-arrow" style={{ ["--accent"]: accent }} aria-hidden="true">↔</div>
                <div>Narrative in motion</div>
              </div>
              <ol className="opp-rows">
                {Array.from({ length: rows }).map((_, i) => {
                  const p = probs[i];
                  const n = narrs[i];
                  return (
                    <li key={i} className="opp-row">
                      <div className="opp-row-problem">
                        {p ?
                        <>
                            <span className={`opp-row-tag opp-row-tag-${p.kind}`}>
                              {p.kind === "personal" ? "personal" : "researched"}
                            </span>
                            <span className="opp-row-text">{p.text}</span>
                            {p.source &&
                          <span className="opp-row-source">— {p.source}</span>
                          }
                          </> :

                        <span className="opp-row-empty">—</span>
                        }
                      </div>
                      <div className="opp-row-link" aria-hidden="true">
                        <span className="opp-row-link-line" style={{ ["--accent"]: accent }} />
                      </div>
                      <div className="opp-row-narrative">
                        {n ?
                        <>
                            <span className="opp-row-tag opp-row-tag-narrative">new</span>
                            <span className="opp-row-text">{n}</span>
                          </> :

                        <span className="opp-row-empty">—</span>
                        }
                      </div>
                    </li>);

                })}
              </ol>
            </section>);

        })}
      </div>
    </div>);

}

/* ── OPEN QUESTIONS ─────────────────────────────────────────────────────── */

function QuestionsTab({ roles, answers, onAnswer, onSkip, accent }) {
  const all = roles.flatMap((r) =>
  r.openQuestions.map((q, i) => ({
    key: `${r.id}-${i}`,
    roleId: r.id,
    roleLabel: r.label,
    text: q
  }))
  );

  const unanswered = all.filter((q) => !answers[q.key]);
  const answered = all.filter((q) => answers[q.key]?.kind === "answer");
  const skipped = all.filter((q) => answers[q.key]?.kind === "skip");

  return (
    <div className="tab-wrap questions">
      <header className="tab-head">
        <div className="tab-eyebrow">04 / Open questions</div>
        <h2 className="tab-title">
          {unanswered.length} sentences {PERSONA.name} began and did not finish.
        </h2>
        <p className="tab-lede">
          The map is sharper when the holes in it are named. Answer one,
          dismiss one, or leave them open. None of them are urgent. All of
          them are useful.
        </p>
        <div className="questions-stats">
          <span><b>{unanswered.length}</b> open</span>
          <span><b>{answered.length}</b> answered</span>
          <span><b>{skipped.length}</b> set aside</span>
        </div>
      </header>

      {unanswered.length > 0 &&
      <ol className="q-list">
          {unanswered.map((q) =>
        <QuestionItem
          key={q.key}
          q={q}
          onAnswer={(text) => onAnswer(q.key, text)}
          onSkip={() => onSkip(q.key)}
          accent={accent} />

        )}
        </ol>
      }

      {answered.length > 0 &&
      <details className="q-archive">
          <summary>Answered ({answered.length})</summary>
          <ol className="q-archive-list">
            {answered.map((q) =>
          <li key={q.key} className="q-archive-row">
                <div className="q-archive-role">{q.roleLabel}</div>
                <div>
                  <div className="q-archive-q">{q.text}</div>
                  <div className="q-archive-a">{answers[q.key].text}</div>
                </div>
              </li>
          )}
          </ol>
        </details>
      }

      {skipped.length > 0 &&
      <details className="q-archive">
          <summary>Set aside ({skipped.length})</summary>
          <ol className="q-archive-list">
            {skipped.map((q) =>
          <li key={q.key} className="q-archive-row">
                <div className="q-archive-role">{q.roleLabel}</div>
                <div className="q-archive-q">{q.text}</div>
              </li>
          )}
          </ol>
        </details>
      }
    </div>);

}

function QuestionItem({ q, onAnswer, onSkip, accent }) {
  const [drafting, setDrafting] = React.useState(false);
  const [text, setText] = React.useState("");
  const submit = () => {
    if (!text.trim()) return;
    onAnswer(text.trim());
  };
  return (
    <li className="q-item">
      <div className="q-item-role">{q.roleLabel}</div>
      <div className="q-item-text">{q.text}</div>
      {!drafting &&
      <div className="q-item-actions">
          <button
          className="q-item-btn"
          style={{ ["--accent"]: accent }}
          onClick={() => setDrafting(true)}>
          
            Answer
          </button>
          <button className="q-item-btn q-item-btn-ghost" onClick={onSkip}>
            Set aside
          </button>
        </div>
      }
      {drafting &&
      <div className="q-item-draft">
          <textarea
          placeholder="Write what comes to mind. A sentence is enough."
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={3}
          autoFocus />
        
          <div className="q-item-draft-actions">
            <button
            className="q-item-btn"
            style={{ ["--accent"]: accent }}
            onClick={submit}
            disabled={!text.trim()}>
            
              Save
            </button>
            <button
            className="q-item-btn q-item-btn-ghost"
            onClick={() => {setDrafting(false);setText("");}}>
            
              Cancel
            </button>
          </div>
        </div>
      }
    </li>);

}

/* ── DISCOVERY DOC TAB ──────────────────────────────────────────────────── */

function DiscoveryDocTab({ persona, doc }) {
  return (
    <div className="tab-wrap discovery">
      <header className="tab-head">
        <div className="tab-eyebrow">05 / Full discovery doc</div>
        <h2 className="tab-title" style={{ fontFamily: "Times" }}>
          The interview the map was built from
        </h2>
        <div className="docmodal-meta" style={{ marginTop: 12 }}>
          <span>{persona.name}</span>
          <span aria-hidden="true">·</span>
          <span>{persona.interviewedOn}</span>
          <span aria-hidden="true">·</span>
          <span>{persona.interviewLength}</span>
        </div>
        <p className="tab-lede" style={{ marginTop: 16 }}>
          Raw — every question asked, every note taken, research pasted in full.
          The visual map shows only the clean takeaways; this is the source of truth.
        </p>
      </header>
      <pre className="docmodal-body" style={{ padding: 0 }}>{doc}</pre>
    </div>
  );
}

/* ── DISCOVERY DOC VIEWER (modal, opened from Tweaks) ───────────────────── */

function DiscoveryDoc({ open, onClose, persona, doc }) {
  React.useEffect(() => {
    if (!open) return;
    const onKey = (e) => {if (e.key === "Escape") onClose();};
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div className="docmodal" role="dialog" aria-modal="true">
      <div className="docmodal-scrim" onClick={onClose} />
      <article className="docmodal-sheet">
        <header className="docmodal-head">
          <div className="docmodal-eyebrow">Source · Discovery Document</div>
          <h2 className="docmodal-title" style={{ fontFamily: "Times" }}>The interview the map was built from</h2>
          <div className="docmodal-meta">
            <span>{persona.name}</span>
            <span aria-hidden="true">·</span>
            <span>{persona.interviewedOn}</span>
            <span aria-hidden="true">·</span>
            <span>{persona.interviewLength}</span>
          </div>
          <button className="docmodal-close" onClick={onClose} aria-label="Close document">×</button>
        </header>
        <pre className="docmodal-body">{doc}</pre>
      </article>
    </div>);

}

Object.assign(window, { NetworkTab, OpportunitiesTab, QuestionsTab, DiscoveryDoc, DiscoveryDocTab });