# Idea Finder — Co-Founder Discovery Agent

> A Claude Code skill that helps you systematically find the right problem to build a company around — before you write a line of code.

---

## The problem with finding a startup idea

Most founders don't fail because they can't build. They fail because they build something nobody needed badly enough to pay for.

The standard advice — "find a problem you're passionate about," "scratch your own itch," "talk to users" — is true but hollow. Passion is not signal. Your own itch might be a niche of one. "Talk to users" doesn't tell you *how* to talk to them, what questions to ask, or how to tell real pain from polite feedback.

What's missing is a structured process: a way to systematically map your whole world — your work, your hobbies, your relationships, your frustrations — and extract from it the problems that are narrow enough to solve, painful enough to pay for, and accessible enough to sell.

That's what this skill does.

---

## What it does

Idea Finder is a Claude Code skill that acts as a co-founder discovery agent. It interviews you about your life and expertise, researches every role you inhabit as a potential market, scores the opportunities it finds, and helps you validate the strongest ones before you commit.

It keeps a running `discovery.md` — your complete discovery record — and renders it as a visual self-map you can explore in a browser.

The skill knows when to push, when to go deeper, and when to tell you a problem isn't real. It doesn't tell you what to build. It helps you find problems worth solving and gives you the tools to test whether they're real.

---

## How it works

### Session 1 — The interview

You type `/idea-finder`. The skill interviews you across 13 structured blocks: your career history, your daily frustrations, your hobbies and communities, your personal life situations, and — critically — the specific people in your network.

By the end, you have a **Roles List**: every identity you inhabit (software engineer, homeowner, immigrant, mountain biker, parent) treated as a potential market.

### Between sessions — Research

The skill runs web searches for each role: what do people in this role struggle with, what workarounds do they use, what new technology could change the picture, how large is the market? Raw research lives in `discovery.md`; clean summaries surface in the visual map.

### Round N — Depth and validation

You return, the skill loads your document, and you go deeper. You run targeted digs on your most promising roles, prep for and debrief customer interviews, simulate skeptical customers, and gradually narrow toward one problem worth pursuing.

### The output

A ranked list of candidate problems scored on pain intensity, frequency, willingness to pay, founder fit, and market accessibility — plus a visual self-map, a founder brief you can share, and a single recommended next action at any point.

---

## Installation

```bash
# Clone the repo
git clone git@github.com:zhenya-vlasov/idea-finder.git ~/idea-finder

# Symlink as a Claude Code skill
ln -s ~/idea-finder ~/.claude/skills/idea-finder

# Symlink the render helper skill
ln -s ~/idea-finder/skills/render ~/.claude/skills/render
```

Open Claude Code and type `/idea-finder` to begin.

---

## Available commands

| Command | What it does |
|---|---|
| `/idea-finder` | Start or resume a discovery session. Loads your existing `discovery.md` automatically on return visits. |
| `/dig [role]` | Zoom in on a specific role. Asks 8 sharper questions: exact break moments, cost estimates, workaround details, willingness-to-pay signals. |
| `/validate [problem]` | Turn a candidate problem into a testable hypothesis. Produces a Reddit post you can publish today, a 5-question interview script, and a list of yes/no signals to watch for. |
| `/interview [contact]` | Generate a tailored interview script for a specific person in your network. Paste in your notes afterward and it structures them back into your discovery document. |
| `/sim [problem]` | Claude plays a skeptical potential customer. You have to convince them the problem is real — without pitching a solution. Ends with a structured debrief and score. |
| `/market [role]` | Deep competitive research: TAM, incumbents, funded startups in the space, community forums, and whitespace analysis. |
| `/persona [role]` | Write a vivid day-in-the-life customer persona — the kind you'd put on a wall and ask "would this person pay for this?" |
| `/score` | Score all candidate problems on a 50-point rubric across pain intensity, frequency, WTP, founder fit, and market accessibility. |
| `/compare [A] vs [B]` | Head-to-head comparison of two problems across six dimensions. Ends with a clear recommendation — not a list of trade-offs. |
| `/why-me [problem]` | Honest, scored assessment of your unfair advantage — or lack of one — for a specific problem. |
| `/brief` | One-page founder brief synthesized from your full discovery document. Ready to share with an advisor, co-founder, or early investor. |
| `/next` | Single most valuable next action, based on exactly where you are in the discovery process right now. |
| `/render` | Rebuild the Self-Map web app from your current `discovery.md`. Runs `render.py` and tells you to refresh the browser. |

---

## Session flow

```
/idea-finder
      │
      ▼
  Session 1 — Interview (13 blocks) + Roles List
      │
      ▼
  Research — web search for each role (pain, workarounds, TAM, incumbents)
      │
      ▼
  Discovery document saved → ~/idea-finder/discovery.md
      │
      ├── /dig [role]       ← go deeper on any role
      ├── /market [role]    ← competitive research
      ├── /persona [role]   ← build a customer profile
      ├── /score            ← rank your candidates
      ▼
  Network contacts identified
      │
      ├── /interview [name] ← tailored script + note processing
      ├── /sim [problem]    ← practice the conversation
      ▼
  Best problem surfaces
      │
      ├── /validate         ← build the hypothesis, get it in front of people
      ├── /compare [A] vs [B]
      ├── /why-me           ← honest founder-market fit check
      ├── /brief            ← one-pager to share
      └── /next             ← one action to take in the next 48 hours
```

---

## The discovery document

Everything is stored in `~/idea-finder/discovery.md` — a single structured markdown file that accumulates across sessions:

- Your complete profile and background
- Full Roles List with categories and how each role was identified
- Per-role research: goals, pain points, workarounds, tech narratives, TAM
- Your personal challenge ratings for each pain
- Network contacts and interview scripts
- Candidate problems with scores and evidence
- Validation plans and open questions

Run `python3 ~/idea-finder/scripts/render.py` at any point to update the visual self-map.

---

## The self-map

The self-map is a visual browser interface showing:

- **Orbital map** — your roles arranged in two concentric rings, sized by intensity
- **Network tab** — your close circle and which roles they overlap with
- **Opportunities tab** — candidate problems ranked by score
- **Open questions tab** — unanswered questions you can fill in over time

---

## What's inside

```
idea-finder/
├── SKILL.md                      # Main skill — all commands
├── skills/
│   └── render/SKILL.md           # /render helper skill
├── scripts/
│   ├── render.py                 # discovery.md → visual self-map
│   └── serve.py                  # local dev server with answer persistence
├── references/
│   ├── industry-workflow.md      # Search queries and research workflows
│   ├── pain-extraction.md        # What counts as real pain signal
│   ├── network-mapping.md        # Interviewability scoring
│   ├── anti-patterns.md          # 10 idea traps to filter out
│   ├── incumbent-risk.md         # Why large companies leave gaps
│   ├── opportunity-ranking.md    # Full 50-point scoring rubric
│   ├── interview-scripts.md      # 30–45 min interview structure
│   ├── competitor-research.md    # Where to find real competitive data
│   ├── validation-playbook.md    # 4-step validation ladder
│   └── distribution-mapping.md  # Where each persona lives online
└── evals/
    └── evals.json                # Test cases for skill evaluation
```

---

## Philosophy

**Stay problem-focused.** The skill never suggests what to build. It surfaces problems and helps you decide.

**Evidence over enthusiasm.** A problem is real when someone describes a specific moment it broke — not when they say they "would use" a solution.

**Your network is the moat.** The founders who win early reach 10 paying customers without a marketing budget. The skill consistently pushes toward that.

**The document is the truth.** The visual interface shows clean takeaways. The markdown file holds every raw quote, every search excerpt, every unanswered question. Don't clean it up — that's your evidence.
