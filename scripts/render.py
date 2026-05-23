#!/usr/bin/env python3
"""
Problem Finder — Discovery Document -> JSX Data + HTML Shell
Parses discovery.md (either the structured SKILL.md template format OR the
"Founder Profile / Industry Landscape" format produced by earlier skill
versions) and generates:
  * data.jsx       -- bridges discovery.md data to the React UI
  * discovery.html -- HTML shell that loads ui/ files + data.jsx

Usage: python3 render.py [input.md] [output-dir]
  output-dir defaults to ~/problem-finder/
"""
import sys, re, json
from pathlib import Path
from datetime import datetime

# ---- Helpers -----------------------------------------------------------------
def safe_id(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def js_str(s):
    return json.dumps(str(s) if s is not None else "")

def escape_template_literal(s):
    s = s.replace("\\", "\\\\")
    s = s.replace("`", "\\`")
    s = s.replace("${", "\\${")
    return s

# ---- Parser ------------------------------------------------------------------
def parse_document(text):
    d = {
        "meta": {"version": "1", "date": "", "round": "1"},
        "profile": {}, "education": [], "work_history": [],
        "relationships": {}, "hobbies": [], "consumer_frustrations": [],
        "active_problems": [], "roles": [], "role_research": {},
        "tech_breakthroughs": [], "candidate_problems": [],
        "network_contacts": [], "open_questions": [],
    }

    m = re.search(r'version:\s*(\d+)\s*\|\s*date:\s*([^|]+)\s*\|\s*round:\s*(\d+)', text, re.IGNORECASE)
    if m:
        d["meta"] = {"version": m.group(1), "date": m.group(2).strip(), "round": m.group(3)}

    # --- section lookup with aliases ---
    def sec(name, *aliases):
        for n in [name] + list(aliases):
            pat = r'\n## ' + re.escape(n) + r'\s*\n(.*?)(?=\n## |\Z)'
            x = re.search(pat, text, re.DOTALL | re.IGNORECASE)
            if x:
                return x.group(1).strip()
        return ""

    def bullets(t, include_pending=False):
        out = []
        for ln in t.split('\n'):
            ln = ln.strip()
            if ln.startswith(('- ', '* ', '• ')):
                v = ln[2:].strip()
                if v and (include_pending or '[PENDING]' not in v):
                    out.append(v)
        return out

    def parse_table(t):
        rows, headers = [], []
        for ln in t.split('\n'):
            ln = ln.strip()
            if not ln.startswith('|'):
                continue
            cells = [c.strip() for c in ln.strip('|').split('|')]
            if not headers:
                headers = cells
                continue
            if all(re.match(r'^[-: ]+$', c) for c in cells if c):
                continue
            if cells:
                rows.append(dict(zip(headers, cells)))
        return rows

    # ---- PROFILE (template format: ## PROFILE, new format: ## FOUNDER PROFILE) ----
    profile_text = sec("PROFILE", "FOUNDER PROFILE")
    # Parse key:value pairs at any indent level
    for ln in profile_text.split('\n'):
        if ':' in ln and not ln.strip().startswith(('-', '*', '#')):
            k, _, v = ln.partition(':')
            k = k.strip().lower().replace(' ', '_')
            v = v.strip()
            if k and v and not v.startswith('[') and v != '[PENDING]':
                d["profile"][k] = v

    # Also check inside ### Professional subsection for the actual format
    prof_sub = re.search(r'### Professional\n(.*?)(?=\n### |\Z)', profile_text, re.DOTALL)
    if prof_sub:
        for ln in prof_sub.group(1).split('\n'):
            if ':' in ln and not ln.strip().startswith(('-', '*', '#')):
                k, _, v = ln.partition(':')
                k = k.strip().lower().replace(' ', '_')
                v = v.strip()
                if k and v:
                    d["profile"][k] = v

    # Try to extract founder name if not found as name: field
    if not d["profile"].get("name"):
        # Look for "Name: X" or "Founder: X" or "Subject: X" pattern
        nm = re.search(r'(?:^|\n)(?:name|founder|subject)\s*:\s*([^\n\[]+)', profile_text, re.IGNORECASE)
        if nm:
            d["profile"]["name"] = nm.group(1).strip()
        else:
            # Try to find from document title line like "DISCOVERY DOCUMENT — Thomas"
            tm = re.search(r'DISCOVERY(?:\s+DOCUMENT)?\s*[—-]\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)', text)
            if tm:
                d["profile"]["name"] = tm.group(1).strip()
            else:
                # Last resort: look for "account owner (Name)" in the document body
                owner_m = re.search(r'account\s+owner\s*\(([A-Z][a-z]{2,})\)', text)
                if owner_m:
                    d["profile"]["name"] = owner_m.group(1).strip()
                else:
                    # Try "escalate to Name" — common in host/ops problem descriptions
                    esc_m = re.search(r'escalate\s+to\s+([A-Z][a-z]{2,})\b', text)
                    if esc_m:
                        d["profile"]["name"] = esc_m.group(1).strip()

    # ---- Standard template sections ----
    d["education"]             = bullets(sec("EDUCATION"))
    d["work_history"]          = bullets(sec("WORK HISTORY"))
    d["hobbies"]               = bullets(sec("HOBBIES AND INTERESTS"))
    d["consumer_frustrations"] = bullets(sec("CONSUMER FRUSTRATIONS"))
    d["active_problems"]       = bullets(sec("ACTIVE PROBLEMS"))
    d["tech_breakthroughs"]    = bullets(sec("TECH BREAKTHROUGHS"))
    d["open_questions"]        = bullets(sec("OPEN QUESTIONS"))

    rel_text = sec("RELATIONSHIPS")
    rel = {}
    for ln in rel_text.split('\n'):
        ln = ln.strip()
        if ':' in ln and not ln.startswith(('-', '*', '#')):
            k, _, v = ln.partition(':')
            if k.strip() and v.strip() and not v.strip().startswith('['):
                rel[k.strip()] = v.strip()
    rel['_bullets'] = bullets(rel_text)
    d["relationships"] = rel

    # ---- ROLES LIST (template format) ----
    roles_list_text = sec("ROLES LIST")
    if roles_list_text:
        for row in parse_table(roles_list_text):
            name = row.get('Role', '')
            if name and not name.startswith('['):
                d["roles"].append({
                    "name": name,
                    "category": row.get('Category', ''),
                    "emoji": row.get('Emoji', '◆'),
                    "how": row.get('How Identified', row.get('What it gives you', '')),
                })

    # ---- ROLE RESEARCH (template format) ----
    role_research_text = sec("ROLE RESEARCH")
    if role_research_text:
        for rs in re.split(r'\n### ', '\n' + role_research_text):
            if not rs.strip():
                continue
            lines = rs.strip().split('\n')
            rname = lines[0].strip()
            rd = {
                "status": "pending", "goals": [], "success": [],
                "pain_points": [], "workarounds": [], "tech_narratives": [],
                "tam": [], "user_challenges": [],
            }
            cur = None
            for ln in lines[1:]:
                s = ln.strip(); sl = s.lower()
                if sl.startswith('research status:'):
                    rd["status"] = s.split(':', 1)[1].strip()
                elif sl == 'goals:':
                    cur = rd["goals"]
                elif sl.startswith('success looks like'):
                    cur = rd["success"]
                elif sl.startswith('pain point'):
                    cur = rd["pain_points"]
                elif sl.startswith('workaround'):
                    cur = rd["workarounds"]
                elif sl.startswith('tech narrative'):
                    cur = rd["tech_narratives"]
                elif sl.startswith('tam') or sl.startswith('market size'):
                    cur = rd["tam"]
                elif sl.startswith('user') and ('challenge' in sl or 'personal' in sl):
                    cur = rd["user_challenges"]
                elif s.startswith(('- ', '* ', '• ')) and cur is not None:
                    v = s[2:].strip()
                    if v and '[PENDING]' not in v:
                        cur.append(v)
            d["role_research"][rname] = rd

    # ---- INDUSTRY LANDSCAPE fallback (actual format) ----
    # Use this when no ROLES LIST / ROLE RESEARCH sections exist
    landscape_text = sec("INDUSTRY LANDSCAPE")
    if landscape_text and not d["roles"]:
        _parse_industry_landscape(landscape_text, d)

    # ---- CANDIDATE PROBLEMS ----
    for block in re.split(r'\n### Problem\s*\d*\s*:', '\n' + sec("CANDIDATE PROBLEMS")):
        if not block.strip():
            continue
        lines = block.strip().split('\n')
        name = lines[0].strip().lstrip('0123456789. ')
        details = {}
        for ln in lines[1:]:
            if ':' in ln:
                k, _, v = ln.strip().partition(':')
                details[k.strip().lower()] = v.strip()
        if name:
            d["candidate_problems"].append({"name": name, "details": details})

    # ---- NETWORK CONTACTS (template format) ----
    net_text = sec("NETWORK CONTACTS")
    if net_text:
        d["network_contacts"] = [
            row for row in parse_table(net_text)
            if row.get('Name') and not row.get('Name', '').startswith('[')
        ]
    else:
        # Fallback: ### Network map table inside ## FOUNDER PROFILE
        net_match = re.search(
            r'### Network map\n(.*?)(?=\n### |\n## |\Z)', profile_text, re.DOTALL)
        if net_match:
            for row in parse_table(net_match.group(1)):
                role_val = row.get('Role', row.get('Name', ''))
                does_val = row.get('What they do', row.get('What They Do', ''))
                note_val = row.get('Why interesting', row.get('Why Interesting', ''))
                if role_val and not role_val.startswith(('|', '[-', '[')):
                    d["network_contacts"].append({
                        'Name': role_val,
                        'How You Know Them': '',
                        'What They Do': does_val,
                        'Role Overlap': '',
                        'Interviewed?': 'No',
                        '_note': note_val,
                    })

    return d


def _parse_industry_landscape(landscape_text, d):
    """Parse the ## INDUSTRY LANDSCAPE section as roles + role research.
    Each ### subsection becomes one role unless it's marked eliminated/context-only."""
    for rs in re.split(r'\n### ', '\n' + landscape_text):
        if not rs.strip():
            continue
        lines = rs.strip().split('\n')
        rname = lines[0].strip()
        content = '\n'.join(lines[1:])

        # Skip eliminated or context-only markets
        first_line = lines[1].strip().lower() if len(lines) > 1 else ''
        is_eliminated = (
            'eliminated' in rname.lower() or
            re.match(r'.*\(eliminated\)', rname, re.IGNORECASE) or
            re.match(r'.*\(context only', content[:200], re.IGNORECASE) or
            re.match(r'market dominated', first_line) or
            re.match(r'narrative has shifted', first_line)
        )
        if is_eliminated:
            continue

        # Infer category from role name
        category = _infer_category(rname)

        d["roles"].append({
            "name": rname,
            "category": category,
            "emoji": _infer_emoji(rname),
            "how": "",
        })

        # Parse the rich content
        rd = {
            "status": "done",
            "goals": [], "success": [],
            "pain_points": [], "workarounds": [],
            "tech_narratives": [], "tam": [], "user_challenges": [],
        }
        cur = None

        for ln in lines[1:]:
            s = ln.strip()
            # Skip the line if it is a pure section header (key:) followed by bullets
            # vs a key: value line (value on same line)
            if ':' in s and not s.startswith(('-', '*', '  -')):
                k, _, v = s.partition(':')
                kl = k.strip().lower()
                v = v.strip()

                if kl == 'goals':
                    if v:
                        rd["goals"].extend(_split_semicolons(v))
                    cur = rd["goals"]
                elif 'workaround' in kl:
                    if v:
                        rd["workarounds"].extend(_split_semicolons(v))
                    cur = rd["workarounds"]
                elif 'pain signal' in kl or 'pain point' in kl:
                    cur = rd["pain_points"]
                elif 'incumbent gap' in kl:
                    cur = rd["pain_points"]
                elif 'recent shift' in kl:
                    if v:
                        rd["tech_narratives"].extend(_split_semicolons(v))
                    cur = rd["tech_narratives"]
                elif 'tech narrative' in kl:
                    cur = rd["tech_narratives"]
                elif kl.startswith('tam') or 'market size' in kl:
                    if v:
                        rd["tam"].append(v)
                    cur = rd["tam"]
                elif 'user' in kl and ('challenge' in kl or 'personal' in kl):
                    cur = rd["user_challenges"]
                else:
                    cur = None

            elif (s.startswith('- ') or s.startswith('  - ') or s.startswith('* ')) and cur is not None:
                v = s.lstrip(' -* ').strip()
                if v and '[PENDING]' not in v:
                    cur.append(v)

        d["role_research"][rname] = rd


def _split_semicolons(s):
    """Split a value like 'A; B; C' into ['A', 'B', 'C']."""
    return [x.strip() for x in s.split(';') if x.strip()]


CATEGORY_KEYWORDS = {
    'professional': ['operator', 'host', 'engineer', 'fintech', 'trader', 'creator', 'startup', 'founder', 'business', 'work'],
    'health':       ['health', 'fitness', 'calorie', 'gym', 'diet', 'nutrition', 'weight'],
    'hobby':        ['crypto', 'memecoin', 'youtube', 'content', 'bike', 'motor', 'cycle', 'snowboard', 'music', 'art'],
    'social':       ['social', 'community', 'friend', 'network', 'club'],
    'family':       ['parent', 'child', 'father', 'mother', 'family', 'partner', 'spouse'],
    'life':         ['life', 'personal', 'daily', 'routine'],
}

def _infer_category(name):
    nl = name.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in nl for kw in keywords):
            return cat
    return 'professional'

EMOJI_MAP = [
    ('airbnb', '🏠'), ('rental', '🏠'), ('host', '🏠'), ('str', '🏠'),
    ('crypto', '₿'), ('memecoin', '₿'), ('token', '₿'),
    ('fitness', '💪'), ('health', '💪'), ('calorie', '💪'), ('gym', '💪'),
    ('youtube', '▶️'), ('content', '🎬'), ('video', '🎬'), ('creator', '🎬'),
    ('trade', '📈'), ('stock', '📈'), ('invest', '📈'),
    ('engineer', '💻'), ('ios', '📱'), ('code', '💻'), ('tech', '💻'),
    ('bike', '🚲'), ('cycle', '🚲'), ('motor', '🏍️'), ('ride', '🏍️'),
    ('snow', '🏔️'), ('ski', '⛷️'), ('board', '🏂'),
    ('design', '🎨'), ('art', '🎨'),
    ('father', '👨‍👧'), ('parent', '👨‍👧'), ('family', '👨‍👧'),
]

def _infer_emoji(name):
    nl = name.lower()
    for keyword, emoji in EMOJI_MAP:
        if keyword in nl:
            return emoji
    return '◆'


# ---- Orbit / angle assignment ------------------------------------------------
ORBIT_1_CATS = {'professional', 'life', 'health'}

def assign_positions(roles):
    """Assign orbit (1=inner, 2=outer) and spread angle by category."""
    orbit1 = [r for r in roles if r['category'].strip().lower() in ORBIT_1_CATS]
    orbit2 = [r for r in roles if r['category'].strip().lower() not in ORBIT_1_CATS]

    result = {}
    n1 = max(len(orbit1), 1)
    for i, r in enumerate(orbit1):
        result[r['name']] = {'orbit': 1, 'angle': round((90 + i * 360 / n1) % 360)}

    n2 = max(len(orbit2), 1)
    for i, r in enumerate(orbit2):
        result[r['name']] = {'orbit': 2, 'angle': round((30 + i * 360 / n2) % 360)}

    return result


# ---- Data mapping ------------------------------------------------------------
def build_persona(d):
    p = d["profile"]
    meta = d["meta"]
    age_raw = p.get("age", "")
    age = int(age_raw) if re.match(r'^\d+$', (age_raw or '')) else None
    return {
        "name":           p.get("name", "Founder"),
        "age":            age,
        "location":       p.get("location_current", p.get("location", "")),
        "epigraph":       p.get("epigraph", p.get("tagline", "")),
        "interviewedOn":  meta.get("date", ""),
        "interviewLength": p.get("interview_length", ""),
    }


def build_roles(d):
    roles = d["roles"]
    research = d["role_research"]
    positions = assign_positions(roles)
    out = []

    for r in roles:
        rname = r['name']
        rr = research.get(rname, {})
        pos = positions.get(rname, {'orbit': 2, 'angle': 0})

        goal_parts = rr.get("goals", []) + rr.get("success", [])
        goal = " ".join(goal_parts)
        practice = rr.get("workarounds", [])
        personal = rr.get("user_challenges", [])
        researched = [{"text": p, "source": "Research"} for p in rr.get("pain_points", [])]

        narratives = []
        tam = rr.get("tam", [])
        if tam:
            narratives.append(tam[0])
        narratives.extend(rr.get("tech_narratives", []))

        cat = r['category'].lower()
        if any(x in cat for x in ('seasonal', 'winter')):
            intensity = "seasonal"
        elif any(x in cat for x in ('social', 'community', 'volunteer')):
            intensity = "weekly"
        else:
            intensity = "daily"

        words = rname.split()
        short = words[0] if len(words) > 1 and len(words[0]) >= 4 else rname

        out.append({
            "id":            safe_id(rname),
            "label":         rname,
            "shortLabel":    short,
            "sublabel":      r.get("how", ""),
            "angle":         pos["angle"],
            "orbit":         pos["orbit"],
            "intensity":     intensity,
            "goal":          goal,
            "practice":      practice,
            "problems":      {"personal": personal, "researched": researched},
            "narratives":    narratives,
            "openQuestions": [],
        })
    return out


def build_network(d, role_ids):
    out = []
    for c in d["network_contacts"]:
        name = c.get("Name", "").strip()
        if not name or name.startswith(("[", "|")):
            continue

        overlap_raw = c.get("Role Overlap", "")
        overlap_ids = []
        if overlap_raw and not overlap_raw.startswith("["):
            for part in re.split(r'[,/&]+', overlap_raw):
                part = part.strip()
                if not part:
                    continue
                sid = safe_id(part)
                matched = next(
                    (rid for rid in role_ids if rid == sid or sid in rid or rid in sid),
                    sid
                )
                overlap_ids.append(matched)

        does = c.get("What They Do", "").strip()
        note = c.get("_note", "").strip() if "_note" in c else ""
        out.append({
            "id":           safe_id(name),
            "name":         name,
            "relation":     c.get("How You Know Them", "").strip(),
            "distance":     1,
            "roles":        [does] if does and not does.startswith("[") else [],
            "overlapsWith": overlap_ids,
            "note":         note,
        })
    return out


# ---- data.jsx generator ------------------------------------------------------
def generate_data_jsx(d, raw_text):
    persona = build_persona(d)
    roles   = build_roles(d)
    role_ids = [r["id"] for r in roles]
    network = build_network(d, role_ids)

    def str_list(lst):
        if not lst:
            return "[]"
        items = ",\n      ".join(js_str(x) for x in lst)
        return "[\n      " + items + ",\n    ]"

    lines = []
    lines.append("/* data.jsx — auto-generated by render.py from discovery.md.\n"
                 "   Edit discovery.md, then re-run:  python3 scripts/render.py\n"
                 "   Do not edit this file by hand. */\n")

    # PERSONA
    lines.append("const PERSONA = {")
    lines.append(f"  name: {js_str(persona['name'])},")
    if persona['age'] is not None:
        lines.append(f"  age: {persona['age']},")
    lines.append(f"  location: {js_str(persona['location'])},")
    lines.append(f"  epigraph: {js_str(persona['epigraph'])},")
    lines.append(f"  interviewedOn: {js_str(persona['interviewedOn'])},")
    lines.append(f"  interviewLength: {js_str(persona['interviewLength'])},")
    lines.append("};\n")

    # ROLES
    lines.append("const ROLES = [")
    for r in roles:
        lines.append("  {")
        lines.append(f"    id: {js_str(r['id'])},")
        lines.append(f"    label: {js_str(r['label'])},")
        lines.append(f"    shortLabel: {js_str(r['shortLabel'])},")
        lines.append(f"    sublabel: {js_str(r['sublabel'])},")
        lines.append(f"    angle: {r['angle']},")
        lines.append(f"    orbit: {r['orbit']},")
        lines.append(f"    intensity: {js_str(r['intensity'])},")
        lines.append(f"    goal: {js_str(r['goal'])},")
        lines.append(f"    practice: {str_list(r['practice'])},")
        lines.append("    problems: {")
        lines.append(f"      personal: {str_list(r['problems']['personal'])},")
        if r['problems']['researched']:
            items = ",\n        ".join(
                "{{ text: {}, source: {} }}".format(js_str(x['text']), js_str(x['source']))
                for x in r['problems']['researched']
            )
            lines.append(f"      researched: [\n        {items},\n      ],")
        else:
            lines.append("      researched: [],")
        lines.append("    },")
        lines.append(f"    narratives: {str_list(r['narratives'])},")
        lines.append(f"    openQuestions: {str_list(r['openQuestions'])},")
        lines.append("  },")
    lines.append("];\n")

    # NETWORK
    lines.append("const NETWORK = [")
    for c in network:
        lines.append("  {")
        lines.append(f"    id: {js_str(c['id'])},")
        lines.append(f"    name: {js_str(c['name'])},")
        lines.append(f"    relation: {js_str(c['relation'])},")
        lines.append(f"    distance: {c['distance']},")
        lines.append(f"    roles: {str_list(c['roles'])},")
        if c['overlapsWith']:
            items = ", ".join(js_str(x) for x in c['overlapsWith'])
            lines.append(f"    overlapsWith: [{items}],")
        else:
            lines.append("    overlapsWith: [],")
        lines.append(f"    note: {js_str(c['note'])},")
        lines.append("  },")
    lines.append("];\n")

    # DISCOVERY_DOC
    escaped = escape_template_literal(raw_text)
    lines.append("const DISCOVERY_DOC = `" + escaped + "`;\n")
    lines.append("Object.assign(window, { PERSONA, ROLES, NETWORK, DISCOVERY_DOC });")
    return "\n".join(lines)


# ---- discovery.html shell ----------------------------------------------------
def generate_html_shell(persona_name):
    return f"""<!doctype html>
<html lang="en" data-tone="cream">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Self — {persona_name}</title>

  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link
    href="https://fonts.googleapis.com/css2?family=Instrument+Serif:ital@0;1&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&display=swap"
    rel="stylesheet"
  />

  <link rel="stylesheet" href="ui/styles.css" />

  <script src="https://unpkg.com/react@18.3.1/umd/react.development.js" integrity="sha384-hD6/rw4ppMLGNu3tX5cjIb+uRZ7UkRJ6BPkLpg4hAu/6onKUg4lLsHAs9EBPT82L" crossorigin="anonymous"></script>
  <script src="https://unpkg.com/react-dom@18.3.1/umd/react-dom.development.js" integrity="sha384-u6aeetuaXnQ38mYT8rp6sbXaQe3NL9t+IBXmnYxwkUI2Hw4bsp2Wvmx4yRQF1uAm" crossorigin="anonymous"></script>
  <script src="https://unpkg.com/@babel/standalone@7.29.0/babel.min.js" integrity="sha384-m08KidiNqLdpJqLq95G/LEi8Qvjl/xUYll3QILypMoQ65QorJ9Lvtp2RXYGBFj1y" crossorigin="anonymous"></script>
</head>
<body>
  <div id="root"></div>

  <script type="text/babel" src="ui/tweaks-panel.jsx"></script>
  <script type="text/babel" src="data.jsx"></script>
  <script type="text/babel" src="ui/map.jsx"></script>
  <script type="text/babel" src="ui/drawer.jsx"></script>
  <script type="text/babel" src="ui/tabs.jsx"></script>
  <script type="text/babel" src="ui/app.jsx"></script>
</body>
</html>"""


# ---- Entry point -------------------------------------------------------------
def main():
    inp = (
        Path(sys.argv[1]) if len(sys.argv) > 1
        else Path.home() / "problem-finder" / "discovery.md"
    )
    out_dir = (
        Path(sys.argv[2]) if len(sys.argv) > 2
        else Path.home() / "problem-finder"
    )

    if not inp.exists():
        print(f"Error: {inp} not found", file=sys.stderr)
        sys.exit(1)

    raw_text = inp.read_text(encoding='utf-8')
    d = parse_document(raw_text)
    persona_name = d["profile"].get("name", "Founder")

    data_jsx_path = out_dir / "data.jsx"
    data_jsx_path.write_text(generate_data_jsx(d, raw_text), encoding='utf-8')
    print(f"✓ data.jsx       → {data_jsx_path}")

    html_path = out_dir / "discovery.html"
    html_path.write_text(generate_html_shell(persona_name), encoding='utf-8')
    print(f"✓ discovery.html → {html_path}")


if __name__ == "__main__":
    main()
