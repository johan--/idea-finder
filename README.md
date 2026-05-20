# Problem Finder — Co-Founder Discovery Agent

A Claude Code skill that helps entrepreneurs systematically find narrow,
recurring, painful, underserved operational problems worth building a company
around.

## What it does

- **Interviews you** about your background, network, and domain knowledge
- **Researches your industries** with live web search — real pain signals from
  Reddit, G2, Capterra, community forums
- **Scores candidate problems** on 10 dimensions using a structured rubric
- **Generates interview scripts** tailored to each person in your network
- **Creates and saves a Discovery Document** to `~/problem-finder/discovery.md`
- **Resumes automatically** — start a new session and it picks up where you
  left off, no copy-pasting required

It stays problem-focused throughout. It will never prescribe what to build —
that's your call, after validation.

## Install

```bash
npx skills add yourusername/problem-finder
```

Or manually clone into your skills directory:

```bash
git clone https://github.com/yourusername/problem-finder ~/.claude/skills/problem-finder
```

## Use

In any Claude Code session:

```
/problem-finder
```

That's it. The skill routes automatically:
- **First session:** starts the interview immediately
- **Return sessions:** reads your saved Discovery Document and asks for
  interview notes

## How sessions work

```
Session 1  →  Interview + Research + Discovery Document created
                        ↓
             Go interview your network (scripts provided)
                        ↓
Session 2  →  /problem-finder  →  auto-loads document  →  process notes
                        ↓
             Updated rankings + WTP analysis + next steps
                        ↓
Session N  →  One problem clearly leads → competitor research + validation plan
```

Your Discovery Document lives at `~/problem-finder/discovery.md` and updates
automatically after each session.

## What's inside

```
problem-finder/
├── SKILL.md                      # Main skill instructions
├── references/
│   ├── industry-workflow.md      # What to research + search queries per industry
│   ├── pain-extraction.md        # Pain hierarchy + what counts as real signal
│   ├── network-mapping.md        # Interviewability scoring rubric
│   ├── anti-patterns.md          # 10 idea traps to filter out immediately
│   ├── incumbent-risk.md         # Why incumbents avoid certain segments
│   ├── opportunity-ranking.md    # 10-dimension scoring rubric (max 50)
│   ├── interview-scripts.md      # Full 30–45 min interview structure
│   ├── tech-behavioral-trends.md # AI/LLM wave + behavioral shifts
│   ├── competitor-research.md    # Where to find negative reviews + TAM math
│   ├── validation-playbook.md    # 4-step validation ladder
│   └── distribution-mapping.md  # Where each persona lives online
└── evals/
    └── evals.json                # Test cases for skill evaluation
