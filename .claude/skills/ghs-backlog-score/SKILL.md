---
name: ghs-backlog-score
description: >
  Calculates and displays the health score for a repository from its backlog items. Use this skill
  whenever the user wants to see a repo's health score, check their score, recalculate after fixes,
  or says things like "what's my score", "show score for {repo}", "health score", "recalculate score",
  "how healthy is my repo", "score check", or "points breakdown".
  Do NOT use for full dashboards with issue lists (use ghs-backlog-board), scanning repos (use ghs-repo-scan),
  or applying fixes (use ghs-backlog-fix).
allowed-tools: "Bash(gh:*) Bash(jq:*) Bash(bc:*)"
compatibility: "Requires gh CLI (authenticated) with project scope. Project data must exist from a prior ghs-repo-scan run."
license: MIT
metadata:
  author: phmatray
  version: 5.0.0
routes-to:
  - ghs-backlog-board
  - ghs-backlog-next
  - ghs-repo-scan
routes-from:
  - ghs-backlog-fix
---

# Backlog Score

Calculate and display the health score for a repository from its GitHub Project health items. This is a lightweight, read-only view -- just the score, tier breakdown, and points summary.

<context>
Purpose: Read-only score renderer that calculates and displays health scores from GitHub Project data.

Roles:
1. **Score Calculator** (you) — queries GitHub Project items, computes scores using jq pipelines, renders the output

No sub-agents — this is a lightweight, read-only skill.

### Shared References

| Reference | Path | Purpose |
|-----------|------|---------|
| Scoring Logic | `../shared/references/scoring-logic.md` | Tier weights, formula, module weighting, status rules, progress bar format |
| Projects Format | `../shared/references/projects-format.md` | Project naming, item schema, custom fields, jq scoring pipelines, score record format |
| Output Conventions | `../shared/references/output-conventions.md` | Terminal output patterns, table formats, routing suggestions |
| Config | `../shared/references/config.md` | Scoring constants, display thresholds |
| gh CLI Patterns | `../shared/references/gh-cli-patterns.md` | Project Operations section — auth check, project discovery, item queries |
</context>

<anti-patterns>

## Anti-Patterns

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Re-scan the repo | Query GitHub Project data only; if no project found, tell the user to run `/ghs-repo-scan` first | This skill is read-only — scanning is `ghs-repo-scan`'s job |
| Modify project items | Never update statuses, points, or fields during scoring | This skill is strictly read-only |
| Invent scores for missing items | Skip items with missing field values and note the gap | Fabricated data produces misleading scores |
| Show full issue lists | Show only the numeric score and tier breakdown | Full item lists are `ghs-backlog-board`'s job |
| Use python scripts | Use jq pipelines from `projects-format.md` § Scoring via jq | Python dependency eliminated; jq is the canonical scoring tool |

</anti-patterns>

<rules>

## Rules

### Rule 1: Determine target repository

| Trigger | Behavior |
|---------|----------|
| User names a repo (`"score for owner/repo"`) | Score that single repo |
| User says `"all scores"` or gives no repo | Score every `[GHS]` project found for the owner |
| No GitHub Project found for this repo | Stop and suggest `/ghs-repo-scan {owner}/{repo}` |

Pre-flight: verify project scope before any project API call:

```bash
gh auth status 2>&1 | grep -q "project" || echo "[FAIL] Run: gh auth refresh -s project"
```

Discover projects for an owner:

```bash
# Find the project number for a specific repo
PROJECT_NUM=$(gh project list --owner {owner} --format json \
  --jq '.projects[] | select(.title == "[GHS] {owner}/{repo}") | .number')

# Find all GHS projects for an owner (for "all scores" mode)
gh project list --owner {owner} --format json \
  --jq '.projects[] | select(.title | startswith("[GHS]"))'
```

Example -- user says: `"what's the score for phmatray/Formidable?"`
Action: look up `[GHS] phmatray/Formidable` project and score it using jq.

### Rule 2: Collect health items and calculate score

Query project items and compute score using jq pipelines (from `projects-format.md` § Scoring via jq):

```bash
ITEMS=$(gh project item-list $PROJECT_NUM --owner {owner} --format json --limit 500)

# Overall score
EARNED=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .status == "Done") | .points] | add // 0')
POSSIBLE=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and (.status == "Todo" or .status == "Done")) | .points] | add // 0')
SCORE=$(echo "scale=0; $EARNED * 100 / $POSSIBLE" | bc)
```

For repos with language modules (e.g., .NET), filter by `Module` field:

```bash
# Core module score
CORE_EARNED=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .module == "core" and .status == "Done") | .points] | add // 0')
CORE_POSSIBLE=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .module == "core" and (.status == "Todo" or .status == "Done")) | .points] | add // 0')

# .NET module score
DOTNET_EARNED=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .module == "dotnet" and .status == "Done") | .points] | add // 0')
DOTNET_POSSIBLE=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .module == "dotnet" and (.status == "Todo" or .status == "Done")) | .points] | add // 0')

# Combined score
COMBINED=$(echo "scale=0; ($CORE_EARNED * 100 / $CORE_POSSIBLE) * 60 / 100 + ($DOTNET_EARNED * 100 / $DOTNET_POSSIBLE) * 40 / 100" | bc)
```

Also read the `[GHS Score]` item body for a cached breakdown if it exists:

```bash
echo "$ITEMS" | jq '.items[] | select(.title == "[GHS Score]") | .body' | jq -r '.'
```

The scoring formula (from `scoring-logic.md`):

| Component | Formula |
|-----------|---------|
| Earned points | `sum(points for each Done health check item)` — per module |
| Possible points | `sum(points for each Todo or Done health check item)` — per module |
| Module percentage | `round(earned / possible * 100)` |
| Combined score (core only) | `core_pct` |
| Combined score (core + lang) | `round(core_pct * 0.6 + lang_pct * 0.4)` |

`In Progress` items are treated as `Todo` for scoring purposes (not yet passing).

WARN items are never added to the project and are automatically excluded from scoring.

Tier point values:

| Tier | Points |
|------|--------|
| 1 — Required | 4 |
| 2 — Recommended | 2 |
| 3 — Nice to Have | 1 |

Count items per tier for the breakdown:

```bash
# Per-tier counts (Done vs total)
echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .tier == "1 — Required")] | {done: [.[] | select(.status == "Done")] | length, total: length}'
```

### Rule 3: Display the score

**Single-repo view (core only):**

```
## Health Score: {owner}/{repo}

  Score: {earned}/{possible} ({percentage}%)

  Tier 1 -- Required:      {n}/{max}  {bar}  ({pct}%)  -- {remaining} remaining
  Tier 2 -- Recommended:   {n}/{max}  {bar}  ({pct}%)  -- {remaining} remaining
  Tier 3 -- Nice to Have:  {n}/{max}  {bar}  ({pct}%)  -- {remaining} remaining

  Status: {pass} PASS | {fail} FAIL | {warn} WARN (excluded)
  Points recoverable: {fail_points} (from {fail_count} failing checks)
```

**Single-repo view (with .NET module):**

```
## Health Score: {owner}/{repo}

  Combined Score: {combined_pct}% (core {core_pct}% × 60% + .NET {dotnet_pct}% × 40%)

  Core:  {core_earned}/{core_possible} ({core_pct}%)
    Tier 1 -- Required:      {n}/{max}  {bar}  ({pct}%)  -- {remaining} remaining
    Tier 2 -- Recommended:   {n}/{max}  {bar}  ({pct}%)  -- {remaining} remaining
    Tier 3 -- Nice to Have:  {n}/{max}  {bar}  ({pct}%)  -- {remaining} remaining

  .NET:  {dotnet_earned}/{dotnet_possible} ({dotnet_pct}%)
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

PASS count = Done health check items. FAIL count = Todo health check items. WARN = reported in terminal only (not in project).

### Rule 4: Handle edge cases

| Situation | Action |
|-----------|--------|
| No GitHub Project found for this repo | Tell user to run `/ghs-repo-scan {owner}/{repo}` |
| All checks pass (100%) | Show congratulatory 100% score with full bars |
| Only WARN items (0/0) | Show "N/A" -- explain all checks are permission-blocked |
| `[GHS Score]` updated date > 30 days old | Note staleness and suggest `/ghs-repo-scan` to refresh |

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
(Note: Could not parse 2 items, estimated their scores as FAIL)
```

Why bad: Never estimate or invent scores. Report only what can be queried. Note items with missing field values as skipped.
