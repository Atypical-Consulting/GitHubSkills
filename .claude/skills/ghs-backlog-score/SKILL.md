---
name: ghs-backlog-score
description: >
  Calculates and displays the health score for a repository from its backlog items. Use this skill
  whenever the user wants to see a repo's health score, check their score, recalculate after fixes,
  or says things like "what's my score", "show score for {repo}", "health score", "recalculate score",
  "how healthy is my repo", "score check", or "points breakdown".
  Do NOT use for full dashboards with issue lists (use ghs-backlog-board), scanning repos (use ghs-repo-scan),
  or applying fixes (use ghs-backlog-fix).
allowed-tools: "Bash(python3:*) Read Glob"
compatibility: "Requires python3. Backlog data must exist from a prior ghs-repo-scan run."
license: MIT
metadata:
  author: phmatray
  version: 4.0.0
routes-to:
  - ghs-backlog-board
  - ghs-backlog-next
  - ghs-repo-scan
routes-from:
  - ghs-backlog-fix
---

# Backlog Score

Calculate and display the health score for a repository from its backlog health items. This is a lightweight, read-only view -- just the score, tier breakdown, and points summary.

<context>
Purpose: Read-only score renderer that calculates and displays health scores from existing backlog data.

Roles:
1. **Score Calculator** (you) — reads backlog items, computes scores using shared scripts, renders the output

No sub-agents — this is a lightweight, read-only skill.

### Shared References

| Reference | Path | Purpose |
|-----------|------|---------|
| Scoring Logic | `../shared/references/scoring-logic.md` | Tier weights, formula, status rules, progress bar format |
| Backlog Format | `../shared/references/backlog-format.md` | Directory structure, file naming, metadata parsing |
| Output Conventions | `../shared/references/output-conventions.md` | Terminal output patterns, table formats, routing suggestions |
</context>

<anti-patterns>

## Anti-Patterns

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Re-scan the repo | Read existing backlog data only; if no data exists, tell the user to run `/ghs-repo-scan` first | This skill is read-only — scanning is `ghs-repo-scan`'s job |
| Modify backlog items | Never update statuses, points, or metadata during scoring | This skill is strictly read-only |
| Invent scores for missing items | Skip unparseable files and note the gap | Fabricated data produces misleading scores |
| Show full issue lists | Show only the numeric score and tier breakdown | Full item lists are `ghs-backlog-board`'s job |

</anti-patterns>

<rules>

## Rules

### Rule 1: Determine target repository

| Trigger | Behavior |
|---------|----------|
| User names a repo (`"score for owner/repo"`) | Score that single repo |
| User says `"all scores"` or gives no repo | Score every repo found under `backlog/` |
| Backlog directory does not exist | Stop and suggest `/ghs-repo-scan {owner}/{repo}` |

Example -- user says: `"what's the score for phmatray/Formidable?"`
Action: look up `backlog/phmatray_Formidable/` and score it.

### Rule 2: Collect health items and calculate score

Use the shared Python script for reliable, consistent scoring:

```bash
python .claude/skills/shared/scripts/calculate_score.py backlog/{owner}_{repo}
```

If you need to parse individual items:

```bash
python .claude/skills/shared/scripts/parse_backlog_item.py <path>
```

The scoring formula (from `scoring-logic.md`):

| Component | Formula |
|-----------|---------|
| Earned points | `sum(tier_points for each PASS check)` |
| Possible points | `sum(tier_points for each PASS or FAIL check)` |
| Percentage | `round(earned / possible * 100)` |

Status scoring rules:

| Status | Earned | In Possible? | Reason |
|--------|--------|-------------|--------|
| PASS | Full tier points | Yes | Check passed |
| FAIL | 0 | Yes | Action required |
| WARN | 0 | No | Permission issue -- excluded from both totals |
| INFO | 0 | No | Informational only -- no score impact |

### Rule 3: Display the score

**Single-repo view:**

```
## Health Score: {owner}/{repo}

  Score: {earned}/{possible} ({percentage}%)

  Tier 1 -- Required:      {n}/{max}  {bar}  ({pct}%)  -- {remaining} remaining
  Tier 2 -- Recommended:   {n}/{max}  {bar}  ({pct}%)  -- {remaining} remaining
  Tier 3 -- Nice to Have:  {n}/{max}  {bar}  ({pct}%)  -- {remaining} remaining

  Status: {pass} PASS | {fail} FAIL | {warn} WARN (excluded)
  Points recoverable: {fail_points} (from {fail_count} failing checks)
```

**Multi-repo view:**

```
## Health Scores

| Repository | Score | Progress | PASS | FAIL | WARN | Recoverable |
|------------|-------|----------|------|------|------|-------------|
| owner/repo | 8/36 (22%) | ██░░░░░░ | 2 | 10 | 0 | 28 pts |
```

Progress bars: 8 chars wide, `█` filled, `░` empty (see `scoring-logic.md`).

### Rule 4: Handle edge cases

| Situation | Action |
|-----------|--------|
| No backlog directory | Tell user to run `/ghs-repo-scan {owner}/{repo}` |
| All checks pass (100%) | Show congratulatory 100% score with full bars |
| Only WARN items (0/0) | Show "N/A" -- explain all checks are permission-blocked |
| SUMMARY.md date > 30 days old | Note staleness and suggest `/ghs-repo-scan` to refresh |

### Rule 5: Suggest next actions

After displaying the score, if there are FAIL items:

```
To see full details: /ghs-backlog-board {owner}/{repo}
To fix the highest-impact item: /ghs-backlog-next
```

</rules>

## Good and Bad Examples

### Good: Clean single-repo output

```
## Health Score: phmatray/Formidable

  Score: 8/36 (22%)

  Tier 1 -- Required:      2/4   ████░░░░  (50%)  -- 2 remaining
  Tier 2 -- Recommended:   2/8   ██░░░░░░  (25%)  -- 6 remaining
  Tier 3 -- Nice to Have:  0/4   ░░░░░░░░  (0%)   -- 4 remaining

  Status: 4 PASS | 12 FAIL | 1 WARN (excluded)
  Points recoverable: 28 (from 12 failing checks)

To see full details: /ghs-backlog-board phmatray/Formidable
To fix the highest-impact item: /ghs-backlog-next
```

### Bad: Mixing in dashboard content

```
## Health Score: phmatray/Formidable
Score: 8/36 (22%)

Here are the failing items:
1. LICENSE -- missing, you should add MIT license...
2. .editorconfig -- not found, here's a template...
```

Why bad: This skill should NOT list individual items or suggest fixes inline. That is `ghs-backlog-board` and `ghs-backlog-fix` territory.

### Bad: Guessing at missing data

```
## Health Score: phmatray/Formidable
Score: 12/36 (33%)
(Note: Could not parse 2 files, estimated their scores as FAIL)
```

Why bad: Never estimate or invent scores. Report only what can be parsed. Note unparseable files as skipped.
