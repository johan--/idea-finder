#!/usr/bin/env python3
"""
Problem Finder — Discovery Document HTML Renderer
Reads ~/problem-finder/discovery.md and generates discovery.html
Usage: python3 render.py [input.md] [output.html]
"""

import sys
import re
from pathlib import Path
from datetime import datetime

def parse_document(text):
    """Parse discovery.md into structured sections."""
    data = {
        "meta": {"version": "1", "date": "", "round": "1"},
        "profile": {},
        "education": [],
        "work_history": [],
        "relationships": {},
        "hobbies": [],
        "consumer_frustrations": [],
        "active_problems": [],
        "roles": [],
        "role_research": {},
        "tech_breakthroughs": [],
        "candidate_problems": [],
        "interview_data": [],
        "insights": [],
        "open_questions": [],
    }

    # Extract meta from first line
    meta_match = re.search(r'version:\s*(\d+)\s*\|\s*date:\s*([^\|]+)\s*\|\s*round:\s*(\d+)', text)
    if meta_match:
        data["meta"]["version"] = meta_match.group(1).strip()
        data["meta"]["date"] = meta_match.group(2).strip()
        data["meta"]["round"] = meta_match.group(3).strip()

    def get_section(heading, content):
        pattern = rf'## {re.escape(heading)}\s*\n(.*?)(?=\n## |\Z)'
        match = re.search(pattern, content, re.DOTALL)
        return match.group(1).strip() if match else ""

    def get_bullets(section_text):
        lines = []
        for line in section_text.split('\n'):
            line = line.strip()
            if line.startswith('- ') or line.startswith('* '):
                lines.append(line[2:].strip())
            elif line.startswith('• '):
                lines.append(line[2:].strip())
        return lines

    # Profile
    profile_text = get_section("PROFILE", text)
    for line in profile_text.split('\n'):
        if ':' in line:
            key, _, val = line.partition(':')
            k = key.strip().lower().replace(' ', '_')
            v = val.strip()
            if v and k:
                data["profile"][k] = v

    # Education
    edu_text = get_section("EDUCATION", text)
    data["education"] = get_bullets(edu_text) or ([edu_text.strip()] if edu_text.strip() else [])

    # Work history
    work_text = get_section("WORK HISTORY", text)
    data["work_history"] = get_bullets(work_text) or ([work_text.strip()] if work_text.strip() else [])

    # Relationships
    rel_text = get_section("RELATIONSHIPS", text)
    for line in rel_text.split('\n'):
        line = line.strip()
        if ':' in line and not line.startswith('-'):
            key, _, val = line.partition(':')
            data["relationships"][key.strip()] = val.strip()
    data["relationships"]["_bullets"] = get_bullets(rel_text)

    # Hobbies
    hobbies_text = get_section("HOBBIES AND INTERESTS", text)
    data["hobbies"] = get_bullets(hobbies_text) or ([hobbies_text.strip()] if hobbies_text.strip() else [])

    # Consumer frustrations
    frust_text = get_section("CONSUMER FRUSTRATIONS", text)
    data["consumer_frustrations"] = get_bullets(frust_text) or ([frust_text.strip()] if frust_text.strip() else [])

    # Active problems
    prob_text = get_section("ACTIVE PROBLEMS", text)
    data["active_problems"] = get_bullets(prob_text) or ([prob_text.strip()] if prob_text.strip() else [])

    # Roles list (parse markdown table)
    roles_text = get_section("ROLES LIST", text)
    for line in roles_text.split('\n'):
        line = line.strip()
        if line.startswith('|') and not line.startswith('|--') and 'Role' not in line:
            parts = [p.strip() for p in line.strip('|').split('|')]
            if len(parts) >= 2 and parts[0]:
                data["roles"].append({
                    "name": parts[0],
                    "category": parts[1] if len(parts) > 1 else "",
                    "emoji": parts[2] if len(parts) > 2 else "◆",
                    "how": parts[3] if len(parts) > 3 else "",
                })

    # Role research (parse ### Role: subsections)
    research_text = get_section("ROLE RESEARCH", text)
    role_sections = re.split(r'### ', research_text)
    for section in role_sections:
        if not section.strip():
            continue
        lines = section.strip().split('\n')
        role_name = lines[0].strip()
        role_data = {
            "status": "pending",
            "goals": [],
            "success": [],
            "pain_points": [],
            "solutions": [],
            "user_challenges": [],
        }
        current_list = None
        for line in lines[1:]:
            line_s = line.strip()
            if line_s.lower().startswith('research status:'):
                role_data["status"] = line_s.split(':', 1)[1].strip()
            elif line_s.lower() == 'goals:':
                current_list = role_data["goals"]
            elif line_s.lower().startswith('success looks like'):
                current_list = role_data["success"]
            elif line_s.lower().startswith('pain points'):
                current_list = role_data["pain_points"]
            elif line_s.lower().startswith('current solutions'):
                current_list = role_data["solutions"]
            elif line_s.lower().startswith("user's personal challenges") or line_s.lower().startswith("user challenges"):
                current_list = role_data["user_challenges"]
            elif (line_s.startswith('- ') or line_s.startswith('* ')) and current_list is not None:
                current_list.append(line_s[2:].strip())
        data["role_research"][role_name] = role_data

    # Tech breakthroughs
    tech_text = get_section("TECH BREAKTHROUGHS", text)
    data["tech_breakthroughs"] = get_bullets(tech_text) or ([tech_text.strip()] if tech_text.strip() else [])

    # Candidate problems
    cand_text = get_section("CANDIDATE PROBLEMS", text)
    cand_sections = re.split(r'### Problem', cand_text)
    for section in cand_sections:
        if not section.strip():
            continue
        lines = section.strip().split('\n')
        problem = {"name": lines[0].strip().lstrip('0123456789.: '), "details": {}}
        for line in lines[1:]:
            if ':' in line:
                key, _, val = line.strip().partition(':')
                problem["details"][key.strip().lower()] = val.strip()
        data["candidate_problems"].append(problem)

    # Open questions
    oq_text = get_section("OPEN QUESTIONS", text)
    data["open_questions"] = get_bullets(oq_text) or ([oq_text.strip()] if oq_text.strip() else [])

    return data


CATEGORY_COLORS = {
    "professional": "#2563EB",
    "hobby": "#16A34A",
    "life": "#EA580C",
    "family": "#7C3AED",
    "social": "#0891B2",
    "health": "#DC2626",
    "community": "#B45309",
}

CATEGORY_BG = {
    "professional": "#EFF6FF",
    "hobby": "#F0FDF4",
    "life": "#FFF7ED",
    "family": "#F5F3FF",
    "social": "#ECFEFF",
    "health": "#FEF2F2",
    "community": "#FFFBEB",
}

def make_tag(category):
    color = CATEGORY_COLORS.get(category.lower().split('/')[0], "#6B7280")
    bg = CATEGORY_BG.get(category.lower().split('/')[0], "#F3F4F6")
    return f'<span class="tag" style="color:{color};background:{bg}">{category}</span>'

def bullets_html(items, empty_msg="—"):
    if not items or (len(items) == 1 and not items[0]):
        return f'<p class="empty">{empty_msg}</p>'
    return '<ul>' + ''.join(f'<li>{i}</li>' for i in items if i) + '</ul>'

def generate_html(data):
    profile = data["profile"]
    name = profile.get("name", "Founder")
    version = data["meta"]["version"]
    date = data["meta"]["date"] or datetime.now().strftime("%B %d, %Y")
    round_n = data["meta"]["round"]

    # ── Tab: You ─────────────────────────────────────────────────────────────
    profile_rows = ""
    field_labels = {
        "name": "Name", "age": "Age", "gender": "Gender",
        "location_current": "Based in", "location_grew_up": "Grew up in",
    }
    for k, label in field_labels.items():
        v = profile.get(k, "")
        if v:
            profile_rows += f'<tr><td class="label">{label}</td><td>{v}</td></tr>'

    # Relationships
    rel = data["relationships"]
    rel_bullets = rel.get("_bullets", [])
    rel_kvs = {k: v for k, v in rel.items() if k != "_bullets" and v}
    rel_rows = ""
    for k, v in rel_kvs.items():
        if v:
            rel_rows += f'<tr><td class="label">{k.replace("_", " ").title()}</td><td>{v}</td></tr>'

    you_tab = f"""
    <div class="section-grid">
      <div class="card">
        <h3>👤 Profile</h3>
        <table class="kv-table">{profile_rows}</table>
      </div>
      <div class="card">
        <h3>🎓 Education</h3>
        {bullets_html(data["education"], "Not yet captured")}
      </div>
      <div class="card full-width">
        <h3>💼 Work History</h3>
        {bullets_html(data["work_history"], "Not yet captured")}
      </div>
      <div class="card">
        <h3>💬 Relationships</h3>
        {'<table class="kv-table">' + rel_rows + '</table>' if rel_rows else ''}
        {bullets_html(rel_bullets, "Not yet captured") if rel_bullets else ''}
      </div>
      <div class="card">
        <h3>🎯 Hobbies &amp; Interests</h3>
        {bullets_html(data["hobbies"], "Not yet captured")}
      </div>
      <div class="card">
        <h3>😤 Consumer Frustrations</h3>
        {bullets_html(data["consumer_frustrations"], "Not yet captured")}
      </div>
      <div class="card">
        <h3>🔧 Active Problems You're Solving</h3>
        {bullets_html(data["active_problems"], "Not yet captured")}
      </div>
    </div>
    """

    # ── Tab: Roles ────────────────────────────────────────────────────────────
    role_cards = ""
    if data["roles"]:
        for role in data["roles"]:
            cat = role.get("category", "").lower().split('/')[0]
            research = data["role_research"].get(role["name"], {})
            status = research.get("status", "pending")
            status_dot = "🟢" if status == "done" else "🟡"
            role_cards += f"""
            <div class="role-card">
              <div class="role-emoji">{role.get('emoji', '◆')}</div>
              <div class="role-name">{role['name']}</div>
              {make_tag(role.get('category', 'other'))}
              <div class="role-how">{role.get('how', '')}</div>
              <div class="role-status">{status_dot} Research {status}</div>
            </div>"""
    else:
        role_cards = '<p class="empty">Roles not yet mapped — complete Session 1 first.</p>'

    roles_tab = f'<div class="roles-grid">{role_cards}</div>'

    # ── Tab: Goals & Pain ─────────────────────────────────────────────────────
    goals_pain_tab = ""
    if data["role_research"]:
        for role_name, rd in data["role_research"].items():
            if not any([rd["goals"], rd["pain_points"], rd["success"]]):
                continue
            goals_pain_tab += f"""
            <div class="card full-width role-deep-dive">
              <h3>{role_name}</h3>
              <div class="deep-grid">
                <div>
                  <h4>🎯 Goals</h4>
                  {bullets_html(rd['goals'], 'Research pending')}
                </div>
                <div>
                  <h4>✅ Success looks like</h4>
                  {bullets_html(rd['success'], 'Research pending')}
                </div>
                <div>
                  <h4>😩 Pain points (reported)</h4>
                  {bullets_html(rd['pain_points'], 'Research pending')}
                </div>
                <div>
                  <h4>🛠 Current solutions</h4>
                  {bullets_html(rd['solutions'], 'Research pending')}
                </div>
              </div>
            </div>"""
    if not goals_pain_tab:
        goals_pain_tab = '<p class="empty">Role research not yet complete — this fills in after Session 1.</p>'

    # ── Tab: Your Challenges ──────────────────────────────────────────────────
    challenges_tab = ""
    if data["role_research"]:
        for role_name, rd in data["role_research"].items():
            if not rd.get("user_challenges"):
                continue
            challenges_tab += f"""
            <div class="card">
              <h3>{role_name}</h3>
              {bullets_html(rd['user_challenges'])}
            </div>"""
    if not challenges_tab:
        challenges_tab = '<p class="empty">Your personal challenges per role will appear here after the per-role interview.</p>'
    challenges_tab = f'<div class="section-grid">{challenges_tab}</div>'

    # ── Tab: Tech Breakthroughs ───────────────────────────────────────────────
    tech_tab = ""
    if data["tech_breakthroughs"] and any(data["tech_breakthroughs"]):
        for item in data["tech_breakthroughs"]:
            if not item:
                continue
            tech_tab += f'<div class="tech-card"><div class="tech-dot">⚡</div><div>{item}</div></div>'
    else:
        tech_tab = '<p class="empty">Tech breakthroughs will be mapped after role research.</p>'
    tech_tab = f'<div class="tech-grid">{tech_tab}</div>'

    # ── Tab: Opportunities ────────────────────────────────────────────────────
    opps_tab = ""
    if data["candidate_problems"]:
        for i, p in enumerate(data["candidate_problems"]):
            details = p.get("details", {})
            score = details.get("score", "—")
            status = details.get("status", "active")
            persona = details.get("persona", "")
            workaround = details.get("workaround", "")
            pain = details.get("pain moment", details.get("pain_moment", ""))
            color = "#16A34A" if "active" in status.lower() else "#9CA3AF"
            opps_tab += f"""
            <div class="card opp-card">
              <div class="opp-header">
                <span class="opp-name">#{i+1} {p['name']}</span>
                <span class="opp-score" style="color:{color}">{score}</span>
              </div>
              {f'<p class="opp-persona">{persona}</p>' if persona else ''}
              {f'<p><strong>Pain:</strong> {pain}</p>' if pain else ''}
              {f'<p><strong>Workaround:</strong> {workaround}</p>' if workaround else ''}
              <span class="tag" style="color:{color};background:{'#F0FDF4' if 'active' in status.lower() else '#F9FAFB'}">{status}</span>
            </div>"""
    if not opps_tab:
        opps_tab = '<p class="empty">Opportunity ranking appears here after candidate problems are identified.</p>'
    opps_tab = f'<div class="section-grid">{opps_tab}</div>'

    # ── Open questions ────────────────────────────────────────────────────────
    oq_html = bullets_html(data["open_questions"], "None recorded yet")

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Problem Finder — {name}</title>
<style>
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #F8FAFC; color: #1E293B; font-size: 15px; line-height: 1.6; }}
  .header {{ background: #fff; border-bottom: 1px solid #E2E8F0;
             padding: 20px 32px; display: flex; align-items: center;
             justify-content: space-between; position: sticky; top: 0; z-index: 100; }}
  .header-left h1 {{ font-size: 20px; font-weight: 700; color: #1E293B; }}
  .header-left h1 span {{ color: #2563EB; }}
  .header-meta {{ font-size: 13px; color: #94A3B8; margin-top: 2px; }}
  .badge {{ background: #EFF6FF; color: #2563EB; border-radius: 99px;
            padding: 4px 12px; font-size: 13px; font-weight: 600; }}
  .nav {{ background: #fff; border-bottom: 1px solid #E2E8F0;
          padding: 0 32px; display: flex; gap: 0; overflow-x: auto; }}
  .nav-btn {{ padding: 14px 20px; font-size: 14px; font-weight: 500;
              color: #64748B; border: none; background: none; cursor: pointer;
              border-bottom: 2px solid transparent; white-space: nowrap;
              transition: all 0.15s; }}
  .nav-btn:hover {{ color: #1E293B; }}
  .nav-btn.active {{ color: #2563EB; border-bottom-color: #2563EB; }}
  .content {{ max-width: 1100px; margin: 0 auto; padding: 32px; }}
  .tab-panel {{ display: none; }}
  .tab-panel.active {{ display: block; }}
  .section-title {{ font-size: 18px; font-weight: 700; margin-bottom: 20px; color: #1E293B; }}
  .section-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
                   gap: 20px; }}
  .card {{ background: #fff; border: 1px solid #E2E8F0; border-radius: 12px;
           padding: 20px; }}
  .card.full-width {{ grid-column: 1 / -1; }}
  .card h3 {{ font-size: 15px; font-weight: 600; margin-bottom: 12px; color: #1E293B; }}
  .card h4 {{ font-size: 13px; font-weight: 600; margin-bottom: 8px; color: #475569; text-transform: uppercase; letter-spacing: 0.05em; }}
  .card ul {{ padding-left: 18px; }}
  .card li {{ margin-bottom: 6px; color: #334155; }}
  .card p {{ color: #334155; }}
  .kv-table {{ width: 100%; border-collapse: collapse; }}
  .kv-table td {{ padding: 6px 0; vertical-align: top; }}
  .kv-table .label {{ color: #94A3B8; font-size: 13px; width: 40%; }}
  .tag {{ display: inline-block; padding: 2px 8px; border-radius: 99px;
          font-size: 12px; font-weight: 500; margin-top: 4px; }}
  .empty {{ color: #94A3B8; font-style: italic; font-size: 14px; }}
  /* Roles */
  .roles-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 16px; }}
  .role-card {{ background: #fff; border: 1px solid #E2E8F0; border-radius: 12px;
                padding: 20px; text-align: center; }}
  .role-emoji {{ font-size: 36px; margin-bottom: 10px; }}
  .role-name {{ font-weight: 700; font-size: 15px; margin-bottom: 6px; color: #1E293B; }}
  .role-how {{ font-size: 12px; color: #94A3B8; margin-top: 6px; }}
  .role-status {{ font-size: 12px; margin-top: 8px; color: #64748B; }}
  /* Deep dive */
  .role-deep-dive h3 {{ font-size: 17px; margin-bottom: 16px; }}
  .deep-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
  @media(max-width: 600px) {{ .deep-grid {{ grid-template-columns: 1fr; }} }}
  /* Tech */
  .tech-grid {{ display: flex; flex-direction: column; gap: 12px; }}
  .tech-card {{ background: #fff; border: 1px solid #E2E8F0; border-radius: 10px;
                padding: 16px; display: flex; gap: 14px; align-items: flex-start; }}
  .tech-dot {{ font-size: 20px; flex-shrink: 0; }}
  /* Opportunities */
  .opp-card {{ }}
  .opp-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }}
  .opp-name {{ font-weight: 700; font-size: 15px; }}
  .opp-score {{ font-weight: 700; font-size: 18px; }}
  .opp-persona {{ font-size: 13px; color: #64748B; margin-bottom: 8px; }}
  /* Open questions */
  .oq-section {{ background: #fff; border: 1px solid #E2E8F0; border-radius: 12px; padding: 24px; margin-top: 32px; }}
  .oq-section h3 {{ font-size: 15px; font-weight: 600; margin-bottom: 12px; }}
</style>
</head>
<body>

<div class="header">
  <div class="header-left">
    <h1>🔍 Problem Finder — <span>{name}</span></h1>
    <div class="header-meta">Updated {date} · Round {round_n}</div>
  </div>
  <div class="badge">v{version}</div>
</div>

<nav class="nav">
  <button class="nav-btn active" onclick="showTab('you', this)">👤 You</button>
  <button class="nav-btn" onclick="showTab('roles', this)">🎭 Your Roles</button>
  <button class="nav-btn" onclick="showTab('goals', this)">🎯 Goals &amp; Pain</button>
  <button class="nav-btn" onclick="showTab('challenges', this)">😩 Your Challenges</button>
  <button class="nav-btn" onclick="showTab('tech', this)">⚡ Tech Breakthroughs</button>
  <button class="nav-btn" onclick="showTab('opps', this)">💡 Opportunities</button>
</nav>

<div class="content">
  <div id="tab-you" class="tab-panel active">
    <div class="section-title">Everything about you</div>
    {you_tab}
  </div>

  <div id="tab-roles" class="tab-panel">
    <div class="section-title">Every market you represent</div>
    {roles_tab}
  </div>

  <div id="tab-goals" class="tab-panel">
    <div class="section-title">What people in your roles want — and what stops them</div>
    <div class="section-grid">{goals_pain_tab}</div>
  </div>

  <div id="tab-challenges" class="tab-panel">
    <div class="section-title">Your personal experience in each role</div>
    {challenges_tab}
  </div>

  <div id="tab-tech" class="tab-panel">
    <div class="section-title">What became newly possible — and why it matters now</div>
    {tech_tab}
  </div>

  <div id="tab-opps" class="tab-panel">
    <div class="section-title">Ranked opportunities</div>
    {opps_tab}
  </div>

  <div class="oq-section">
    <h3>❓ Open Questions</h3>
    {oq_html}
  </div>
</div>

<script>
function showTab(id, btn) {{
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
  document.getElementById('tab-' + id).classList.add('active');
  btn.classList.add('active');
}}
</script>

</body>
</html>"""
    return html


def main():
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.home() / "problem-finder" / "discovery.md"
    output_path = Path(sys.argv[2]) if len(sys.argv) > 2 else input_path.with_suffix('.html')

    if not input_path.exists():
        print(f"Error: {input_path} not found")
        sys.exit(1)

    text = input_path.read_text()
    data = parse_document(text)
    html = generate_html(data)
    output_path.write_text(html)
    print(f"Generated: {output_path}")


if __name__ == "__main__":
    main()
