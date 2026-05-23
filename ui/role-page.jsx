/* role-page.jsx — Role detail as a standalone page (not a slide-in drawer).
   Layered editorial structure: Goal → Practice → Problems (personal +
   researched) → Narratives → Open Questions. Each section is collapsible. */

function RolePage({ role, onBack, onPrev, onNext, accent }) {
  // expanded: which sections are open. Defaults: first three open, deeper
  // layers collapsed.
  const [open, setOpen] = React.useState({
    goal: true,
    practice: true,
    problems: true,
    narratives: false,
    questions: false
  });

  // Reset to default-open pattern whenever the user navigates to a new role.
  React.useEffect(() => {
    if (!role) return;
    setOpen({ goal: true, practice: true, problems: true, narratives: false, questions: false });
    // Scroll to top of the page so the new role's header is visible.
    window.scrollTo({ top: 0, behavior: "instant" });
  }, [role?.id]);

  if (!role) return null;
  const toggle = (k) => setOpen((s) => ({ ...s, [k]: !s[k] }));

  return (
    <article className="role-page" aria-label={`${role.label} detail`}>
      <div className="role-page-bar">
        <button className="role-page-back" onClick={onBack}>
          <span aria-hidden="true">←</span>
          <span>Back to self-map</span>
        </button>
        <div className="role-page-nav">
          {onPrev && (
            <button className="role-page-nav-btn" onClick={onPrev} aria-label="Previous role">
              <span aria-hidden="true">←</span>
              <span>Previous</span>
            </button>
          )}
          {onNext && (
            <button className="role-page-nav-btn" onClick={onNext} aria-label="Next role">
              <span>Next</span>
              <span aria-hidden="true">→</span>
            </button>
          )}
        </div>
      </div>

      <header className="role-page-head">
        <div className="role-page-eyebrow">
          <span className="role-page-eyebrow-tag">{role.intensity}</span>
          <span className="role-page-eyebrow-sep" aria-hidden="true">/</span>
          <span>Role</span>
        </div>
        <h1 className="role-page-title">{role.label}</h1>
        <div className="role-page-subtitle">{role.sublabel}</div>
      </header>

      <div className="role-page-body">
        <Section
          k="goal"
          open={open.goal}
          onToggle={toggle}
          label="What success looks like"
          counter="">
          <p className="role-page-goal">{role.goal}</p>
        </Section>

        <Section
          k="practice"
          open={open.practice}
          onToggle={toggle}
          label="How it is achieved now"
          counter={role.practice.length}>
          <ol className="role-page-list">
            {role.practice.map((p, i) =>
              <li key={i}>
                <span className="role-page-list-marker">{String(i + 1).padStart(2, "0")}</span>
                <span>{p}</span>
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
          <div className="role-page-subhead">Said in the interview</div>
          <ul className="role-page-quotes">
            {role.problems.personal.map((p, i) =>
              <li key={i} className="role-page-quote">
                <span className="role-page-quote-mark" aria-hidden="true">“</span>
                {p}
              </li>
            )}
          </ul>

          <div className="role-page-subhead role-page-subhead-spaced">Found in the field</div>
          <ul className="role-page-cites">
            {role.problems.researched.map((c, i) =>
              <li key={i} className="role-page-cite">
                <span className="role-page-cite-text">{c.text}</span>
                <span className="role-page-cite-source">— {c.source}</span>
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
          <ul className="role-page-narratives">
            {role.narratives.map((n, i) =>
              <li key={i} style={{ ["--accent"]: accent }}>
                <span className="role-page-narratives-pill">new</span>
                <span>{n}</span>
              </li>
            )}
          </ul>
          <p className="role-page-narratives-note">
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
          <ul className="role-page-questions">
            {role.openQuestions.map((q, i) =>
              <li key={i}>
                <span className="role-page-questions-mark" aria-hidden="true">?</span>
                {q}
              </li>
            )}
          </ul>
        </Section>
      </div>

      <footer className="role-page-foot">
        <button className="role-page-back" onClick={onBack}>
          <span aria-hidden="true">←</span>
          <span>Back to self-map</span>
        </button>
        <div className="role-page-nav">
          {onPrev && (
            <button className="role-page-nav-btn" onClick={onPrev}>
              <span aria-hidden="true">←</span>
              <span>Previous</span>
            </button>
          )}
          {onNext && (
            <button className="role-page-nav-btn" onClick={onNext}>
              <span>Next</span>
              <span aria-hidden="true">→</span>
            </button>
          )}
        </div>
      </footer>
    </article>
  );
}

function Section({ k, open, onToggle, label, counter, children }) {
  return (
    <section className={`role-page-section ${open ? "is-open" : ""}`}>
      <button className="role-page-section-head" onClick={() => onToggle(k)} aria-expanded={open}>
        <span className="role-page-section-label">{label}</span>
        <span className="role-page-section-meta">
          {counter !== "" && counter != null &&
            <span className="role-page-section-count">{String(counter).padStart(2, "0")}</span>
          }
          <span className={`role-page-section-chevron ${open ? "is-open" : ""}`} aria-hidden="true">
            ▾
          </span>
        </span>
      </button>
      <div className="role-page-section-body" hidden={!open}>
        {children}
      </div>
    </section>
  );
}

Object.assign(window, { RolePage });
