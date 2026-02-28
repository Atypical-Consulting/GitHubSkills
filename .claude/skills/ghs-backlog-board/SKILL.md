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
allowed-tools: "Bash(gh:*) Bash(jq:*) Bash(bc:*)"
compatibility: "Requires gh CLI (authenticated) with project scope. Project data must exist from a prior ghs-repo-scan run."
license: MIT
metadata:
  author: phmatray
  version: 7.0.0
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
Purpose: Read-only dashboard renderer for GitHub Project data produced by ghs-repo-scan.

Roles:
1. **Dashboard Renderer** (you) — queries GitHub Projects, formats the display, recommends next action

No sub-agents — this is a read-only skill that renders project data.

Shared references (use these, do not duplicate their logic):

| Reference | Purpose |
|-----------|---------|
| `../shared/references/scoring-logic.md` | Tier weights, score formula, module weighting, priority algorithm, progress bar format |
| `../shared/references/projects-format.md` | Project naming, item schema, custom fields, jq scoring pipelines, score record format, state issue lookup |
| `../shared/references/output-conventions.md` | Dashboard tables, status indicators, recommendation block |
| `../shared/references/state-persistence.md` | State issue format, lifecycle, reading patterns for dashboard enrichment |
| `../shared/references/config.md` | Scoring constants, display thresholds |
| `../shared/references/gh-cli-patterns.md` | Project Operations section — auth check, project discovery, item queries |
</context>

<anti-patterns>

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Re-query all project items when `[GHS Score]` item exists | Use the `[GHS Score]` item as the index — it has the computed score, tier breakdowns, and timestamps | Avoids unnecessary API calls and keeps rendering fast |
| Recalculate scores from scratch | Use the score from the `[GHS Score]` item body, or the jq pipeline from `projects-format.md` | `[GHS Score]` item is the single source of truth for scores |
| Suggest fixes inline in the dashboard | Route to `ghs-backlog-fix` for any fix action | Dashboard is read-only; fixes belong in a separate skill |
| Show resolved/Done items by default | Only show Todo (FAIL/OPEN) items; show Done items only when user drills down | Keeps the dashboard focused on actionable items |
| Read all project items unprompted | Only read individual items when the user asks for detail on a specific item | Progressive disclosure — load detail on demand |

</anti-patterns>

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

No input required. The skill discovers all `[GHS]` projects automatically.

Optional filters the user might provide:
- A specific repo: "show backlog for phmatray/NewSLN"
- A specific source: "show health items" or "show issues only"
- A specific tier: "show tier 1 items"
- Only failures: "show remaining failures"

## Pre-flight

Verify project scope before any project API call:

```bash
gh auth status 2>&1 | grep -q "project" || echo "[FAIL] Run: gh auth refresh -s project"
```

## Phase 1 — Discover Repositories (`[GHS Score]` as Index)

Discover all `[GHS]` projects for the owner:

```bash
gh project list --owner {owner} --format json \
  --jq '.projects[] | select(.title | startswith("[GHS]"))'
```

For each project, read **only** the `[GHS Score]` draft item to extract:
- Health score (earned / possible / percentage) — may include per-module breakdown from the JSON body
- Tier breakdown (earned per tier, per module)
- Active modules (core, dotnet, etc.)
- Combined score if multiple modules active
- Last updated date (from `[GHS Score]` item body `"updated"` field)

```bash
# Get the score record for a project
ITEMS=$(gh project item-list $PROJECT_NUM --owner {owner} --format json --limit 500)
SCORE_ITEM=$(echo "$ITEMS" | jq '.items[] | select(.title == "[GHS Score]")')
SCORE_BODY=$(echo "$SCORE_ITEM" | jq -r '.body' | jq '.')
```

Also count open issue items and health Todo items from the project:

```bash
OPEN_ISSUES=$(echo "$ITEMS" | jq '[.items[] | select(.source == "GitHub Issue" and .status == "Todo")] | length')
FAIL_HEALTH=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .status == "Todo")] | length')
```

Then look up the state issue for this repo to extract activity context:

```bash
# Find the state issue
gh issue list --repo {owner}/{repo} --label "ghs:state" --state open \
  --json number,title,body --limit 1
```

From the state issue body, extract:
- **Last activity** — date from most recent session entry
- **Active blockers** — count of blockers with status ACTIVE
- **Decisions** — any user preferences that affect display (e.g., skip list)
- **Last session summary** — skill name and outcome (e.g., "ghs-backlog-fix — 3 PASS, 1 FAILED")

> **Rule:** `[GHS Score]` item is the single source of truth for scores. The state issue enriches the view with activity context.
>
> **Trigger:** User asks "show backlog", "dashboard", "how are my repos doing"
>
> **Example:** Read `[GHS Score]` item from `[GHS] phmatray/NewSLN` project for `10/31 (32%)`, then query the state issue for "Last activity: 2026-02-28 — 3 items fixed". Do NOT read every individual project item.

### Progressive Disclosure

| User Action | Data Source |
|-------------|------------|
| "show backlog" / "dashboard" | `[GHS Score]` item body + state issue (if exists) |
| "show details for phmatray/NewSLN" | `[GHS Score]` item + state issue + list Todo items from project (health and issues) |
| "tell me about the README item" | Query the specific `[Health] README` project item |

## Phase 2 — Display the Dashboard

### Dashboard Columns

| Column | Source | Description |
|--------|--------|-------------|
| Repository | Project title (strip `[GHS] ` prefix) | `{owner}/{repo}` format |
| Health | `[GHS Score]` item body | `{earned}/{possible} ({pct}%)` |
| Progress | Computed from score | 8-char bar per `../shared/references/scoring-logic.md` |
| Issues | Project item count | Count of items with `Source = GitHub Issue` and `Status = Todo` |
| Open | Project item count | Issues with `Status = Todo` |
| PRs | Project item count | Issues with `Status = In Progress` (PR created) |
| Last Scan | `[GHS Score]` item body `"updated"` field | `YYYY-MM-DD` |
| Last Activity | State issue body | Most recent session date, or `--` if no state issue |
| Blockers | State issue body | Count of ACTIVE blockers, or `--` if none |

### Status Indicators

See `../shared/references/output-conventions.md` for the canonical list. Key indicators for this skill:

| Indicator | When Shown |
|-----------|-----------|
| `[FAIL]` | Health check in Todo column — action required |
| `[WARN]` | Permission-blocked check — shown in terminal output but not in project |
| `[PASS]` | Only in drill-down view, not default dashboard |

### Multi-repo overview (when multiple repos exist)

> **Rule:** Show one row per repo. Only Todo (FAIL/OPEN) counts matter in the overview.
>
> **Trigger:** Multiple `[GHS]` projects found for the owner
>
> **Example output:**

```
## Backlog Dashboard

| Repository | Health | Progress | Issues | Open | PRs | Last Scan | Last Activity | Blockers |
|------------|--------|----------|--------|------|-----|-----------|---------------|----------|
| phmatray/NewSLN | 10/31 (32%) | ██░░░░░░ | 18 | 15 | 3 | 2026-02-26 | 2026-02-28 | 1 |
| phmatray/OtherRepo | 24/28 (86%) | ██████░░ | 5 | 2 | 1 | 2026-02-20 | -- | -- |

Total: 2 repos | Health items: 25 (14 pass) | Issues: 23 (17 open)
```

The Last Activity and Blockers columns are sourced from the state issue. Repos with no state issue show `--`.

Progress bar format is defined in `../shared/references/scoring-logic.md`.

### Single-repo detail (when one repo, or user filters to one)

> **Rule:** Show remaining Todo (FAIL/OPEN) items by default. Show Done items in a collapsed section.
>
> **Trigger:** Single `[GHS]` project found, or user says "show backlog for {owner}/{repo}"
>
> **Example output:**

```
## Backlog: phmatray/NewSLN

> Health Score: 10/31 (32%) | Open Issues: 15 | Last scan: 2026-02-26 | Visibility: Private
> Last activity: 2026-02-28 — ghs-backlog-fix (3 PASS, 1 FAILED) | Active blockers: 1

### Health — Remaining Items (by priority)

| # | Item | Tier | Points | Status | Issue | PR |
|---|------|------|--------|--------|-------|----|
| 1 | README | 1 | 4 | FAIL | #42 | -- |
| 2 | Branch Protection | 1 | 4 | FAIL | -- | -- |
...

### Health Score Breakdown

  Core:   30/74  ███░░░░░ (41%)
    Tier 1:  8/16  ████░░░░ (50%)  -- 2 remaining
    Tier 2:  2/12  █░░░░░░░ (17%)  -- 5 remaining
    Tier 3:  0/3   ░░░░░░░░ (0%)   -- 3 remaining

  .NET:   18/34  ████░░░░ (53%)   (if .NET module active)
    Tier 1:  8/8   ████████ (100%)
    Tier 2:  8/16  ████░░░░ (50%)  -- 4 remaining
    Tier 3:  2/10  █░░░░░░░ (20%)  -- 8 remaining

  Combined: 46% (core 41% × 60% + .NET 53% × 40%)

### Open Issues

| # | Issue | Labels | Age | Assignee | Status |
|---|-------|--------|-----|----------|--------|
| 42 | Login page crashes on mobile | bug | 12d | @user | OPEN |
...

Labels: bug: 5 | enhancement: 8 | docs: 2 | unlabeled: 3

### Active Blockers (from state issue)

| Blocker | Affected Items | Status |
|---------|---------------|--------|
| No admin access | branch-protection, security-alerts | ACTIVE |
```

If a state issue exists and has ACTIVE blockers, show the blockers section. If no state issue or no active blockers, omit this section entirely.

The "Issue" column in the health table shows `#{number}` for items that are linked GitHub Issues (synced via `ghs-backlog-sync`), or `--` for draft health items not yet synced. Only display this column when at least one item has a linked issue.

Order health items by tier (1 first), then by points (highest first). Order issues by creation date (oldest first).

#### Good vs Bad Output

**Good** (default view — only Todo/FAIL items):
```
### Health — Remaining Items (by priority)

| # | Item | Tier | Points | Status |
|---|------|------|--------|--------|
| 1 | README | 1 | 4 | FAIL |
| 2 | Branch Protection | 1 | 4 | FAIL |
| 3 | .editorconfig | 2 | 2 | FAIL |
```

**Bad** (showing everything including Done/PASS — clutters the view):
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

  /ghs-backlog-fix {owner}/{repo} --item readme
```

### Routing Logic

| User Situation | Suggest | Command |
|---------------|---------|---------|
| Has failing health items | Apply the top-priority fix | `/ghs-backlog-fix {owner}/{repo} --item {slug}` |
| All health items pass, has open issues | Implement the oldest issue | `/ghs-issue-implement {owner}/{repo}#{number}` |
| Scan data > 30 days old | Re-scan the repo | `/ghs-repo-scan {owner}/{repo}` |
| Items not yet linked to GitHub issues | Sync backlog to issues | `/ghs-backlog-sync {owner}/{repo}` |
| All items resolved | Congratulations message | (none) |

### Stale Scan Detection

If the `[GHS Score]` item `"updated"` date is more than 30 days old (threshold defined in `../shared/references/scoring-logic.md`), add:

```
> This scan is 45 days old. Consider re-running:
>   /ghs-repo-scan {owner}/{repo}
```

## Phase 4 — Quick-Apply Prompt

> **Rule:** Treat follow-up fix requests as a trigger for ghs-backlog-fix.
>
> **Trigger:** User says "apply it", "fix it", "do it", "yes" after seeing the recommendation
>
> **Example:** User sees README recommended, says "fix it" -> invoke `ghs-backlog-fix phmatray/NewSLN --item readme`

</process>

## Edge Cases

- **No GitHub Projects found**: Tell the user no scans have been run yet and suggest: `/ghs-repo-scan {owner}/{repo}`
- **All items done**: Display a congratulatory message with the final score
- **WARN items**: Show them separately in terminal output -- they are not in the project and not actionable without permission changes
- **No open issues in project**: Normal — if the repo had no open issues when scanned, there are no `GitHub Issue` items in the project

## Troubleshooting

**"No GitHub Projects found"**
No repos have been scanned yet. Run `/ghs-repo-scan owner/repo` first.

**Scores don't match expectations**
Re-run the scan to refresh: `/ghs-repo-scan owner/repo`. Scores are based on the last scan's `[GHS Score]` item.

**Stale scan data**
If a scan is more than 30 days old, the dashboard will flag it with a re-scan suggestion.
