---
name: ghs-backlog-board
description: >
  Shows a dashboard of all backlog items across all audited repositories — health scores, open issues,
  progress, and what to work on next. Use this skill whenever the user wants to see backlog status,
  check progress across repos, find the next item to fix, or asks things like "show backlog",
  "what's left to fix", "backlog status", "dashboard", "show all repos", "remaining items",
  "how are my repos doing", or "progress report".
  Also trigger when the user says "list backlog", "show findings", "show issues", or just "backlog".
  Do NOT use for scanning new repos (use ghs-repo-scan), applying fixes (use ghs-backlog-fix), or reviewing code.
  For quick "what should I work on next?" queries, prefer ghs-backlog-next instead.
allowed-tools: "Bash(python3:*) Read Glob"
compatibility: "Requires python3. Backlog data must exist from a prior ghs-repo-scan run."
license: MIT
metadata:
  author: phmatray
  version: 3.0.0
routes-to:
  - ghs-backlog-fix
  - ghs-backlog-sync
  - ghs-repo-scan
  - ghs-backlog-next
routes-from:
  - ghs-repo-scan
  - ghs-backlog-fix
  - ghs-backlog-sync
---

# Backlog Dashboard

Scan all backlog items (health findings and issues), display a cross-repo dashboard with scores and progress, and recommend what to work on next.

<context>
Purpose: Display a cross-repo dashboard of all backlog items with scores, progress, and next-action recommendations.

Roles:
1. **Dashboard Renderer** (you) — reads backlog files, computes scores, formats the display

No sub-agents — this is a read-only skill that renders local data.

Shared docs:
- `../shared/gh-prerequisites.md` — authentication and error handling
- `../shared/backlog-format.md` — file naming, metadata formats, scoring rules
- `../shared/config.md` — scoring constants, display settings, stale scan threshold
</context>

<objective>
Display a dashboard of all backlog items with health scores, issue counts, and progress.

Outputs:
- Terminal dashboard with multi-repo overview or single-repo detail
- Highest-impact next action recommendation

Next routing:
- Suggest `ghs-backlog-fix` for the recommended item — "To apply: `/ghs-backlog-fix backlog/{owner}_{repo}/health/{item}`"
- Suggest `ghs-repo-scan` if scan data is stale (> 30 days)
- If user says "apply it" or "fix it" after seeing the recommendation, treat as a trigger for `ghs-backlog-fix`
</objective>

<process>

## Input

No input required. The skill scans all `backlog/` subdirectories automatically.

Optional filters the user might provide:
- A specific repo: "show backlog for phmatray/NewSLN"
- A specific source: "show health items" or "show issues only"
- A specific tier: "show tier 1 items"
- Only failures: "show remaining failures"

## Phase 1 — Discover Repositories

Scan `backlog/` for all `{owner}_{repo}/` directories. For the backlog directory structure and file formats, see `../shared/backlog-format.md`.

For each repo, read `SUMMARY.md` to extract:
- Health score (earned / max / percentage)
- Tier breakdown (earned per tier)
- Open issue count
- Generated date
- Visibility (Public / Private)

## Phase 2 — Collect Item Status

For each repo, scan both `health/` and `issues/` directories.

Parse items using the shared format defined in `../shared/backlog-format.md`.
You can also parse items programmatically: `python ../shared/scripts/parse_backlog_item.py <path>`
For aggregate scores: `python ../shared/scripts/calculate_score.py backlog/{owner}_{repo}`

Count totals per repo:
- Health: items total, passed, failed, warned; points earned vs possible
- Issues: total, open, with PRs, closed

## Phase 3 — Display the Dashboard

### Multi-repo overview (when multiple repos exist)

```
## Backlog Dashboard

| Repository | Health | Progress | Issues | Open | PRs | Last Scan |
|------------|--------|----------|--------|------|-----|-----------|
| phmatray/NewSLN | 10/31 (32%) | ██░░░░░░ | 18 | 15 | 3 | 2026-02-26 |
| phmatray/OtherRepo | 24/28 (86%) | ██████░░ | 5 | 2 | 1 | 2026-02-20 |

Total: 2 repos | Health items: 25 (14 pass) | Issues: 23 (17 open)
```

Progress bar uses `█` and `░`, 8 chars wide (see `../shared/config.md` for display constants).

### Single-repo detail (when one repo, or user filters to one)

```
## Backlog: phmatray/NewSLN

> Health Score: 10/31 (32%) | Open Issues: 15 | Last scan: 2026-02-26 | Visibility: Private

### Health — Remaining Items (by priority)

| # | Item | Tier | Points | Status | Issue | PR |
|---|------|------|--------|--------|-------|----|
| 1 | README | 1 | 4 | FAIL | #42 | — |
| 2 | Branch Protection | 1 | 4 | FAIL | — | — |
...

### Health — Completed Items

| Item | Tier | Points | PR |
|------|------|--------|----|
| LICENSE | 1 | 4 | (pre-existing) |
| Description | 1 | 4 | N/A — API fix |
...

### Health Score Breakdown

  Tier 1:  8/16  ████░░░░ (50%)  — 2 remaining
  Tier 2:  2/12  █░░░░░░░ (17%)  — 5 remaining
  Tier 3:  0/3   ░░░░░░░░ (0%)   — 3 remaining

### Open Issues

| # | Issue | Labels | Age | Assignee | Status |
|---|-------|--------|-----|----------|--------|
| 42 | Login page crashes on mobile | bug | 12d | @user | OPEN |
...

Labels: bug: 5 | enhancement: 8 | docs: 2 | unlabeled: 3
```

The "Issue" column shows `#{number}` for items synced via `ghs-backlog-sync`, or `—` for non-synced items. Only display this column when at least one item has a synced issue.

Order health items by tier (1 first), then by points (highest first). Order issues by creation date (oldest first).

## Phase 4 — Recommend Next Action

After the dashboard, suggest the highest-impact next action:

```
### Recommended Next

The highest-impact item is **README** (Health — Tier 1, 4 points).
To apply it:

  /ghs-backlog-fix backlog/phmatray_NewSLN/health/tier-1--readme.md
```

Selection logic (same as `ghs-backlog-next`):
1. Pick the repo with the lowest health score percentage
2. Health items take priority over issues — they improve the repo's foundation
3. Within health items, pick the lowest tier number (Tier 1 > Tier 2 > Tier 3)
4. Within that tier, pick the highest point value
5. If all health items are done, recommend the oldest open issue
6. If there's a tie, pick the first one alphabetically

Tier point values are defined in `../shared/config.md`.

### Stale scan detection

If the scan date is more than 30 days old (see `../shared/config.md` for threshold), add a note:

```
> This scan is 45 days old. Consider re-running:
>   /ghs-repo-scan {owner}/{repo}
```

## Phase 5 — Quick-Apply Prompt

If the user says something like "apply it" or "fix it" after seeing the recommendation, treat that as a trigger for the `ghs-backlog-fix` skill with the recommended item's path.

</process>

## Edge Cases

- **No backlog directory**: Tell the user no scans have been run yet and suggest: `/ghs-repo-scan {owner}/{repo}`
- **All items done**: Display a congratulatory message with the final score
- **WARN items**: Show them separately — they aren't actionable without permission changes

## Examples

**Example 1: Show full dashboard**
User says: "show backlog"
Result: Multi-repo overview table with health scores and issue counts, followed by recommendation.

**Example 2: Drill into one repo**
User says: "backlog status for phmatray/NewSLN"
Result: Single-repo detail view with remaining/completed items, score breakdown, and issue table.

**Example 3: Find next action**
User says: "what should I work on next?"
Result: Dashboard with recommendation pointing to the lowest-scoring repo's highest-priority failing item.

## Troubleshooting

**"No backlog directory found"**
No repos have been scanned yet. Run `/ghs-repo-scan owner/repo` first.

**Scores don't match expectations**
Re-run the scan to refresh: `/ghs-repo-scan owner/repo`. Scores are based on the last scan's SUMMARY.md.

**Stale scan data**
If a scan is more than 30 days old, the dashboard will flag it with a re-scan suggestion.

**Missing issues directory**
If a repo had no open issues when scanned, the `issues/` directory won't exist. This is normal.
