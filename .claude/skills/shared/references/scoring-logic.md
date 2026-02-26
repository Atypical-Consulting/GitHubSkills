# Scoring Logic Reference

Health score calculation rules used by ghs-repo-scan, ghs-backlog-score, ghs-backlog-board, and ghs-backlog-next. For canonical values, see `config.md`.

## Tier Definitions and Weights

| Tier | Label | Points per Check | Description |
|------|-------|-----------------|-------------|
| 1 | Required | 4 | Non-negotiable for any public or team-shared repo |
| 2 | Recommended | 2 | Important for maintainability and collaboration |
| 3 | Nice to Have | 1 | Polish items signaling a mature project |

## Maximum Possible Points

| Tier | Checks | Points Each | Subtotal |
|------|--------|-------------|----------|
| 1 | 4 | 4 | 16 |
| 2 | 22 | 2 | 44 |
| 3 | 14 (excluding Funding, Discussions, Commit Signoff) | 1 | 14 |
| **Total** | **40** | | **74** |

## Score Calculation Formula

```
earned_points = sum(points for each PASS check)
possible_points = sum(points for each check that is PASS or FAIL)
percentage = round(earned_points / possible_points * 100)
```

## Status Scoring Rules

| Status | Earned Points | Counted in Possible? | Rationale |
|--------|--------------|---------------------|-----------|
| PASS | Full tier points | Yes | Check passed |
| FAIL | 0 | Yes | Check failed, action required |
| WARN | 0 | **No** | Permission issue — excluded from both totals |
| INFO | 0 | **No** | Informational only (e.g., FUNDING.yml) — no impact |

Key: WARN and INFO items are **excluded** from both earned and possible totals. This prevents penalizing users for checks that cannot be verified due to permissions.

## Priority Algorithm (Next Item Selection)

Used by ghs-backlog-next and ghs-backlog-board to recommend the highest-impact item:

| Priority | Rule |
|----------|------|
| 1 | Lowest health score percentage repo first |
| 2 | Health items over issues (structural foundation) |
| 3 | Lowest tier number (Tier 1 > Tier 2 > Tier 3) |
| 4 | Highest point value within same tier |
| 5 | Oldest issue (by creation date) for issue items |
| 6 | Alphabetical (final tiebreaker) |

Tie between repos: pick the one with the most failing items.

## Progress Bar Format

```
Width:  8 characters
Filled: █
Empty:  ░
Formula: filled_chars = round(percentage / 100 * 8)
```

Examples:

| Percentage | Bar |
|-----------|-----|
| 0% | `░░░░░░░░` |
| 25% | `██░░░░░░` |
| 50% | `████░░░░` |
| 75% | `██████░░` |
| 100% | `████████` |

## Score Verification

```bash
python .claude/skills/shared/scripts/calculate_score.py backlog/{owner}_{repo}
```

## Stale Scan Detection

If a scan's SUMMARY.md date is older than **30 days**, flag it and suggest re-scanning:

```
> This scan is {N} days old. Consider re-running:
>   /ghs-repo-scan {owner}/{repo}
```
