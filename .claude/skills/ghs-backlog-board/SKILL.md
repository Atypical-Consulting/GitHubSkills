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
  version: 4.0.0
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

Display a cross-repo dashboard of all backlog items with scores, progress, and next-action recommendations.

<context>
Purpose: Read-only dashboard renderer for backlog data produced by ghs-repo-scan.

Roles:
1. **Dashboard Renderer** (you) — reads SUMMARY.md files, formats the display, recommends next action

No sub-agents — this is a read-only skill that renders local data.

Shared references (use these, do not duplicate their logic):
- `../shared/references/scoring-logic.md` — tier weights, score formula, priority algorithm, progress bar format
- `../shared/references/backlog-format.md` — directory structure, file naming, metadata formats, status values
- `../shared/references/output-conventions.md` — dashboard tables, status indicators, recommendation block
</context>

## Anti-Patterns

| Do NOT | Do Instead |
|--------|-----------|
| Re-read every backlog item when SUMMARY.md exists | Use SUMMARY.md as the index — it has scores, tier breakdowns, and item lists |
| Recalculate scores from scratch | Use the score from SUMMARY.md, or `python ../shared/scripts/calculate_score.py` |
| Suggest fixes inline in the dashboard | Route to `ghs-backlog-fix` for any fix action |
| Show resolved/PASS items by default | Only show FAIL and WARN items; show PASS items only when user drills down |
| Read individual health/issue files unprompted | Only read individual files when the user asks for detail on a specific item |

<objective>
Display a dashboard of all backlog items with health scores, issue counts, and progress.

Outputs:
- Terminal dashboard with multi-repo overview or single-repo detail
- Highest-impact next action recommendation

Next routing:
- Suggest `ghs-backlog-fix` for the recommended item
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

## Phase 1 — Discover Repositories (SUMMARY.md as Index)

Scan `backlog/` for all `{owner}_{repo}/` directories. For directory structure, see `../shared/references/backlog-format.md`.

For each repo, read **only** `SUMMARY.md` to extract:
- Health score (earned / max / percentage)
- Tier breakdown (earned per tier)
- Open issue count
- Generated date
- Visibility (Public / Private)

> **Rule:** SUMMARY.md is the single source of truth for the overview.
>
> **Trigger:** User asks "show backlog", "dashboard", "how are my repos doing"
>
> **Example:** Read `backlog/phmatray_NewSLN/SUMMARY.md` to get `10/31 (32%)` — do NOT scan individual item files.

### Progressive Disclosure

| User Action | Data Source |
|-------------|------------|
| "show backlog" / "dashboard" | SUMMARY.md files only |
| "show details for phmatray/NewSLN" | SUMMARY.md + list FAIL/WARN files from `health/` and `issues/` |
| "tell me about the README item" | Read the specific `tier-1--readme.md` file |

## Phase 2 — Display the Dashboard

### Dashboard Columns

| Column | Source | Description |
|--------|--------|-------------|
| Repository | Directory name | `{owner}/{repo}` format |
| Health | SUMMARY.md | `{earned}/{possible} ({pct}%)` |
| Progress | Computed | 8-char bar per `../shared/references/scoring-logic.md` |
| Issues | SUMMARY.md | Total open issue count |
| Open | SUMMARY.md | Issues currently open |
| PRs | SUMMARY.md | Issues with PRs created |
| Last Scan | SUMMARY.md | `YYYY-MM-DD` generated date |

### Status Indicators

See `../shared/references/output-conventions.md` for the canonical list. Key indicators for this skill:

| Indicator | When Shown |
|-----------|-----------|
| `[FAIL]` | Health check failed — action required |
| `[WARN]` | Cannot verify (permissions) — shown but not actionable |
| `[PASS]` | Only in drill-down view, not default dashboard |

### Multi-repo overview (when multiple repos exist)

> **Rule:** Show one row per repo. Only FAIL/WARN counts matter in the overview.
>
> **Trigger:** Multiple `backlog/{owner}_{repo}/` directories found
>
> **Example output:**

```
## Backlog Dashboard

| Repository | Health | Progress | Issues | Open | PRs | Last Scan |
|------------|--------|----------|--------|------|-----|-----------|
| phmatray/NewSLN | 10/31 (32%) | ██░░░░░░ | 18 | 15 | 3 | 2026-02-26 |
| phmatray/OtherRepo | 24/28 (86%) | ██████░░ | 5 | 2 | 1 | 2026-02-20 |

Total: 2 repos | Health items: 25 (14 pass) | Issues: 23 (17 open)
```

Progress bar format is defined in `../shared/references/scoring-logic.md`.

### Single-repo detail (when one repo, or user filters to one)

> **Rule:** Show remaining FAIL/WARN items by default. Show PASS items in a collapsed section.
>
> **Trigger:** Single repo in backlog, or user says "show backlog for {owner}/{repo}"
>
> **Example output:**

```
## Backlog: phmatray/NewSLN

> Health Score: 10/31 (32%) | Open Issues: 15 | Last scan: 2026-02-26 | Visibility: Private

### Health — Remaining Items (by priority)

| # | Item | Tier | Points | Status | Issue | PR |
|---|------|------|--------|--------|-------|----|
| 1 | README | 1 | 4 | FAIL | #42 | -- |
| 2 | Branch Protection | 1 | 4 | FAIL | -- | -- |
...

### Health Score Breakdown

  Tier 1:  8/16  ████░░░░ (50%)  -- 2 remaining
  Tier 2:  2/12  █░░░░░░░ (17%)  -- 5 remaining
  Tier 3:  0/3   ░░░░░░░░ (0%)   -- 3 remaining

### Open Issues

| # | Issue | Labels | Age | Assignee | Status |
|---|-------|--------|-----|----------|--------|
| 42 | Login page crashes on mobile | bug | 12d | @user | OPEN |
...

Labels: bug: 5 | enhancement: 8 | docs: 2 | unlabeled: 3
```

The "Issue" column in the health table shows `#{number}` for items synced via `ghs-backlog-sync`, or `--` for non-synced items. Only display this column when at least one item has a synced issue.

Order health items by tier (1 first), then by points (highest first). Order issues by creation date (oldest first).

#### Good vs Bad Output

**Good** (default view — only FAIL/WARN):
```
### Health — Remaining Items (by priority)

| # | Item | Tier | Points | Status |
|---|------|------|--------|--------|
| 1 | README | 1 | 4 | FAIL |
| 2 | Branch Protection | 1 | 4 | FAIL |
| 3 | .editorconfig | 2 | 2 | FAIL |
```

**Bad** (showing everything including PASS — clutters the view):
```
### Health — All Items

| # | Item | Tier | Points | Status |
|---|------|------|--------|--------|
| 1 | LICENSE | 1 | 4 | PASS |
| 2 | README | 1 | 4 | FAIL |
| 3 | Description | 1 | 4 | PASS |
| 4 | Branch Protection | 1 | 4 | FAIL |
| 5 | .gitignore | 2 | 2 | PASS |
| 6 | .editorconfig | 2 | 2 | FAIL |
```

## Phase 3 — Recommend Next Action

After the dashboard, suggest the highest-impact next action. Use the priority algorithm from `../shared/references/scoring-logic.md` (do not redefine it here).

### Recommendation Block

See `../shared/references/output-conventions.md` for the canonical format:

```
### Recommended Next

The highest-impact item is **README** (Health -- Tier 1, 4 points).
To apply it:

  /ghs-backlog-fix backlog/phmatray_NewSLN/health/tier-1--readme.md
```

### Routing Logic

| User Situation | Suggest | Command |
|---------------|---------|---------|
| Has failing health items | Apply the top-priority fix | `/ghs-backlog-fix backlog/{owner}_{repo}/health/{item}` |
| All health items pass, has open issues | Implement the oldest issue | `/ghs-issue-implement {owner}/{repo}#{number}` |
| Scan data > 30 days old | Re-scan the repo | `/ghs-repo-scan {owner}/{repo}` |
| Items not synced to GitHub | Sync backlog to issues | `/ghs-backlog-sync {owner}/{repo}` |
| All items resolved | Congratulations message | (none) |

### Stale Scan Detection

If the scan date is more than 30 days old (threshold defined in `../shared/references/scoring-logic.md`), add:

```
> This scan is 45 days old. Consider re-running:
>   /ghs-repo-scan {owner}/{repo}
```

## Phase 4 — Quick-Apply Prompt

> **Rule:** Treat follow-up fix requests as a trigger for ghs-backlog-fix.
>
> **Trigger:** User says "apply it", "fix it", "do it", "yes" after seeing the recommendation
>
> **Example:** User sees README recommended, says "fix it" -> invoke `ghs-backlog-fix backlog/phmatray_NewSLN/health/tier-1--readme.md`

</process>

## Edge Cases

- **No backlog directory**: Tell the user no scans have been run yet and suggest: `/ghs-repo-scan {owner}/{repo}`
- **All items done**: Display a congratulatory message with the final score
- **WARN items**: Show them separately -- they are not actionable without permission changes
- **Missing issues directory**: If a repo had no open issues when scanned, the `issues/` directory will not exist. This is normal.

## Troubleshooting

**"No backlog directory found"**
No repos have been scanned yet. Run `/ghs-repo-scan owner/repo` first.

**Scores don't match expectations**
Re-run the scan to refresh: `/ghs-repo-scan owner/repo`. Scores are based on the last scan's SUMMARY.md.

**Stale scan data**
If a scan is more than 30 days old, the dashboard will flag it with a re-scan suggestion.
