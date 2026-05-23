#!/usr/bin/env python3
"""
Problem Finder — Discovery Document HTML Renderer
Summary-first: main takeaways always visible, full data in expandable sections.
Usage: python3 render.py [input.md] [output.html]
"""
import sys, re
from pathlib import Path
from datetime import datetime
from html import escape as esc

CAT_COLORS = {
    'professional': {'bg':'#EFF6FF','bdr':'#93C5FD','txt':'#1E40AF','dot':'#2563EB','lbl':'Professional'},
    'hobby':        {'bg':'#F0FDF4','bdr':'#86EFAC','txt':'#166534','dot':'#16A34A','lbl':'Hobby'},
    'life':         {'bg':'#FFF7ED','bdr':'#FDBA74','txt':'#9A3412','dot':'#EA580C','lbl':'Life'},
    'family':       {'bg':'#FAF5FF','bdr':'#C4B5FD','txt':'#5B21B6','dot':'#7C3AED','lbl':'Family'},
    'social':       {'bg':'#ECFEFF','bdr':'#67E8F9','txt':'#164E63','dot':'#0891B2','lbl':'Social'},
    'health':       {'bg':'#FEF2F2','bdr':'#FECACA','txt':'#991B1B','dot':'#DC2626','lbl':'Health'},
    'community':    {'bg':'#FFFBEB','bdr':'#FDE68A','txt':'#92400E','dot':'#D97706','lbl':'Community'},
}
DEF_CAT = {'bg':'#F9FAFB','bdr':'#D1D5DB','txt':'#374151','dot':'#6B7280','lbl':'Other'}

def cat_style(s):
    return CAT_COLORS.get((s or '').strip().lower().split('/')[0], DEF_CAT)

def safe_id(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

# ── Parser ────────────────────────────────────────────────────────────────────
def parse_document(text):
    d = {
        "meta": {"version":"1","date":"","round":"1"},
        "profile": {}, "education": [], "work_history": [],
        "relationships": {}, "hobbies": [], "consumer_frustrations": [],
        "active_problems": [], "roles": [], "role_research": {},
        "tech_breakthroughs": [], "candidate_problems": [],
        "network_contacts": [], "open_questions": [],
    }
    m = re.search(r'version:\s*(\d+)\s*\|\s*date:\s*([^|]+)\s*\|\s*round:\s*(\d+)', text)
    if m:
        d["meta"] = {"version":m.group(1),"date":m.group(2).strip(),"round":m.group(3)}

    def sec(name):
        pat = r'\n## ' + re.escape(name) + r'\s*\n(.*?)(?=\n## |\Z)'
        x = re.search(pat, text, re.DOTALL | re.IGNORECASE)
        return x.group(1).strip() if x else ""

    def bullets(t):
        out = []
        for ln in t.split('\n'):
            ln = ln.strip()
            if ln.startswith(('- ','* ','• ')):
                v = ln[2:].strip()
                if v and '[PENDING]' not in v: out.append(v)
        return out

    def all_bullets(t):
        """Include pending items too, for completeness checks"""
        out = []
        for ln in t.split('\n'):
            ln = ln.strip()
            if ln.startswith(('- ','* ','• ')): out.append(ln[2:].strip())
        return [x for x in out if x]

    def parse_table(t):
        rows, headers = [], []
        for ln in t.split('\n'):
            ln = ln.strip()
            if not ln.startswith('|'): continue
            cells = [c.strip() for c in ln.strip('|').split('|')]
            if not headers: headers = cells; continue
            if all(re.match(r'^[-: ]+$', c) for c in cells if c): continue
            rows.append(dict(zip(headers, cells)))
        return rows

    for ln in sec("PROFILE").split('\n'):
        if ':' in ln and not ln.strip().startswith('-'):
            k, _, v = ln.partition(':')
            k = k.strip().lower().replace(' ','_'); v = v.strip()
            if k and v and not v.startswith('[') and v != '[PENDING]':
                d["profile"][k] = v

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
        if ':' in ln and not ln.startswith('-'):
            k, _, v = ln.partition(':')
            if k.strip() and v.strip() and not v.strip().startswith('['):
                rel[k.strip()] = v.strip()
    rel['_bullets'] = bullets(rel_text)
    d["relationships"] = rel

    for row in parse_table(sec("ROLES LIST")):
        name = row.get('Role','')
        if name and not name.startswith('['):
            d["roles"].append({
                "name": name, "category": row.get('Category',''),
                "emoji": row.get('Emoji','◆'),
                "how": row.get('How Identified', row.get('What it gives you','')),
            })

    for rs in re.split(r'\n### ', '\n' + sec("ROLE RESEARCH")):
        if not rs.strip(): continue
        lines = rs.strip().split('\n')
        rname = lines[0].strip()
        rd = {"status":"pending","goals":[],"success":[],"pain_points":[],
              "workarounds":[],"tech_narratives":[],"tam":[],"user_challenges":[]}
        cur = None
        for ln in lines[1:]:
            s = ln.strip(); sl = s.lower()
            if sl.startswith('research status:'): rd["status"] = s.split(':',1)[1].strip()
            elif sl == 'goals:': cur = rd["goals"]
            elif sl.startswith('success looks like'): cur = rd["success"]
            elif sl.startswith('pain point'): cur = rd["pain_points"]
            elif sl.startswith('workaround'): cur = rd["workarounds"]
            elif sl.startswith('tech narrative'): cur = rd["tech_narratives"]
            elif sl.startswith('tam') or sl.startswith('market size'): cur = rd["tam"]
            elif sl.startswith('user') and ('challenge' in sl or 'personal' in sl): cur = rd["user_challenges"]
            elif s.startswith(('- ','* ','• ')) and cur is not None:
                v = s[2:].strip()
                if v and '[PENDING]' not in v: cur.append(v)
        d["role_research"][rname] = rd

    for block in re.split(r'\n### Problem\s*\d*\s*:', '\n' + sec("CANDIDATE PROBLEMS")):
        if not block.strip(): continue
        lines = block.strip().split('\n')
        name = lines[0].strip().lstrip('0123456789. ')
        details = {}
        for ln in lines[1:]:
            if ':' in ln:
                k, _, v = ln.strip().partition(':')
                details[k.strip().lower()] = v.strip()
        if name: d["candidate_problems"].append({"name":name,"details":details})

    d["network_contacts"] = [
        row for row in parse_table(sec("NETWORK CONTACTS"))
        if row.get('Name') and not row.get('Name','').startswith('[')
    ]
    return d

# ── HTML primitives ───────────────────────────────────────────────────────────
def blist(items):
    if not items: return ''
    return '<ul class="blist">' + ''.join('<li>' + esc(i) + '</li>' for i in items if i) + '</ul>'

def empty_state(msg):
    return '<p class="muted-hint">' + esc(msg) + '</p>'

def details_block(summary_label, count_badge, body_html, open_by_default=False):
    """Expandable section using native <details>/<summary>"""
    count_html = (' <span class="det-count">' + str(count_badge) + '</span>') if count_badge else ''
    open_attr = ' open' if open_by_default else ''
    return (
        '<details class="det-block"' + open_attr + '>'
        + '<summary class="det-summary">'
        + '<span class="det-label">' + esc(summary_label) + count_html + '</span>'
        + '<span class="det-arrow">›</span>'
        + '</summary>'
        + '<div class="det-body">' + body_html + '</div>'
        + '</details>'
    )

def takeaway_line(icon, label, value, cls=''):
    if not value: return ''
    return (
        '<div class="takeaway-row ' + cls + '">'
        + '<span class="ta-icon">' + icon + '</span>'
        + '<span class="ta-label">' + esc(label) + '</span>'
        + '<span class="ta-val">' + esc(value) + '</span>'
        + '</div>'
    )

# ── Tab: You ──────────────────────────────────────────────────────────────────
def tab_you(d):
    p = d["profile"]

    # Compact profile bar
    profile_parts = []
    for k, lbl in [('name',''),('age',''),('gender',''),('location_current','📍')]:
        v = p.get(k,'')
        if v:
            profile_parts.append(('<span class="prof-sep">·</span>' if profile_parts and not lbl else '') + ('<span class="prof-icon">' + lbl + '</span>' if lbl else '') + esc(v))
    profile_bar = ('<div class="profile-bar">' + ' '.join(profile_parts) + '</div>') if profile_parts else empty_state("Start the interview to build your profile.")

    roles = d["roles"]; n_c = len(d["network_contacts"]); n_o = len(d["candidate_problems"])
    stats_bar = (
        '<div class="stats-bar">'
        + '<span class="stat-chip">' + str(len(roles)) + ' roles</span>'
        + '<span class="stat-chip">' + str(n_c) + ' contacts</span>'
        + '<span class="stat-chip">' + str(n_o) + ' opportunities</span>'
        + '</div>'
    )

    # Active problems — always visible (these are the founder's own pains)
    ap = d["active_problems"]
    ap_html = (
        '<div class="card">'
        + '<h3 class="card-title">🔧 Active Problems <span class="card-sub-hint">what you\'re already trying to solve</span></h3>'
        + (blist(ap) if ap else empty_state("What are you actively trying to solve right now? (Block 10)"))
        + '</div>'
    )

    # Education + Work — expandable
    edu_work = (
        (blist(d["education"]) or empty_state("Education not yet captured (Block 2)"))
        + '<h4 class="det-inner-title">💼 Work History</h4>'
        + (blist(d["work_history"]) or empty_state("Work history not yet captured (Block 3)"))
    )
    edu_det = details_block("🎓 Education & Work Background", None, edu_work)

    # Hobbies + Frustrations — expandable
    hobby_frust = (
        (blist(d["hobbies"]) or empty_state("Hobbies not yet captured (Block 8)"))
        + '<h4 class="det-inner-title">😤 Consumer Frustrations</h4>'
        + (blist(d["consumer_frustrations"]) or empty_state("Frustrations not yet captured (Block 9)"))
    )
    hobby_det = details_block("🎯 Hobbies, Interests & Frustrations", None, hobby_frust)

    # Relationships — expandable
    rel = d["relationships"]
    rel_parts = [('<strong>' + esc(k) + ':</strong> ' + esc(v)) for k,v in rel.items() if k != '_bullets' and v]
    rel_parts += [esc(b) for b in rel.get('_bullets',[])]
    rel_html = ('<ul class="blist">' + ''.join('<li>' + x + '</li>' for x in rel_parts) + '</ul>') if rel_parts else empty_state("Relationships not yet captured (Block 7)")
    rel_det = details_block("💬 Relationships & Family", None, rel_html)

    # Roles mini-grid — always visible
    if roles:
        mini = []
        for r in roles:
            cs = cat_style(r['category']); sid = safe_id(r['name'])
            mini.append(
                '<div class="mini-role" style="background:' + cs['bg'] + ';border-color:' + cs['bdr'] + ';" onclick="switchToRoles(\'' + sid + '\')">'
                + '<span class="mini-emoji">' + esc(r['emoji']) + '</span>'
                + '<div><div class="mini-name">' + esc(r['name']) + '</div>'
                + '<div class="mini-cat" style="color:' + cs['txt'] + '">' + esc(cs['lbl']) + '</div></div></div>'
            )
        roles_html = '<div class="mini-roles-grid">' + ''.join(mini) + '</div>'
    else:
        roles_html = empty_state("Roles not yet mapped — complete Block 11 to build your Roles List.")

    return (
        '<div class="tab-section">'
        + '<div class="card">'
        + '<h3 class="card-title">👤 Founder</h3>'
        + profile_bar + stats_bar
        + '</div>'
        + ap_html
        + '<div class="card detblocks">' + edu_det + hobby_det + rel_det + '</div>'
        + '<div class="card">'
        + '<h3 class="card-title">🎭 Your Roles <span class="count-chip">' + str(len(roles)) + '</span></h3>'
        + '<p class="card-sub-hint">Every role is a market you understand from the inside. Click to explore in the Roles tab.</p>'
        + roles_html + '</div>'
        + '</div>'
    )

# ── Tab: Roles ────────────────────────────────────────────────────────────────
def tab_roles(d):
    roles = d["roles"]; research = d["role_research"]
    if not roles:
        return '<div class="tab-section"><div class="card">' + empty_state("Complete the founder interview to build your Roles List.") + '</div></div>'

    cards = []
    for r in roles:
        cs = cat_style(r['category']); sid = safe_id(r['name'])
        rr = research.get(r['name'], {})
        rn = r['name']
        status = rr.get('status','pending')
        status_dot = ('🟢' if status == 'done' else '🟡') + ' ' + status.capitalize()

        # ── Summary takeaways (always visible) ──
        top_pain = rr.get("pain_points",[''])[0] if rr.get("pain_points") else None
        top_tam  = rr.get("tam",[''])[0] if rr.get("tam") else None
        top_work = rr.get("workarounds",[''])[0] if rr.get("workarounds") else None

        pain_line = takeaway_line('🔥', 'Top pain:', top_pain, 'ta-pain') if top_pain else ''
        tam_line  = takeaway_line('📊', 'Market:', top_tam) if top_tam else ''
        work_line = takeaway_line('🔧', 'Today\'s fix:', top_work, 'ta-work') if top_work else ''

        no_takeaways = not (top_pain or top_tam or top_work)
        if no_takeaways:
            takeaway_html = empty_state("Research pending — type /dig " + rn + " to explore this role")
        else:
            takeaway_html = '<div class="takeaway-block">' + pain_line + tam_line + work_line + '</div>'

        # ── Expandable: Goals & Pain ──
        goals_pain = ''
        if rr.get("goals"):
            goals_pain += '<h4 class="det-inner-title">🎯 Goals</h4>' + blist(rr["goals"])
        if rr.get("success"):
            goals_pain += '<h4 class="det-inner-title">✅ Success looks like</h4>' + blist(rr["success"])
        if rr.get("pain_points"):
            goals_pain += '<h4 class="det-inner-title">🔥 All Pain Points</h4>' + blist(rr["pain_points"])
        gp_det = details_block("Goals & Pain Points", len(rr.get("pain_points",[])) or None, goals_pain or empty_state("Research not yet done for this role."))

        # ── Expandable: Workarounds & Tech ──
        work_tech = ''
        if rr.get("workarounds"):
            work_tech += '<h4 class="det-inner-title">🔧 Current Workarounds</h4>' + blist(rr["workarounds"])
        if rr.get("tech_narratives"):
            work_tech += '<h4 class="det-inner-title">💡 New Tech & Narratives</h4>' + blist(rr["tech_narratives"])
        wt_det = details_block("Workarounds & Tech Opportunity", None, work_tech or empty_state("Type /dig " + rn + " to explore workarounds and tech angles."))

        # ── Expandable: Your Experience ──
        exp_html = blist(rr.get("user_challenges",[])) or empty_state("Which of these pains do YOU personally experience? Rate each 1–5 (Block 3 of interview).")
        exp_det = details_block("Your Personal Experience", None, exp_html)

        # ── Card assembly ──
        cards.append(
            '<div class="role-card" id="role-' + sid + '">'
            + '<div class="rc-header" style="background:' + cs['bg'] + ';border-color:' + cs['bdr'] + '">'
            + '<span class="rc-emoji">' + esc(r['emoji']) + '</span>'
            + '<div class="rc-meta">'
            + '<h3 class="rc-name">' + esc(rn) + '</h3>'
            + '<div class="rc-badges">'
            + '<span class="cat-badge" style="background:' + cs['bg'] + ';color:' + cs['txt'] + ';border-color:' + cs['bdr'] + '">' + esc(cs['lbl']) + '</span>'
            + '<span class="status-pill">' + status_dot + '</span>'
            + '</div>'
            + (('<p class="rc-insight">' + esc(r["how"]) + '</p>') if r.get("how") and not r["how"].startswith("[") else '')
            + '</div></div>'
            + '<div class="rc-body">'
            + takeaway_html
            + '<div class="rc-details">' + gp_det + wt_det + exp_det + '</div>'
            + '</div>'
            + '</div>'
        )

    return (
        '<div class="tab-section">'
        + '<div class="roles-grid">' + ''.join(cards) + '</div>'
        + '</div>'
    )

# ── Tab: Network ──────────────────────────────────────────────────────────────
def tab_network(d):
    contacts = d["network_contacts"]

    def filled_card(c):
        name = c.get('Name',''); how = c.get('How You Know Them','')
        does = c.get('What They Do',''); overlap = c.get('Role Overlap','')
        iv = c.get('Interviewed?','No')
        init = (name[0] if name else '?').upper()
        interviewed = str(iv).lower() in ('yes','y','done')
        badge = ('<span class="badge badge-green">Interviewed ✓</span>' if interviewed else '<span class="badge badge-gray">Not yet</span>')
        role_html = ('<div class="contact-role">' + esc(does) + '</div>') if does and not does.startswith('[') else ''
        known_html = ('<div class="contact-known">' + esc(how) + '</div>') if how and not how.startswith('[') else ''
        overlap_html = ('<div class="contact-overlap">↔ ' + esc(overlap) + '</div>') if overlap and not overlap.startswith('[') else ''
        return (
            '<div class="contact-card' + (' contact-done' if interviewed else '') + '">'
            + '<div class="contact-avatar">' + esc(init) + '</div>'
            + '<div class="contact-info">'
            + '<div class="contact-name">' + esc(name) + '</div>'
            + role_html + known_html + overlap_html + badge
            + '</div></div>'
        )

    def empty_slot(n):
        return (
            '<div class="contact-card contact-empty">'
            + '<div class="contact-avatar contact-avatar-empty">' + str(n) + '</div>'
            + '<div class="contact-info">'
            + '<div class="contact-name contact-empty-name">Contact ' + str(n) + '</div>'
            + '<div class="contact-known">Answer Block 13 to add</div>'
            + '</div></div>'
        )

    cards = [filled_card(c) for c in contacts]
    while len(cards) < 5: cards.append(empty_slot(len(cards)+1))

    interviewed_count = sum(1 for c in contacts if str(c.get('Interviewed?','')).lower() in ('yes','y','done'))

    return (
        '<div class="tab-section">'
        + '<div class="card">'
        + '<h3 class="card-title">🤝 Interview Network <span class="count-chip">' + str(len(contacts)) + ' added · ' + str(interviewed_count) + ' interviewed</span></h3>'
        + '<p class="card-sub-hint">Each person is a potential customer discovery interview. Aim for 5+ honest conversations.</p>'
        + '</div>'
        + '<div class="contacts-grid">' + ''.join(cards) + '</div>'
        + '</div>'
    )

# ── Tab: Opportunities ────────────────────────────────────────────────────────
def tab_opps(d):
    problems = d["candidate_problems"]; oq = d["open_questions"]
    if not problems:
        return '<div class="tab-section"><div class="card">' + empty_state("Opportunity ranking appears here after research + challenge interview phases.") + '</div></div>'

    def snum(s):
        try: return int(re.sub(r'[^0-9]','',s.split('/')[0]))
        except: return 0

    cards = []
    for p in sorted(problems, key=lambda x: snum(x['details'].get('score','')), reverse=True):
        det = p['details']
        score = det.get('score',''); status = det.get('status','ACTIVE')
        persona = det.get('persona',''); pain = det.get('pain moment', det.get('pain_moment',''))
        wa = det.get('workaround','')
        sn = snum(score); active = 'active' in status.lower()
        sc = '#16A34A' if sn >= 35 else '#EA580C' if sn >= 20 else '#94A3B8'

        score_badge = ('<span class="score-badge" style="color:' + sc + ';border-color:' + sc + '">' + esc(score) + '</span>') if score else ''
        status_badge = '<span class="badge ' + ('badge-green' if active else 'badge-red') + '">' + esc(status) + '</span>'

        # Always-visible: name + score + top pain
        summary_html = ''
        if pain and not pain.startswith('['):
            summary_html = '<p class="opp-pain">🔥 ' + esc(pain) + '</p>'
        elif persona and not persona.startswith('['):
            summary_html = '<p class="opp-pain">' + esc(persona) + '</p>'

        # Expandable: full details
        full_html = ''
        if persona and not persona.startswith('['):
            full_html += '<p class="problem-detail"><strong>Persona:</strong> ' + esc(persona) + '</p>'
        if pain and not pain.startswith('['):
            full_html += '<p class="problem-detail"><strong>Pain moment:</strong> ' + esc(pain) + '</p>'
        if wa and not wa.startswith('['):
            full_html += '<p class="problem-detail"><strong>Workaround:</strong> ' + esc(wa) + '</p>'
        detail_det = details_block("Full scoring details", None, full_html or empty_state("Scoring details not yet captured.")) if full_html else ''

        cards.append(
            '<div class="problem-card ' + ('problem-eliminated' if not active else '') + '">'
            + '<div class="problem-header">'
            + '<h3 class="problem-name">' + esc(p["name"]) + '</h3>'
            + '<div class="problem-badges">' + score_badge + status_badge + '</div>'
            + '</div>'
            + summary_html
            + detail_det
            + '</div>'
        )

    oq_html = ''
    if oq:
        oq_html = '<div class="card"><h3 class="card-title">❓ Open Questions</h3>' + blist(oq) + '</div>'

    return (
        '<div class="tab-section">'
        + '<div class="problems-list">' + ''.join(cards) + '</div>'
        + oq_html
        + '</div>'
    )

# ── Styles ────────────────────────────────────────────────────────────────────
CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#F1F5F9;color:#0F172A;font-size:14px;line-height:1.6}
.header{background:#fff;border-bottom:1px solid #E2E8F0;padding:14px 28px;position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.header-title{font-size:17px;font-weight:800}.header-title span{color:#2563EB}
.header-meta{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.badge{display:inline-flex;align-items:center;padding:3px 9px;border-radius:99px;font-size:11px;font-weight:600;border:1px solid transparent}
.badge-blue{background:#EFF6FF;color:#1E40AF;border-color:#BFDBFE}
.badge-green{background:#F0FDF4;color:#166534;border-color:#86EFAC}
.badge-gray{background:#F9FAFB;color:#374151;border-color:#D1D5DB}
.badge-red{background:#FEF2F2;color:#991B1B;border-color:#FECACA}
.tabs{background:#fff;border-bottom:1px solid #E2E8F0;display:flex;padding:0 28px;position:sticky;top:55px;z-index:99;overflow-x:auto}
.tab{padding:11px 18px;cursor:pointer;font-size:13px;font-weight:500;color:#64748B;border-bottom:2px solid transparent;white-space:nowrap;transition:color .15s,border-color .15s;user-select:none}
.tab:hover{color:#0F172A}.tab.active{color:#2563EB;border-bottom-color:#2563EB}
.tab-content{display:none}.tab-content.active{display:block}
.tab-section{max-width:960px;margin:0 auto;padding:24px;display:flex;flex-direction:column;gap:16px}
.card{background:#fff;border:1px solid #E2E8F0;border-radius:12px;padding:20px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.card-title{font-size:14px;font-weight:700;margin-bottom:10px;display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.card-sub-hint{font-size:12px;color:#94A3B8;margin-bottom:10px}
.count-chip{background:#F1F5F9;color:#64748B;font-size:11px;font-weight:600;padding:1px 7px;border-radius:99px;margin-left:4px}
.muted-hint{color:#94A3B8;font-size:13px;font-style:italic}
.blist{padding-left:18px;display:flex;flex-direction:column;gap:4px}.blist li{font-size:13px;color:#334155;line-height:1.5}
/* Profile bar */
.profile-bar{font-size:16px;font-weight:600;color:#0F172A;margin-bottom:10px;display:flex;flex-wrap:wrap;gap:6px;align-items:center}
.prof-sep{color:#CBD5E1;font-weight:300}.prof-icon{margin-right:2px}
.stats-bar{display:flex;gap:8px;flex-wrap:wrap}
.stat-chip{background:#F8FAFC;border:1px solid #E2E8F0;border-radius:99px;padding:3px 10px;font-size:12px;font-weight:600;color:#64748B}
/* Mini roles grid */
.mini-roles-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px;margin-top:12px}
.mini-role{border:1.5px solid;border-radius:8px;padding:10px 12px;cursor:pointer;display:flex;align-items:center;gap:10px;transition:transform .1s,box-shadow .1s}
.mini-role:hover{transform:translateY(-1px);box-shadow:0 3px 10px rgba(0,0,0,.08)}
.mini-emoji{font-size:20px;flex-shrink:0}.mini-name{font-size:13px;font-weight:700}.mini-cat{font-size:11px;font-weight:500}
/* Details / expandable */
.detblocks{padding:0;overflow:hidden}
.det-block{border:none;border-top:1px solid #F1F5F9}
.det-block:first-child{border-top:none}
details.det-block summary{padding:14px 20px;cursor:pointer;display:flex;align-items:center;justify-content:space-between;list-style:none;user-select:none;background:#fff;transition:background .1s}
details.det-block summary:hover{background:#F8FAFC}
details.det-block[open]>summary{background:#F8FAFC;border-bottom:1px solid #E2E8F0}
details.det-block summary::-webkit-details-marker{display:none}
.det-label{font-size:13px;font-weight:600;color:#334155;display:flex;align-items:center;gap:6px}
.det-count{background:#EFF6FF;color:#2563EB;font-size:10px;font-weight:700;padding:1px 6px;border-radius:99px}
.det-arrow{font-size:16px;color:#94A3B8;transition:transform .2s;display:inline-block}
details.det-block[open] .det-arrow{transform:rotate(90deg)}
.det-body{padding:16px 20px;background:#fff}
.det-inner-title{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#94A3B8;margin:14px 0 6px}
.det-inner-title:first-child{margin-top:0}
/* Roles grid */
.roles-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(420px,1fr));gap:16px}
@media(max-width:500px){.roles-grid{grid-template-columns:1fr}}
.role-card{background:#fff;border:1px solid #E2E8F0;border-radius:12px;overflow:hidden;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.rc-header{display:flex;align-items:flex-start;gap:12px;padding:16px;border-bottom:1px solid}
.rc-emoji{font-size:32px;line-height:1;flex-shrink:0}
.rc-meta{flex:1;min-width:0}
.rc-name{font-size:16px;font-weight:800;margin-bottom:4px}
.rc-badges{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:4px}
.cat-badge{display:inline-block;padding:2px 8px;border-radius:99px;font-size:11px;font-weight:600;border:1px solid}
.status-pill{font-size:11px;color:#64748B}
.rc-insight{font-size:12px;color:#64748B;margin-top:2px}
.rc-body{padding:0}
/* Takeaway block */
.takeaway-block{padding:14px 16px;border-bottom:1px solid #F1F5F9;display:flex;flex-direction:column;gap:6px}
.takeaway-row{display:flex;align-items:flex-start;gap:8px;font-size:13px}
.ta-icon{flex-shrink:0;width:18px;text-align:center}
.ta-label{color:#94A3B8;flex-shrink:0;min-width:70px}
.ta-val{color:#0F172A;flex:1}
.ta-pain .ta-val{font-weight:600}
.rc-details{border-top:1px solid #F1F5F9}
/* Role details use same det-block style but no border-radius */
.rc-details .det-block{border-top:1px solid #F1F5F9}
.rc-details .det-block:first-child{border-top:none}
.rc-details details.det-block summary{padding:12px 16px}
.rc-details .det-body{padding:12px 16px}
/* Network */
.contacts-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:12px}
.contact-card{background:#fff;border:1px solid #E2E8F0;border-radius:10px;padding:14px;display:flex;gap:12px;align-items:flex-start;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.contact-card.contact-empty{border-style:dashed;background:#F8FAFC}
.contact-card.contact-done{border-color:#86EFAC;background:#FAFFFE}
.contact-avatar{width:40px;height:40px;border-radius:50%;background:#2563EB;color:#fff;font-size:16px;font-weight:800;flex-shrink:0;display:flex;align-items:center;justify-content:center}
.contact-avatar-empty{background:#E2E8F0;color:#94A3B8}
.contact-name{font-size:14px;font-weight:700;margin-bottom:2px}.contact-empty-name{color:#94A3B8}
.contact-role{font-size:12px;color:#334155;margin-bottom:2px}
.contact-known{font-size:11px;color:#94A3B8;font-style:italic;margin-bottom:4px}
.contact-overlap{font-size:11px;color:#64748B;margin-bottom:4px}
/* Opportunities */
.problems-list{display:flex;flex-direction:column;gap:12px}
.problem-card{background:#fff;border:1px solid #E2E8F0;border-radius:12px;padding:16px;box-shadow:0 1px 2px rgba(0,0,0,.04)}
.problem-eliminated{opacity:.5}
.problem-header{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:8px}
.problem-name{font-size:15px;font-weight:700}
.problem-badges{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end;flex-shrink:0}
.score-badge{padding:2px 9px;border-radius:99px;font-size:12px;font-weight:800;border:1.5px solid}
.opp-pain{font-size:13px;color:#334155;margin-bottom:8px}
.problem-detail{font-size:13px;color:#64748B;margin-top:5px}.problem-detail strong{color:#334155}
/* Footer note */
.doc-footer{text-align:center;padding:24px;color:#CBD5E1;font-size:12px}
.doc-footer code{background:#F1F5F9;padding:2px 6px;border-radius:4px;font-size:11px;color:#64748B}
"""

JS = """
function switchTab(name,el){
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  el.classList.add('active');
}
function switchToRoles(sid){
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('tab-roles').classList.add('active');
  document.querySelectorAll('.tab')[1].classList.add('active');
  const card = document.getElementById('role-'+sid);
  if(card){ setTimeout(()=>card.scrollIntoView({behavior:'smooth',block:'start'}),50); }
}
"""

def generate_html(d):
    meta = d["meta"]
    name = d["profile"].get("name","Founder")
    n_roles = len(d["roles"]); n_c = len(d["network_contacts"]); n_o = len(d["candidate_problems"])
    date_str = meta.get("date") or datetime.now().strftime("%B %d, %Y")

    header = (
        '<div class="header">'
        + '<div class="header-title">🔍 Discovery — <span>' + esc(name) + '</span></div>'
        + '<div class="header-meta">'
        + '<span class="badge badge-blue">v' + esc(meta['version']) + ' · Round ' + esc(meta['round']) + '</span>'
        + '<span class="badge badge-gray">Updated ' + esc(date_str) + '</span>'
        + '</div></div>'
    )

    tabs = (
        '<div class="tabs">'
        + '<div class="tab active" onclick="switchTab(\'you\',this)">👤 You</div>'
        + '<div class="tab" onclick="switchTab(\'roles\',this)">🎭 Roles (' + str(n_roles) + ')</div>'
        + '<div class="tab" onclick="switchTab(\'network\',this)">🤝 Network (' + str(n_c) + ')</div>'
        + '<div class="tab" onclick="switchTab(\'opps\',this)">🚀 Opportunities (' + str(n_o) + ')</div>'
        + '</div>'
    )

    footer = '<div class="doc-footer">Full data, raw research & all questions → <code>~/problem-finder/discovery.md</code></div>'

    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        + '<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width,initial-scale=1.0">\n'
        + '<title>Discovery — ' + esc(name) + '</title>\n'
        + '<style>\n' + CSS + '\n</style>\n</head>\n<body>\n'
        + header + '\n' + tabs + '\n'
        + '<div id="tab-you" class="tab-content active">' + tab_you(d) + '</div>\n'
        + '<div id="tab-roles" class="tab-content">' + tab_roles(d) + '</div>\n'
        + '<div id="tab-network" class="tab-content">' + tab_network(d) + '</div>\n'
        + '<div id="tab-opps" class="tab-content">' + tab_opps(d) + '</div>\n'
        + footer + '\n'
        + '<script>\n' + JS + '\n</script>\n</body>\n</html>'
    )

def main():
    inp = Path(sys.argv[1]) if len(sys.argv)>1 else Path.home()/"problem-finder"/"discovery.md"
    out = Path(sys.argv[2]) if len(sys.argv)>2 else inp.with_suffix('.html')
    if not inp.exists(): print("Error: "+str(inp)+" not found",file=sys.stderr); sys.exit(1)
    text = inp.read_text(encoding='utf-8')
    html = generate_html(parse_document(text))
    out.write_text(html,encoding='utf-8')
    print("✓ Rendered → "+str(out))

if __name__=="__main__": main()
