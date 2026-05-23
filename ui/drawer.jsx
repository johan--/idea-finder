/* drawer.jsx — Role detail. Slides in from the right when a role is selected.
   Layered editorial structure: Goal → Practice → Problems (personal +
   researched) → Narratives → Open Questions. Each layer is collapsible. */

function RoleDrawer({ role, onClose, accent }) {
  // expanded: which sections are open. By default the first three are open
  // ("the most important information first") and the deeper layers are
  // collapsed so the drawer doesn't feel crowded.
  const [open, setOpen] = React.useState({
    goal: true,
    practice: true,
    problems: true,
    narratives: false,
    questions: false
  });

  // Keep state synced with role changes — opening a fresh role re-applies the
  // default-open pattern. Otherwise switching from one role's drawer to the
  // next can show all sections collapsed if the previous user had closed them.
  React.useEffect(() => {
    if (!role) return;
    setOpen({ goal: true, practice: true, problems: true, narratives: false, questions: false });
  }, [role?.id]);

  if (!role) return null;
  const toggle = (k) => setOpen((s) => ({ ...s, [k]: !s[k] }));

  return (
    <aside className="drawer" role="dialog" aria-label={`${role.label} detail`}>
      <header className="drawer-head">
        <div className="drawer-eyebrow">
          <span className="drawer-eyebrow-tag">{role.intensity}</span>
          <span className="drawer-eyebrow-sep" aria-hidden="true">/</span>
          <span>Role</span>
        </div>
        <h2 className="drawer-title">{role.label}</h2>
        <div className="drawer-subtitle">{role.sublabel}</div>
        <button className="drawer-close" onClick={onClose} aria-label="Close detail">
          <span aria-hidden="true">×</span>
        </button>
      </header>

      <div className="drawer-body">
        <Section
          k="goal"
          open={open.goal}
          onToggle={toggle}
          label="What success looks like"
          counter="">
          
          <p className="drawer-goal">{role.goal}</p>
        </Section>

        <Section
          k="practice"
          open={open.practice}
          onToggle={toggle}
          label="How it is achieved now"
          counter={role.practice.length}>
          
          <ol className="drawer-list">
            {role.practice.map((p, i) =>
            <li key={i}>
                <span className="drawer-list-marker">{String(i + 1).padStart(2, "0")}</span>
                <span style={{ fontSize: "23px" }}>{p}</span>
              </li>
            )}
          </ol>
        </Section>

        <Section
          k="problems"
          open={open.problems}
          onToggle={toggle}
          label="Problems"
          counter={role.problems.personal.length + role.problems.researched.length}>
          
          <div className="drawer-subhead">Said in the interview</div>
          <ul className="drawer-quotes">
            {role.problems.personal.map((p, i) =>
            <li key={i} className="drawer-quote">
                <span className="drawer-quote-mark" aria-hidden="true">“</span>
                {p}
              </li>
            )}
          </ul>

          <div className="drawer-subhead drawer-subhead-spaced">Found in the field</div>
          <ul className="drawer-cites">
            {role.problems.researched.map((c, i) =>
            <li key={i} className="drawer-cite">
                <span className="drawer-cite-text" style={{ fontSize: "23px" }}>{c.text}</span>
                <span className="drawer-cite-source">— {c.source}</span>
              </li>
            )}
          </ul>
        </Section>

        <Section
          k="narratives"
          open={open.narratives}
          onToggle={toggle}
          label="Narratives in the air"
          counter={role.narratives.length}>
          
          <ul className="drawer-narratives">
            {role.narratives.map((n, i) =>
            <li key={i} style={{ ["--accent"]: accent }}>
                <span className="drawer-narratives-pill">new</span>
                <span>{n}</span>
              </li>
            )}
          </ul>
          <p className="drawer-narratives-note">
            Surfaced from current writing and product launches. These are
            shapes the future is taking — not solutions. The solutions are
            yours to draw.
          </p>
        </Section>

        <Section
          k="questions"
          open={open.questions}
          onToggle={toggle}
          label="Still open"
          counter={role.openQuestions.length}>
          
          <ul className="drawer-questions">
            {role.openQuestions.map((q, i) =>
            <li key={i}>
                <span className="drawer-questions-mark" aria-hidden="true">?</span>
                {q}
              </li>
            )}
          </ul>
        </Section>
      </div>
    </aside>);

}

function Section({ k, open, onToggle, label, counter, children }) {
  return (
    <section className={`drawer-section ${open ? "is-open" : ""}`}>
      <button className="drawer-section-head" onClick={() => onToggle(k)} aria-expanded={open}>
        <span className="drawer-section-label" style={{ fontFamily: "\"Open Sans\"", fontSize: "35px" }}>{label}</span>
        <span className="drawer-section-meta">
          {counter !== "" && counter != null &&
          <span className="drawer-section-count">{String(counter).padStart(2, "0")}</span>
          }
          <span className={`drawer-section-chevron ${open ? "is-open" : ""}`} aria-hidden="true">
            ▾
          </span>
        </span>
      </button>
      <div className="drawer-section-body" hidden={!open}>
        {children}
      </div>
    </section>);

}

Object.assign(window, { RoleDrawer });