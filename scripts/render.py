#!/usr/bin/env python3
"""
Problem Finder — Discovery Document → data.jsx
Reads discovery.md, maps it to the self-map React UI schema, and writes
data.jsx to the design folder so the website loads with real data.

Usage:
  python3 render.py                          # uses default paths
  python3 render.py path/to/discovery.md     # custom input
  python3 render.py path/to/discovery.md /path/to/output/data.jsx
"""
import sys, re, json
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
DEFAULT_INPUT  = Path.home() / "problem-finder" / "discovery.md"
DEFAULT_OUTPUT = Path("/Users/evgeny/Downloads/self profile/data.jsx")

# ── Helpers ───────────────────────────────────────────────────────────────────
def safe_id(s):
    return re.sub(r'[^a-z0-9]+', '-', (s or '').lower()).strip('-')

def js_str(s):
    return json.dumps(str(s) if s is not None else "")

def escape_tl(s):
    """Escape a string for use inside a JS template literal."""
    s = s.replace("\\", "\\\\")
    s = s.replace("`", "\\`")
    s = s.replace("${", "\\${")
    return s

# ── Parser ────────────────────────────────────────────────────────────────────
def parse_document(text):
    d = {
        "meta": {"version": "1", "date": "", "round": "1"},
        "profile": {}, "roles": [], "role_research": {},
        "network_contacts": [], "open_questions": [], "candidate_problems": [],
    }

    # Meta line
    m = re.search(r'version:\s*(\d+)\s*\|\s*date:\s*([^|]+)\s*\|\s*round:\s*(\d+)', text, re.I)
    if m:
        d["meta"] = {"version": m.group(1), "date": m.group(2).strip(), "round": m.group(3)}

    # Section lookup — accepts aliases so both old and new doc formats work
    def sec(name, *aliases):
        for n in [name] + list(aliases):
            x = re.search(r'\n## ' + re.escape(n) + r'\s*\n(.*?)(?=\n## |\Z)',
                          text, re.DOTALL | re.IGNORECASE)
            if x:
                return x.group(1).strip()
        return ""

    def bullets(t):
        out = []
        for ln in t.split('\n'):
            s = ln.strip()
            if s.startswith(('- ', '* ', '• ')):
                v = s[2:].strip()
                if v and '[PENDING]' not in v:
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

    # ── Profile ────────────────────────────────────────────────────────────────
    profile_text = sec("PROFILE", "FOUNDER PROFILE")
    for ln in profile_text.split('\n'):
        if ':' in ln and not ln.strip().startswith(('-', '*', '#')):
            k, _, v = ln.partition(':')
            k = k.strip().lower().replace(' ', '_')
            v = v.strip()
            if k and v and not v.startswith('[') and v != '[PENDING]':
                d["profile"][k] = v

    # Also parse ### Professional subsection (actual doc format)
    ps = re.search(r'### Professional\n(.*?)(?=\n### |\Z)', profile_text, re.DOTALL)
    if ps:
        for ln in ps.group(1).split('\n'):
            if ':' in ln and not ln.strip().startswith(('-', '*', '#')):
                k, _, v = ln.partition(':')
                k = k.strip().lower().replace(' ', '_')
                v = v.strip()
                if k and v:
                    d["profile"].setdefault(k, v)

    # Name fallback: look for "account owner (Name)" in body
    if not d["profile"].get("name"):
        nm = re.search(r'account\s+owner\s*\(([A-Z][a-z]{2,})\)', text)
        if nm:
            d["profile"]["name"] = nm.group(1)
        else:
            em = re.search(r'escalate\s+to\s+([A-Z][a-z]{2,})\b', text)
            if em:
                d["profile"]["name"] = em.group(1)

    # ── Roles list ─────────────────────────────────────────────────────────────
    roles_table = sec("ROLES LIST")
    if roles_table:
        for row in parse_table(roles_table):
            name = row.get('Role', '')
            if name and not name.startswith('['):
                d["roles"].append({
                    "name":     name,
                    "category": row.get('Category', ''),
                    "emoji":    row.get('Emoji', '◆'),
                    "how":      row.get('How Identified', row.get('What it gives you', '')),
                })

    # ── Role research ──────────────────────────────────────────────────────────
    for rs in re.split(r'\n### ', '\n' + sec("ROLE RESEARCH")):
        if not rs.strip():
            continue
        lines = rs.strip().split('\n')
        rname = lines[0].strip()
        rd = {"status": "pending", "goals": [], "success": [], "pain_points": [],
              "workarounds": [], "tech_narratives": [], "tam": [],
              "user_challenges": [], "open_questions": []}
        cur = None
        for ln in lines[1:]:
            s = ln.strip(); sl = s.lower()
            if sl.startswith('research status:'):    rd["status"] = s.split(':', 1)[1].strip(); cur = None
            elif sl == 'goals:':                      cur = rd["goals"]
            elif sl.startswith('success looks like'): cur = rd["success"]
            elif sl.startswith('pain point'):         cur = rd["pain_points"]
            elif sl.startswith('workaround'):         cur = rd["workarounds"]
            elif sl.startswith('tech narrative'):     cur = rd["tech_narratives"]
            elif sl.startswith('tam') or sl.startswith('market size'): cur = rd["tam"]
            elif sl.startswith('user') and ('challenge' in sl or 'personal' in sl): cur = rd["user_challenges"]
            elif sl.startswith('open question'):      cur = rd["open_questions"]
            elif s.startswith(('- ', '* ', '• ')) and cur is not None:
                v = s[2:].strip()
                if v and '[PENDING]' not in v:
                    cur.append(v)
        d["role_research"][rname] = rd

    # ── Fallback: INDUSTRY LANDSCAPE as role research ──────────────────────────
    landscape = sec("INDUSTRY LANDSCAPE")
    if landscape and not d["role_research"]:
        _parse_landscape(landscape, d)

    # ── Network ────────────────────────────────────────────────────────────────
    net_text = sec("NETWORK CONTACTS")
    if net_text:
        d["network_contacts"] = [
            r for r in parse_table(net_text)
            if r.get('Name') and not r.get('Name', '').startswith('[')
        ]
    else:
        # Fallback: ### Network map table inside the profile section
        profile_text2 = sec("FOUNDER PROFILE", "PROFILE")
        nm_match = re.search(r'### Network map\n(.*?)(?=\n### |\n## |\Z)',
                             profile_text2, re.DOTALL)
        if nm_match:
            for row in parse_table(nm_match.group(1)):
                role_val = row.get('Role', row.get('Name', ''))
                if role_val and not role_val.startswith(('[', '|')):
                    d["network_contacts"].append({
                        'Name':             role_val,
                        'How You Know Them': '',
                        'What They Do':     row.get('What they do', ''),
                        'Role Overlap':     '',
                        'Interviewed?':     'No',
                        '_note':            row.get('Why interesting', ''),
                    })

    # ── Open questions (global) ────────────────────────────────────────────────
    d["open_questions"] = bullets(sec("OPEN QUESTIONS"))

    # ── Candidate problems ─────────────────────────────────────────────────────
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

    return d


def _parse_landscape(landscape, d):
    """Parse ## INDUSTRY LANDSCAPE subsections as role research fallback."""
    skip_markers = ('eliminated', 'context only', 'market dominated', 'narrative has shifted',
                    'very crowded')
    for rs in re.split(r'\n### ', '\n' + landscape):
        if not rs.strip():
            continue
        lines = rs.strip().split('\n')
        rname = lines[0].strip()
        content_head = '\n'.join(lines[1:4]).lower()
        if any(m in rname.lower() or m in content_head for m in skip_markers):
            continue

        rd = {"status": "done", "goals": [], "success": [], "pain_points": [],
              "workarounds": [], "tech_narratives": [], "tam": [],
              "user_challenges": [], "open_questions": []}
        cur = None
        for ln in lines[1:]:
            s = ln.strip()
            if ':' in s and not s.startswith(('-', '*', '  ')):
                k, _, v = s.partition(':')
                kl = k.strip().lower()
                v = v.strip()
                if kl == 'goals':
                    if v: rd["goals"].extend(x.strip() for x in v.split(';') if x.strip())
                    cur = rd["goals"]
                elif 'workaround' in kl:
                    if v: rd["workarounds"].extend(x.strip() for x in v.split(';') if x.strip())
                    cur = rd["workarounds"]
                elif 'pain signal' in kl or 'pain point' in kl: cur = rd["pain_points"]
                elif 'incumbent gap' in kl:                       cur = rd["pain_points"]
                elif 'recent shift' in kl:
                    if v: rd["tech_narratives"].extend(x.strip() for x in v.split(';') if x.strip())
                    cur = rd["tech_narratives"]
                elif 'tech narrative' in kl: cur = rd["tech_narratives"]
                elif kl.startswith('tam') or 'market size' in kl:
                    if v: rd["tam"].append(v)
                    cur = rd["tam"]
                else: cur = None
            elif s.startswith(('- ', '  - ', '* ')) and cur is not None:
                v = s.lstrip(' -*').strip()
                if v and '[PENDING]' not in v:
                    cur.append(v)
        d["role_research"][rname] = rd


# ── Orbit / angle assignment ──────────────────────────────────────────────────
ORBIT_1_CATS = {'professional', 'life', 'health'}

def assign_positions(roles):
    orbit1 = [r for r in roles if r['category'].lower().split('/')[0].strip() in ORBIT_1_CATS]
    orbit2 = [r for r in roles if r['category'].lower().split('/')[0].strip() not in ORBIT_1_CATS]
    pos = {}
    n1 = max(len(orbit1), 1)
    for i, r in enumerate(orbit1):
        pos[r['name']] = {'orbit': 1, 'angle': round((90 + i * 360 / n1) % 360)}
    n2 = max(len(orbit2), 1)
    for i, r in enumerate(orbit2):
        pos[r['name']] = {'orbit': 2, 'angle': round((30 + i * 360 / n2) % 360)}
    return pos


# ── Data mapping ──────────────────────────────────────────────────────────────
def build_persona(d):
    p = d["profile"]
    meta = d["meta"]
    age_raw = p.get("age", "")
    age = int(age_raw) if re.match(r'^\d+$', age_raw) else None

    # Format date nicely if it's YYYY-MM-DD
    date_raw = meta.get("date", "")
    try:
        from datetime import datetime
        date_fmt = datetime.strptime(date_raw, "%Y-%m-%d").strftime("%B %d, %Y")
    except Exception:
        date_fmt = date_raw

    return {
        "name":           p.get("name", "Founder"),
        "age":            age,
        "location":       p.get("location_current", p.get("location", "")),
        "epigraph":       p.get("epigraph", p.get("tagline", "")),
        "interviewedOn":  date_fmt,
        "interviewLength": p.get("interview_length", f"Round {meta.get('round', '1')} of 3"),
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

        # goal: goals + success joined into one paragraph
        goal = " ".join(rr.get("goals", []) + rr.get("success", []))

        # practice: workarounds = how the role is done today
        practice = rr.get("workarounds", [])

        # problems
        personal   = rr.get("user_challenges", [])
        researched = [{"text": p, "source": "Research"}
                      for p in rr.get("pain_points", [])]

        # narratives: optional TAM note first, then tech narratives
        narratives = []
        tam = rr.get("tam", [])
        if tam:
            narratives.append(tam[0])
        narratives.extend(rr.get("tech_narratives", []))

        # open questions: per-role if available, else empty
        open_qs = rr.get("open_questions", [])

        # intensity: rough default by category
        cat = r['category'].lower()
        if any(x in cat for x in ('seasonal', 'winter')):
            intensity = "seasonal"
        elif any(x in cat for x in ('social', 'community')):
            intensity = "weekly"
        else:
            intensity = "daily"

        # shortLabel: first word if meaningful
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
            "openQuestions": open_qs,
        })
    return out


def build_network(d, role_ids):
    out = []
    for c in d["network_contacts"]:
        name = c.get("Name", "").strip()
        if not name or name.startswith(('[', '|')):
            continue

        # Parse Role Overlap → matching role ids
        overlap_ids = []
        overlap_raw = c.get("Role Overlap", "")
        if overlap_raw and not overlap_raw.startswith('['):
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
            "roles":        [does] if does and not does.startswith('[') else [],
            "overlapsWith": overlap_ids,
            "note":         note,
        })
    return out


# ── data.jsx writer ───────────────────────────────────────────────────────────
def generate_data_jsx(d, raw_text):
    persona  = build_persona(d)
    roles    = build_roles(d)
    role_ids = [r["id"] for r in roles]
    network  = build_network(d, role_ids)

    def str_list(lst, indent=6):
        if not lst:
            return "[]"
        pad = " " * indent
        items = (",\n" + pad).join(js_str(x) for x in lst)
        return "[\n" + pad + items + ",\n" + " " * (indent - 2) + "]"

    L = []
    L.append("/* data.jsx — auto-generated from discovery.md by scripts/render.py")
    L.append("   Edit discovery.md, then run:  python3 scripts/render.py")
    L.append("   Do not edit this file by hand. */\n")

    # PERSONA
    L.append("const PERSONA = {")
    L.append(f"  name: {js_str(persona['name'])},")
    if persona['age'] is not None:
        L.append(f"  age: {persona['age']},")
    L.append(f"  location: {js_str(persona['location'])},")
    L.append(f"  epigraph: {js_str(persona['epigraph'])},")
    L.append(f"  interviewedOn: {js_str(persona['interviewedOn'])},")
    L.append(f"  interviewLength: {js_str(persona['interviewLength'])},")
    L.append("};\n")

    # ROLES
    L.append("const ROLES = [")
    for r in roles:
        L.append("  {")
        L.append(f"    id: {js_str(r['id'])},")
        L.append(f"    label: {js_str(r['label'])},")
        L.append(f"    shortLabel: {js_str(r['shortLabel'])},")
        L.append(f"    sublabel: {js_str(r['sublabel'])},")
        L.append(f"    angle: {r['angle']},")
        L.append(f"    orbit: {r['orbit']},")
        L.append(f"    intensity: {js_str(r['intensity'])},")
        L.append(f"    goal: {js_str(r['goal'])},")
        L.append(f"    practice: {str_list(r['practice'])},")
        L.append("    problems: {")
        L.append(f"      personal: {str_list(r['problems']['personal'], 8)},")
        if r['problems']['researched']:
            items = (",\n        ").join(
                "{{ text: {}, source: {} }}".format(js_str(x['text']), js_str(x['source']))
                for x in r['problems']['researched']
            )
            L.append(f"      researched: [\n        {items},\n      ],")
        else:
            L.append("      researched: [],")
        L.append("    },")
        L.append(f"    narratives: {str_list(r['narratives'])},")
        L.append(f"    openQuestions: {str_list(r['openQuestions'])},")
        L.append("  },")
    L.append("];\n")

    # NETWORK
    L.append("const NETWORK = [")
    for c in network:
        L.append("  {")
        L.append(f"    id: {js_str(c['id'])},")
        L.append(f"    name: {js_str(c['name'])},")
        L.append(f"    relation: {js_str(c['relation'])},")
        L.append(f"    distance: {c['distance']},")
        L.append(f"    roles: {str_list(c['roles'])},")
        if c['overlapsWith']:
            L.append(f"    overlapsWith: [{', '.join(js_str(x) for x in c['overlapsWith'])}],")
        else:
            L.append("    overlapsWith: [],")
        L.append(f"    note: {js_str(c['note'])},")
        L.append("  },")
    L.append("];\n")

    # DISCOVERY_DOC
    L.append("const DISCOVERY_DOC = `" + escape_tl(raw_text) + "`;\n")
    L.append("Object.assign(window, { PERSONA, ROLES, NETWORK, DISCOVERY_DOC });")
    return "\n".join(L)


# ── Entry point ───────────────────────────────────────────────────────────────
def main():
    inp = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_OUTPUT

    if not inp.exists():
        print(f"Error: {inp} not found", file=sys.stderr)
        sys.exit(1)

    raw = inp.read_text(encoding='utf-8')
    d   = parse_document(raw)
    out.write_text(generate_data_jsx(d, raw), encoding='utf-8')
    print(f"✓ {inp.name} → {out}")

if __name__ == "__main__":
    main()
