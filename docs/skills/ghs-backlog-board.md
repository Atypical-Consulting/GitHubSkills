# ghs-backlog-board

Shows a read-only dashboard of all backlog items across audited repositories with scores, progress, and next-action recommendations.

::: info Skill Info
**Version:** 3.0.0
**Trigger phrases:** "show me the backlog board", "show my repos", "what's the status?", "backlog status", "dashboard", "show all repos", "how are my repos doing", "progress report"
:::

## What It Does

`ghs-backlog-board` reads all backlog data from prior scans and renders a dashboard in the terminal. It does not make any API calls or modify any files — it is purely a read-only display skill.

The dashboard comes in two views:

- **Multi-repo overview** — when multiple repos have been scanned, shows a summary table with scores, progress bars, issue counts, and last scan dates
- **Single-repo detail** — when one repo is selected, shows remaining and completed health items, score breakdown by tier, and open issues

After displaying the dashboard, it recommends the highest-impact next action using the same priority algorithm as `ghs-backlog-next`.

### Stale Scan Detection

If a scan is more than 30 days old, the dashboard flags it with a re-scan suggestion.

## Example

### Multi-Repo View

```
## Backlog Dashboard

| Repository          | Health        | Progress | Issues | Open | PRs | Last Scan  |
|---------------------|---------------|----------|--------|------|-----|------------|
| phmatray/NewSLN     | 10/31 (32%)   | ██░░░░░░ | 18     | 15   | 3   | 2026-02-26 |
| phmatray/OtherRepo  | 24/28 (86%)   | ██████░░ | 5      | 2    | 1   | 2026-02-20 |

Total: 2 repos | Health items: 25 (14 pass) | Issues: 23 (17 open)
```

### Single-Repo View

```
## Backlog: phmatray/NewSLN

> Health Score: 10/31 (32%) | Open Issues: 15 | Last scan: 2026-02-26

### Health — Remaining Items (by priority)

| # | Item              | Tier | Points | Status | PR |
|---|-------------------|------|--------|--------|----|
| 1 | README            | 1    | 4      | FAIL   | -- |
| 2 | Branch Protection | 1    | 4      | FAIL   | -- |
...

### Health Score Breakdown

  Tier 1:  8/16  ████░░░░ (50%)  — 2 remaining
  Tier 2:  2/12  █░░░░░░░ (17%)  — 5 remaining
  Tier 3:  0/3   ░░░░░░░░ (0%)   — 3 remaining

### Recommended Next

The highest-impact item is **README** (Health — Tier 1, 4 points).
To apply it:
  /ghs-backlog-fix backlog/phmatray_NewSLN/health/tier-1--readme.md
```

## Routes To

After viewing the dashboard, GHS suggests:

- **[ghs-backlog-fix](/skills/ghs-backlog-fix)** — to fix the recommended item
- **[ghs-repo-scan](/skills/ghs-repo-scan)** — to re-scan if data is stale
- **[ghs-backlog-next](/skills/ghs-backlog-next)** — for a quick single-item recommendation

## Technical Details

| Property | Value |
|----------|-------|
| Allowed tools | `Bash(python3:*)`, `Read`, `Glob` |
| Spawns sub-agents | No — read-only dashboard renderer |
| Phases | 5 (Discover Repos, Collect Status, Display Dashboard, Recommend Next, Quick-Apply Prompt) |
| Requires | `python3`, backlog data from a prior `ghs-repo-scan` run |
| Re-run safe | Yes — read-only, no side effects |
