#!/usr/bin/env python3
"""
Problem Finder — Discovery Document HTML Renderer
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
                out.append(ln[2:].strip())
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
            if k and v and not v.startswith('['): d["profile"][k] = v

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
            if k.strip() and v.strip() and not v.strip().startswith('['): rel[k.strip()] = v.strip()
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
            elif s.startswith(('- ','* ','• ')) and cur is not None: cur.append(s[2:].strip())
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

def pending_card(prompt, icon='⏳'):
    return '<div class="pending"><span class="pending-icon">' + icon + '</span><p class="pending-text">' + esc(prompt) + '</p></div>'

def blist(items):
    if not items: return ''
    lis = ''.join('<li>' + esc(i) + '</li>' for i in items if i)
    return '<ul class="blist">' + lis + '</ul>'

def sub_card(title, icon, items, empty_prompt, accent=''):
    border = 'border-left:3px solid ' + accent + ';' if accent else ''
    body = blist(items) if items else pending_card(empty_prompt)
    return '<div class="sub-card" style="' + border + '"><h4 class="sub-title">' + icon + ' ' + esc(title) + '</h4>' + body + '</div>'

def tab_you(d):
    p = d["profile"]
    fields = [(k,lbl) for k,lbl in [
        ('name','Name'),('age','Age'),('gender','Gender'),
        ('location_current','Location'),('location_grew_up','Grew up')] if p.get(k)]
    if fields:
        profile_html = '<div class="profile-grid">' + ''.join(
            '<div class="pfield"><span class="plabel">' + lbl + '</span><span class="pval">' + esc(p[k]) + '</span></div>'
            for k,lbl in fields) + '</div>'
    else:
        profile_html = pending_card("Start the interview to fill in your profile.")

    roles = d["roles"]
    if roles:
        mini = []
        for r in roles:
            cs = cat_style(r['category']); sid = safe_id(r['name'])
            mini.append(
                '<div class="mini-role" style="background:' + cs['bg'] + ';border-color:' + cs['bdr'] + ';" onclick="openRole(\'' + sid + '\')">'
                + '<span class="mini-emoji">' + esc(r['emoji']) + '</span>'
                + '<div><div class="mini-name">' + esc(r['name']) + '</div>'
                + '<div class="mini-cat" style="color:' + cs['txt'] + '">' + esc(cs['lbl']) + '</div></div></div>'
            )
        roles_html = '<div class="mini-roles-grid">' + ''.join(mini) + '</div>'
    else:
        roles_html = pending_card("Complete the interview to build your Roles List — every market you represent.")

    return (
        '<div class="tab-section">'
        + '<div class="card"><h3 class="card-title">👤 Profile</h3>' + profile_html + '</div>'
        + '<div class="two-col">'
        + '<div class="card"><h3 class="card-title">🎓 Education</h3>' + (blist(d["education"]) or pending_card("Share your educational background — schools, degrees, what you studied.")) + '</div>'
        + '<div class="card"><h3 class="card-title">💼 Work History</h3>' + (blist(d["work_history"]) or pending_card("Walk through your career — roles, industries, what you actually did.")) + '</div>'
        + '</div>'
        + '<div class="two-col">'
        + '<div class="card"><h3 class="card-title">😤 Consumer Frustrations</h3>' + (blist(d["consumer_frustrations"]) or pending_card("What do you pay for regularly that you're not happy with?")) + '</div>'
        + '<div class="card"><h3 class="card-title">🔧 Active Problems</h3>' + (blist(d["active_problems"]) or pending_card("What are you actively trying to solve right now, even informally?")) + '</div>'
        + '</div>'
        + '<div class="card">'
        + '<h3 class="card-title">🎭 Your Roles <span class="count-badge">' + str(len(roles)) + '</span></h3>'
        + '<p class="card-sub">Every role is a market you understand from the inside. Click any to explore.</p>'
        + roles_html + '</div>'
        + '</div>'
    )

def tab_roles(d):
    roles = d["roles"]; research = d["role_research"]
    if not roles:
        return '<div class="tab-section">' + pending_card("Complete the founder interview to build your Roles List.") + '</div>'

    pills = []
    for i, r in enumerate(roles):
        cs = cat_style(r['category']); sid = safe_id(r['name'])
        active_cls = 'pill-active' if i == 0 else ''
        pills.append(
            '<div class="role-pill ' + active_cls + '" id="pill-' + sid + '"'
            + ' style="--cat-bg:' + cs['bg'] + ';--cat-bdr:' + cs['bdr'] + ';--cat-txt:' + cs['txt'] + '"'
            + ' onclick="selectRole(\'' + sid + '\')">'
            + '<span>' + esc(r['emoji']) + '</span>'
            + '<span class="pill-name">' + esc(r['name']) + '</span></div>'
        )

    panels = []
    for i, r in enumerate(roles):
        cs = cat_style(r['category']); sid = safe_id(r['name'])
        rr = research.get(r['name'], {})
        rn = r['name']
        insight_html = ''
        if r.get("how") and not r["how"].startswith("["):
            insight_html = '<p class="rpanel-insight">' + esc(r["how"]) + '</p>'
        panels.append(
            '<div class="role-panel" id="panel-' + sid + '" style="display:' + ('block' if i==0 else 'none') + '">'
            + '<div class="rpanel-header" style="background:' + cs['bg'] + ';border-color:' + cs['bdr'] + '">'
            + '<span class="rpanel-emoji">' + esc(r['emoji']) + '</span>'
            + '<div><h2 class="rpanel-name">' + esc(rn) + '</h2>'
            + '<span class="cat-badge" style="background:' + cs['bg'] + ';color:' + cs['txt'] + ';border-color:' + cs['bdr'] + '">' + esc(cs['lbl']) + '</span>'
            + insight_html + '</div></div>'
            + '<div class="rpanel-body"><div class="subcards-grid">'
            + sub_card("Goals", "🎯", rr.get("goals",[]), "What are people in the '" + rn + "' role trying to achieve?", cs['dot'])
            + sub_card("Problems & Pain Points", "🔥", rr.get("pain_points",[]), "What do '" + rn + "' people struggle with most? Type /dig " + rn + " to go deeper.", '#EF4444')
            + sub_card("How They Solve It Today", "🔧", rr.get("workarounds",[]), "What tools, hacks, or manual processes do '" + rn + "' people use right now?", '#F59E0B')
            + sub_card("New Tech & Narratives", "💡", rr.get("tech_narratives",[]), "What new technology could change how '" + rn + "' problems get solved?", '#8B5CF6')
            + sub_card("Market Size (TAM)", "📊", rr.get("tam",[]), "How large is the '" + rn + "' market? Estimate: # of people × what they'd pay.", '#10B981')
            + sub_card("Your Personal Experience", "⭐", rr.get("user_challenges",[]), "Which '" + rn + "' problems do YOU personally experience? Rate each 1–5.", cs['dot'])
            + '</div></div></div>'
        )

    return (
        '<div class="roles-layout">'
        + '<div class="roles-sidebar">' + ''.join(pills) + '</div>'
        + '<div class="roles-detail">' + ''.join(panels) + '</div>'
        + '</div>'
    )

def tab_network(d):
    contacts = d["network_contacts"]

    def filled_card(c):
        name = c.get('Name',''); how = c.get('How You Know Them','')
        does = c.get('What They Do',''); overlap = c.get('Role Overlap','')
        iv = c.get('Interviewed?','No')
        init = (name[0] if name else '?').upper()
        badge = '<span class="badge badge-green">Interviewed ✓</span>' if str(iv).lower() in ('yes','y','done') else '<span class="badge badge-gray">Not yet</span>'
        role_html = ('<div class="contact-role">' + esc(does) + '</div>') if does and not does.startswith('[') else ''
        known_html = ('<div class="contact-known">' + esc(how) + '</div>') if how and not how.startswith('[') else ''
        overlap_html = ('<div class="contact-overlap">↔ ' + esc(overlap) + '</div>') if overlap and not overlap.startswith('[') else ''
        return (
            '<div class="contact-card">'
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
    while len(cards) < 5:
        cards.append(empty_slot(len(cards)+1))

    return (
        '<div class="tab-section">'
        + '<div class="network-header">'
        + '<h3>🤝 Your Interview Network</h3>'
        + '<p>These people can validate your hypothesis — or kill a bad one before you build. Aim for 5+ honest conversations.</p>'
        + '</div>'
        + '<div class="contacts-grid">' + ''.join(cards) + '</div>'
        + '</div>'
    )

def tab_opps(d):
    problems = d["candidate_problems"]; oq = d["open_questions"]
    if not problems:
        return '<div class="tab-section"><div class="card">' + pending_card("Opportunity ranking appears here after research + challenge interview phases.", "🚀") + '</div></div>'

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
        persona_html = ('<p class="problem-detail"><strong>Persona:</strong> ' + esc(persona) + '</p>') if persona and not persona.startswith('[') else ''
        pain_html = ('<p class="problem-detail"><strong>Pain:</strong> ' + esc(pain) + '</p>') if pain and not pain.startswith('[') else ''
        wa_html = ('<p class="problem-detail"><strong>Workaround:</strong> ' + esc(wa) + '</p>') if wa and not wa.startswith('[') else ''
        cards.append(
            '<div class="problem-card ' + ('problem-eliminated' if not active else '') + '">'
            + '<div class="problem-header">'
            + '<h3 class="problem-name">' + esc(p["name"]) + '</h3>'
            + '<div class="problem-badges">' + score_badge + status_badge + '</div>'
            + '</div>'
            + persona_html + pain_html + wa_html
            + '</div>'
        )

    oq_html = ('<div class="card"><h3 class="card-title">❓ Open Questions</h3>' + (blist(oq) or pending_card("Open questions for next session appear here.")) + '</div>') if oq else ''
    return (
        '<div class="tab-section">'
        + '<div class="network-header"><h3>🚀 Ranked Opportunities</h3><p>Problems scored across 10 dimensions. Max score: 50/50.</p></div>'
        + '<div class="problems-list">' + ''.join(cards) + '</div>'
        + oq_html + '</div>'
    )

CSS = """
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#F8FAFC;color:#0F172A;font-size:14px;line-height:1.6}
.header{background:#fff;border-bottom:1px solid #E2E8F0;padding:14px 28px;position:sticky;top:0;z-index:100;display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap}
.header-title{font-size:17px;font-weight:800}.header-title span{color:#2563EB}
.header-badges{display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.badge{display:inline-flex;align-items:center;padding:3px 10px;border-radius:99px;font-size:11px;font-weight:600;border:1px solid transparent}
.badge-blue{background:#EFF6FF;color:#1E40AF;border-color:#BFDBFE}
.badge-green{background:#F0FDF4;color:#166534;border-color:#86EFAC}
.badge-gray{background:#F9FAFB;color:#374151;border-color:#D1D5DB}
.badge-red{background:#FEF2F2;color:#991B1B;border-color:#FECACA}
.tabs{background:#fff;border-bottom:1px solid #E2E8F0;display:flex;padding:0 28px;position:sticky;top:55px;z-index:99;overflow-x:auto}
.tab{padding:11px 18px;cursor:pointer;font-size:13px;font-weight:500;color:#64748B;border-bottom:2px solid transparent;white-space:nowrap;transition:color .15s,border-color .15s;user-select:none}
.tab:hover{color:#0F172A}.tab.active{color:#2563EB;border-bottom-color:#2563EB}
.tab-content{display:none}.tab-content.active{display:block}
.tab-section{max-width:1080px;margin:0 auto;padding:24px;display:flex;flex-direction:column;gap:18px}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:18px}
@media(max-width:650px){.two-col{grid-template-columns:1fr}}
.card{background:#fff;border:1px solid #E2E8F0;border-radius:12px;padding:20px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.card-title{font-size:14px;font-weight:700;margin-bottom:12px;display:flex;align-items:center;gap:8px}
.card-sub{font-size:12px;color:#64748B;margin-bottom:12px}
.count-badge{background:#EFF6FF;color:#2563EB;font-size:11px;font-weight:700;padding:1px 7px;border-radius:99px}
.pending{background:#F8FAFC;border:1.5px dashed #CBD5E1;border-radius:9px;padding:14px;display:flex;gap:10px;align-items:flex-start}
.pending-icon{font-size:16px;flex-shrink:0;line-height:1.4}.pending-text{color:#64748B;font-size:13px;line-height:1.5}
.blist{padding-left:18px;display:flex;flex-direction:column;gap:4px}.blist li{font-size:13px;color:#334155}
.profile-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:10px}
.pfield{background:#F8FAFC;border-radius:8px;padding:10px 12px}
.plabel{display:block;font-size:10px;font-weight:700;text-transform:uppercase;letter-spacing:.05em;color:#94A3B8;margin-bottom:2px}
.pval{font-size:14px;font-weight:600;color:#0F172A}
.mini-roles-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:10px}
.mini-role{border:1.5px solid;border-radius:9px;padding:11px 13px;cursor:pointer;display:flex;align-items:center;gap:10px;transition:transform .1s,box-shadow .1s}
.mini-role:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(0,0,0,.08)}
.mini-emoji{font-size:22px;flex-shrink:0}.mini-name{font-size:13px;font-weight:700}.mini-cat{font-size:11px;font-weight:500}
.roles-layout{display:grid;grid-template-columns:210px 1fr;gap:0;min-height:70vh}
@media(max-width:750px){.roles-layout{grid-template-columns:1fr}}
.roles-sidebar{border-right:1px solid #E2E8F0;padding:16px 12px;display:flex;flex-direction:column;gap:5px;position:sticky;top:110px;max-height:calc(100vh - 110px);overflow-y:auto;background:#fff}
.role-pill{display:flex;align-items:center;gap:9px;padding:9px 11px;border-radius:8px;cursor:pointer;border:1px solid var(--cat-bdr,#E2E8F0);font-size:13px;font-weight:500;transition:background .15s;overflow:hidden}
.role-pill:hover{background:var(--cat-bg,#F8FAFC)}
.role-pill.pill-active{background:var(--cat-bg,#EFF6FF);border-color:var(--cat-bdr,#93C5FD);color:var(--cat-txt,#1E40AF);font-weight:700}
.pill-name{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.roles-detail{padding:20px;background:#F8FAFC}
.role-panel{background:#fff;border:1px solid #E2E8F0;border-radius:12px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.rpanel-header{display:flex;align-items:flex-start;gap:14px;padding:20px;border-bottom:1px solid}
.rpanel-emoji{font-size:40px;line-height:1}.rpanel-name{font-size:20px;font-weight:800;margin-bottom:5px}
.rpanel-insight{font-size:12px;color:#64748B;margin-top:5px}
.cat-badge{display:inline-block;padding:2px 9px;border-radius:99px;font-size:11px;font-weight:600;border:1px solid}
.rpanel-body{padding:16px}
.subcards-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:700px){.subcards-grid{grid-template-columns:1fr}}
.sub-card{background:#FAFAFA;border:1px solid #E2E8F0;border-radius:9px;padding:14px}
.sub-title{font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.06em;color:#475569;margin-bottom:10px}
.network-header{padding:0 0 8px}.network-header h3{font-size:20px;font-weight:800;margin-bottom:4px}.network-header p{font-size:13px;color:#64748B}
.contacts-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:14px}
.contact-card{background:#fff;border:1px solid #E2E8F0;border-radius:12px;padding:16px;display:flex;gap:14px;align-items:flex-start;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.contact-card.contact-empty{border-style:dashed;background:#F8FAFC}
.contact-avatar{width:44px;height:44px;border-radius:50%;background:#2563EB;color:#fff;font-size:18px;font-weight:800;flex-shrink:0;display:flex;align-items:center;justify-content:center}
.contact-avatar-empty{background:#E2E8F0;color:#94A3B8}
.contact-name{font-size:15px;font-weight:700;margin-bottom:3px}.contact-empty-name{color:#94A3B8}
.contact-role{font-size:12px;color:#334155;margin-bottom:2px}.contact-known{font-size:11px;color:#94A3B8;font-style:italic;margin-bottom:6px}.contact-overlap{font-size:11px;color:#64748B;margin-bottom:6px}
.problems-list{display:flex;flex-direction:column;gap:14px}
.problem-card{background:#fff;border:1px solid #E2E8F0;border-radius:12px;padding:18px;box-shadow:0 1px 3px rgba(0,0,0,.04)}
.problem-eliminated{opacity:.5}
.problem-header{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:10px}
.problem-name{font-size:16px;font-weight:700}
.problem-badges{display:flex;gap:6px;flex-wrap:wrap;justify-content:flex-end;flex-shrink:0}
.score-badge{padding:3px 10px;border-radius:99px;font-size:12px;font-weight:800;border:1.5px solid}
.problem-detail{font-size:13px;color:#64748B;margin-top:5px}.problem-detail strong{color:#334155}
"""

JS = """
function switchTab(name,el){
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  el.classList.add('active');
}
function selectRole(sid){
  document.querySelectorAll('.role-panel').forEach(p=>p.style.display='none');
  document.querySelectorAll('.role-pill').forEach(p=>p.classList.remove('pill-active'));
  const panel=document.getElementById('panel-'+sid);
  const pill=document.getElementById('pill-'+sid);
  if(panel)panel.style.display='block';
  if(pill)pill.classList.add('pill-active');
}
function openRole(sid){
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab').forEach(t=>t.classList.remove('active'));
  document.getElementById('tab-roles').classList.add('active');
  document.querySelectorAll('.tab')[1].classList.add('active');
  selectRole(sid);
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
        + '<div class="header-badges">'
        + '<span class="badge badge-blue">v' + esc(meta['version']) + ' · Round ' + esc(meta['round']) + '</span>'
        + '<span class="badge badge-gray">Updated ' + esc(date_str) + '</span>'
        + '<span class="badge badge-gray">' + str(n_roles) + ' roles · ' + str(n_c) + ' contacts · ' + str(n_o) + ' opps</span>'
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

    return (
        '<!DOCTYPE html>\n<html lang="en">\n<head>\n'
        + '<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        + '<title>Discovery — ' + esc(name) + '</title>\n'
        + '<style>\n' + CSS + '\n</style>\n</head>\n<body>\n'
        + header + '\n' + tabs + '\n'
        + '<div id="tab-you" class="tab-content active">' + tab_you(d) + '</div>\n'
        + '<div id="tab-roles" class="tab-content">' + tab_roles(d) + '</div>\n'
        + '<div id="tab-network" class="tab-content">' + tab_network(d) + '</div>\n'
        + '<div id="tab-opps" class="tab-content">' + tab_opps(d) + '</div>\n'
        + '<script>\n' + JS + '\n</script>\n</body>\n</html>'
    )

def main():
    inp = Path(sys.argv[1]) if len(sys.argv)>1 else Path.home()/"problem-finder"/"discovery.md"
    out = Path(sys.argv[2]) if len(sys.argv)>2 else inp.with_suffix('.html')
    if not inp.exists(): print("Error: " + str(inp) + " not found", file=sys.stderr); sys.exit(1)
    text = inp.read_text(encoding='utf-8')
    html = generate_html(parse_document(text))
    out.write_text(html, encoding='utf-8')
    print("✓ Rendered → " + str(out))

if __name__=="__main__": main()
