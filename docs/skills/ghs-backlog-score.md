# ghs-backlog-score

Calculates and displays the health score for a repository from its backlog items.

::: info Skill Info
**Version:** 2.0.0
**Trigger phrases:** "what's the score?", "show me the score", "health score", "recalculate score", "how healthy is my repo", "score check", "points breakdown"
:::

## What It Does

`ghs-backlog-score` is a lightweight, focused view that shows only the health score and tier breakdown. It reads backlog files, applies the scoring rules, and renders a compact display. No API calls, no side effects.

Use this when you want a quick score check without the full dashboard that `ghs-backlog-board` provides.

### Scoring Rules

- **PASS** items earn their tier's point value (Tier 1 = 4, Tier 2 = 2, Tier 3 = 1)
- **FAIL** items earn zero points
- **WARN** items are excluded from both earned and possible totals
- **INFO** items are excluded entirely
- Percentage = earned / possible * 100, rounded to nearest integer

## Example

### Single-Repo View

```
## Health Score: phmatray/my-project

  Score: 45/67 (67%)

  Tier 1 — Required:      12/16  ██████░░  (75%)  — 1 remaining
  Tier 2 — Recommended:   30/40  ██████░░  (75%)  — 5 remaining
  Tier 3 — Nice to Have:   3/11  ██░░░░░░  (27%)  — 8 remaining

  Status: 25 PASS | 14 FAIL | 1 WARN (excluded)
  Points recoverable: 22 (from 14 failing checks)
```

### Multi-Repo View

```
## Health Scores

| Repository            | Score        | Progress | PASS | FAIL | WARN | Recoverable |
|-----------------------|--------------|----------|------|------|------|-------------|
| phmatray/Formidable   | 8/36 (22%)   | ██░░░░░░ | 2    | 10   | 0    | 28 pts      |
| phmatray/NewSLN       | 24/36 (67%)  | █████░░░ | 12   | 4    | 0    | 12 pts      |
```

## Routes To

After viewing the score, GHS suggests:

- **[ghs-backlog-board](/skills/ghs-backlog-board)** — for full details with item lists
- **[ghs-backlog-next](/skills/ghs-backlog-next)** — for the highest-impact next fix
- **[ghs-repo-scan](/skills/ghs-repo-scan)** — if the data is stale

## Technical Details

| Property | Value |
|----------|-------|
| Allowed tools | `Bash(python3:*)`, `Read`, `Glob` |
| Spawns sub-agents | No — read-only score calculator |
| Phases | 3 (Collect Health Items, Calculate Score, Display Score) |
| Requires | `python3`, backlog data from a prior `ghs-repo-scan` run |
| Re-run safe | Yes — read-only, no side effects |
