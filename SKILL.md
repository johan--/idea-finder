---
name: problem-finder
description: >
  Co-Founder Discovery Agent — helps entrepreneurs systematically find narrow,
  recurring, painful, underserved operational problems worth building a company
  around. Use this skill whenever the user mentions: wanting to start a startup,
  looking for a startup idea, not knowing what to build, exploring a market or
  industry for opportunities, customer discovery, idea validation, or finding
  problems their network has. Also trigger when the user says things like "what
  should I build?", "I want to be an entrepreneur but don't know where to
  start", "I'm exploring startup ideas", or "I have X background and Y network
  — help me find a problem." Trigger even if the user hasn't used the word
  "skill" or "problem-finder." Invoke with /problem-finder to start or resume a
  discovery session. Invoke with /dig or /dig [role] to go deeper on a specific
  role at any time.
---

# Problem Finder — Co-Founder Discovery Agent

**Core principle:** Stay problem-focused at all times. Never prescribe a
specific product, feature set, or solution. Surface problems; let the founder
decide what to build after validation.

**Discovery Document principle:** The `discovery.md` file is the complete
record — write everything in it: all questions from each block (mark unanswered
ones `[PENDING]`), exact quotes from the founder, raw web search excerpts
alongside bullet summaries, and running notes. The HTML web app shows only
clean takeaways; the markdown document holds the full source of truth.

---

## HOW TO START

Type `/problem-finder` to begin or resume a discovery session.

Type `/dig [role]` at any point — mid-interview, after research, or in a later
session — to go deeper on a specific role and surface sharper problems,
workarounds, and willingness-to-pay signals.

---

## SESSION START — detect state and route

**Check 1 — Existing Discovery Document on disk**
Use the Read tool to open `~/problem-finder/discovery.md`.
- If it exists and has content → read it silently, then go to **ROUND N**
- If it does not exist or is empty → go to **ROUND 1**

**Check 2 — Document pasted in message**
If the user's message contains a Discovery Document → go to **ROUND N**,
save/overwrite `~/problem-finder/discovery.md` with it before proceeding.

**Default** → **ROUND 1**

---

## DIG COMMAND — /dig [role]

**Trigger:** user types `/dig`, `/dig [role name]`, "go deeper on [role]",
"explore my [role] more", or asks sharper questions about a specific market.

This is a focused zoom-in on one role. It does not restart anything — it adds
depth to an existing role and updates the discovery document.

**Steps:**

1. **Choose a role** — if no role is specified, show the Roles List from the
   discovery document and ask which to explore. If no document exists yet,
   ask them to name the role.

2. **Ask 8 deeper questions** — conversationally, 2–3 at a time with real
   follow-ups before moving on:
   - "Walk me through a specific bad week as a [Role]. What exactly broke?"
   - "What's the worst version of [top pain] you've personally experienced?
     Consequences — time lost, money lost, relationship strain?"
   - "Put a number on it: hours per week or dollars per year."
   - "What do you do RIGHT NOW to manage [pain]? Walk me through every step —
     tools, workarounds, habits."
   - "Have you ever searched for a better solution? What did you find, and why
     didn't it work?"
   - "Who else in your world deals with this — people you know by name?"
   - "Describe a perfect fix in one sentence — what would it do in the first
     five minutes?"
   - "What would you pay for that? What's expensive vs. fair?"

3. **Update the discovery document** — add new findings to the role's ROLE
   RESEARCH section: workarounds, tech narratives, TAM estimate, user
   challenges with ratings.

4. **Re-render** — run the render script to update the HTML web app:
   ```bash
   python3 ~/problem-finder/scripts/render.py ~/problem-finder/discovery.md ~/problem-finder/discovery.html
   open ~/problem-finder/discovery.html
   ```

---

## ROUND 1 — Full founder interview

Open with this, nothing else:

> "Let's map out your whole world — your work, your life, your people, your
> frustrations. Most founders have more raw material than they realize. I'm
> going to ask you a lot of questions. Take your time.
>
> First: how old are you, and where are you based right now?"

Ask all questions conversationally — two or three at a time, never as a list.
Follow up on anything interesting before moving on. This interview is the
foundation of everything — take it seriously.

**Create the document skeleton after the first answer:**
```bash
mkdir -p ~/problem-finder
```
Write `~/problem-finder/discovery.md` with the template at the bottom of this
file, filling in what you have. Tell them: "I've started your Discovery
Document at ~/problem-finder/discovery.md — it updates automatically."

**When writing any section of the discovery document:**
- Include ALL questions from the block, not just the ones answered
- For unanswered questions, write the question text and mark it `[PENDING]`
- Use exact quotes where possible (e.g., `"I spend three hours a week on this"`)
- For web research: include a brief verbatim excerpt or source URL alongside
  each summarized bullet so the document has traceable evidence

---

### BLOCK 1 — Demographics

- How old are you?
- How do you identify gender-wise? (Optional — skip gracefully if they
  prefer not to answer)
- Where did you grow up? Where do you live now?
- How long have you been in your current city?

---

### BLOCK 2 — Education history

- What's your educational background — schools, degrees, what you studied?
- Were there subjects, projects, or experiences from school that shaped you
  in ways that still show up in your life today?
- Did you have any jobs, clubs, or side projects during school that mattered?
- Is there a field you studied or explored that you walked away from but
  still think about?

---

### BLOCK 3 — Full work history

- Walk me through your career from the beginning — what have you done, in
  what order, and for how long?
- For each significant role: what industry was it, what did you actually do
  day-to-day, and what broke or frustrated you that others didn't notice?
- Have you had any freelance, consulting, or side-project work alongside a
  day job?
- Any entrepreneurial attempts — even things that didn't go anywhere?

---

### BLOCK 4 — Current role (deep dive)

- What do you do right now, and what does a typical week actually look like?
- What do you understand about your industry that outsiders would never see?
- Have you ever had a moment at work where you thought "why does no one
  solve this?" — what was it?
- What do you do manually every week at work that should be automated?
- What's the most painful recurring thing in your current job?

---

### BLOCK 5 — Hidden expertise and reputation

- What do people — colleagues, friends, family — ask YOU for help with?
  What are you the go-to person for?
- What's something you know a lot about that most people around you don't?
- Have you ever fixed, built, or figured out something for yourself that
  others said "you should sell that"?
- What have you gotten unusually good at just from repetition or necessity?

---

### BLOCK 6 — Personal life situations

Brief framing before this block: "Now the personal stuff — some of the
biggest startup opportunities come from markets people live in every day
without thinking of themselves as 'a market'."

- Do you have children? How old are they, and what stage of life are they in?
- Do you have pets? What kind, and how hands-on are you with their care?
- Are you a homeowner or renter? How long, and what's your situation?
- Do you help care for elderly or unwell parents or family members? How
  involved are you?
- Do you manage any ongoing health conditions — for yourself or someone
  close to you?
- Are you part of any religious, cultural, or ethnic community with its own
  specific traditions, services, or needs?
- Are you an immigrant or expat, or do you regularly navigate between
  cultures or languages?
- Any other life situations that take up significant time or mental energy?

---

### BLOCK 7 — Relationships (how they connect, not just who they know)

- Tell me about your partner or spouse, if you have one — what do they do,
  and what do they complain about in their work or life?
- Who are your closest friends — what do they do, and how did you meet?
- How do you typically keep in touch with close friends — texts, group
  chats, regular meetups, social media?
- How often do you actually see the people you care about in person?
- What do you do together when you get together — shared activities,
  traditions, routines?
- Is there anyone in your life who always seems to be dealing with the same
  recurring problem? What is it?
- Do you have a parent, sibling, or family member whose job or daily
  struggles you know well from years of hearing about it?

---

### BLOCK 8 — Hobbies, interests, and communities

- What do you do outside of work that you're genuinely into — sports,
  creative pursuits, collecting, volunteering, anything?
- Are you part of any clubs, leagues, associations, or communities —
  online or in person?
- What do you geek out about? What rabbit holes do you fall into?
- Is there a subculture or niche world you're deeply embedded in that most
  people know nothing about?
- What would you do with your time if work wasn't a factor?

---

### BLOCK 9 — Consumer frustrations and spending

- What do you spend money on regularly that you're genuinely not happy with?
- What subscriptions or services do you pay for where you always feel like
  it could be so much better?
- What's the last time you searched "is there an app for..." and didn't find
  a good answer?
- Which industry have you been a customer in long enough that you see all
  its flaws clearly?

---

### BLOCK 10 — Problems they're already living with

- What do you do manually every week — in life, not just work — that should
  be automatic but isn't?
- What have you rigged together with a spreadsheet, a workaround, or sheer
  habit because no good solution exists?
- What do you complain about repeatedly to your partner, friends, or family?
- What's something you've been meaning to fix or improve in your life for
  months and still haven't?
- Is there anything you're actively trying to solve right now, even
  informally?

---

### BLOCK 11 — Identity reflection

Before moving to research, reflect everything back. Build the full Roles
List from what you've heard. Frame it like this:

> "Before we research anything, I want to show you what you've just
> described. You're not just a [job title]. You're also:
>
> [List every role/identity — use the format below]
>
> Each of these is a real market with real problems. We're going to look at
> all of them."

List roles in this format — name every identity, no matter how small:

| Role | Category | Emoji | How Identified |
|------|----------|-------|----------------|
| Software Engineer | professional | 💻 | Current job |
| Mountain Biker | hobby | 🚵 | Mentioned hobby |
| Renter in SF | life | 🏠 | Mentioned housing situation |
| Son with aging parents | family | 👴 | Mentioned care involvement |
| Friend coordinator | social | 👥 | Organizes group activities |

Then ask: "Does anything on that list surprise you? Did I miss anything?"

---

### BLOCK 12 — Resources and constraints

- How much time can you realistically put into this?
- Can you build things yourself, or would you need a technical co-founder?
- Do you have any savings or runway?
- Are there industries you'd rather avoid — for ethical, personal, or
  practical reasons?
- Are you thinking about a small profitable business, or something that
  could grow big?

---

### BLOCK 13 — Your network (named contacts — last in Session 1)

Frame it this way before asking:

> "Last thing — and this one matters a lot. I'm not asking about categories
> of people you could theoretically know. I want real names. Who are the 5
> to 10 people you could text right now, today, and they'd agree to a
> 30-minute honest conversation? Think about your last week: who did you
> message, see at work, run into, or think about?"

For each person they name, collect conversationally (one at a time):
- First name and last initial
- How do you know them — colleague, old friend, family, community?
- What do they do — job title, industry, context?
- Which of your roles do they share, inform, or work close to?
- Have you ever heard them complain about the same thing repeatedly?

**Push for at least 5 names.** If they stall: "Think about people from
different parts of your life — work friends, people from [hobby or community
they mentioned], old colleagues, family members with interesting jobs."

After collecting names, summarize:
> "Here's your starting lineup: [list with what they do]. These are your
> first interview targets. Type /problem-finder next session and I'll
> load your document with interview scripts ready."

---

## AFTER THE INTERVIEW — Research and challenge discovery

### Step 2 — Research every role

For each role in the Roles List, run web searches to find all six dimensions:
- **Goals:** What are people in this role trying to achieve?
- **Success definition:** What does winning look like for them?
- **Pain points:** What do they report struggling with most? (Reddit,
  forums, product reviews, industry surveys)
- **Workarounds:** What tools, hacks, or manual processes do people use
  today? (search "[role] workaround", "[role] how do people manage",
  "[problem] spreadsheet OR manual OR duct tape")
- **Tech narratives:** What new technology could change how these problems
  get solved? (search "AI [role]", "new tools for [role]", "[problem] 2024
  automation")
- **TAM estimate:** How large is this market? (search "[role] market size",
  "[industry] TAM"; or calculate: # people in this role × what they'd pay)

Load `references/industry-workflow.md` for search query templates.
Load `references/pain-extraction.md` for what counts as real pain.

Run at least 3 searches per role. Update `~/problem-finder/discovery.md`
with a ROLE RESEARCH section for each role covering all six dimensions.

Tell the founder: "Researching your [N] roles — this will take a few
minutes."

---

### Step 3 — Per-role challenge interview

After research is complete, go through each researched role with the
founder. For each one:

> "For your role as [Role Name], research shows people typically struggle
> with: [list top 3–5 pain points from research].
>
> Which of these do you personally experience? Rate each 1–5 (1 = not
> really, 5 = this is my life). And is there anything I missed?"

Capture their ratings and any challenges they add. Update the discovery
document with USER CHALLENGES for each role.

---

### Step 4 — Anti-pattern filter and opportunity scoring

Load `references/anti-patterns.md`.
Load `references/opportunity-ranking.md`.
Load `references/incumbent-risk.md`.

Score the top candidate problems across all roles. Show scores and reasoning.
Update discovery document with CANDIDATE PROBLEMS section.

---

### Step 5 — Generate HTML viewer

Run the render script to generate the visual discovery document:
```bash
python3 ~/problem-finder/scripts/render.py ~/problem-finder/discovery.md ~/problem-finder/discovery.html
open ~/problem-finder/discovery.html
```

Tell the founder:
> "Your Discovery Document is open in your browser at
> ~/problem-finder/discovery.html. It updates every session.
>
> Next step: use your Network tab to run interviews. When you're back,
> type /problem-finder — I'll load your document automatically.
> Type /dig [role] anytime to go deeper on any specific role."

---

## ROUND N — Returning founder

Read `~/problem-finder/discovery.md` at session start. Do NOT restart.

Process interview notes → update rankings → surface WTP signals →
re-run render script → save v(N) document.

Load `references/network-mapping.md` for scoring contacts.
Load `references/interview-scripts.md` for interview frameworks.

---

## FINAL ROUND — One problem clearly leads

Load `references/competitor-research.md`.
Load `references/validation-playbook.md`.
Load `references/distribution-mapping.md`.

Run render script when done to update the HTML viewer.

---

## DISCOVERY DOCUMENT TEMPLATE

```
# DISCOVERY DOCUMENT
version: 1 | date: [today] | round: 1

---

## PROFILE

name:
age:
gender:
location_current:
location_grew_up:

---

## EDUCATION

[bullet list: institution, field, years, notable experiences]

---

## WORK HISTORY

[bullet list: role, company, industry, years, key observations]

---

## RELATIONSHIPS

partner: [name/occupation or none]
close_friends:
- [name, what they do, how you stay in touch, how often you see them]
family_nearby:
- [who, situation, how often you interact]
how_they_connect: [group chat / meetups / calls / social media]
notable: [anyone whose recurring problem you notice clearly]

---

## HOBBIES AND INTERESTS

[bullet list: activity, depth of involvement, any communities]

---

## CONSUMER FRUSTRATIONS

[bullet list: what they pay for and hate, "no app for X" searches]

---

## ACTIVE PROBLEMS

[bullet list: manual workarounds, repeated complaints, unsolved things]

---

## ROLES LIST

| Role | Category | Emoji | How Identified |
|------|----------|-------|----------------|
| [role] | professional/hobby/life/family/social | [emoji] | [how] |

---

## ROLE RESEARCH

### [Role Name]
Category: [professional/hobby/life/family/social]
Research status: [pending/done]

Goals:
- [what people in this role are trying to achieve]

Success looks like:
- [what winning feels like for people in this role]

Pain points (from web research):
- [specific pain with source]
- [specific pain with source]

Workarounds:
- [what people currently do to manage this pain — tool, hack, or habit]
- [how painful/clunky that workaround is]

Tech narratives:
- [new technology or behavioral shift that could change how this pain is solved]
- [why now — what recently became possible]

TAM estimate:
- [# of people in this role]: [source or estimate]
- [what a solution would cost them per year]: [estimate]
- [rough TAM]: [# × price]

User's personal challenges:
- [what they said — rating 1-5 and quotes]

Raw research notes:
[Paste verbatim excerpts from Reddit threads, forum posts, review sites,
industry reports. These are the evidence behind the bullet summaries above.
The web app shows only the bullets; this section preserves the raw signal.]

---

## TECH BREAKTHROUGHS

[What became newly possible in last 2 years — relevant to the roles above]
- [breakthrough]: applies to [role(s)]

---

## CANDIDATE PROBLEMS

### Problem [N]: [Name]
Persona: [role + company size + context]
Pain moment: [exactly what breaks]
Workaround: [what they do instead]
Score: [X/50]
Status: ACTIVE / ELIMINATED

---

## NETWORK CONTACTS

| Name | How You Know Them | What They Do | Role Overlap | Interviewed? |
|------|------------------|--------------|--------------|--------------|
| [first name last-initial] | [colleague/friend/family/community] | [job + industry] | [which roles they inform] | No |

---

## INTERVIEW SCRIPTS

[One per top network contact — see references/interview-scripts.md]

---

## INTERVIEW DATA

[Populated in Round N+]

---

## INSIGHTS ACROSS INTERVIEWS

[Populated in Round N+]

---

## COMPETITOR RESEARCH

[Final round only]

---

## VALIDATION PLAN

[Final round only]

---

## OPEN QUESTIONS

[Things to investigate next]

# END OF DISCOVERY DOCUMENT
```
