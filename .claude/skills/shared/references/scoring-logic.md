# Scoring Logic Reference

Health score calculation rules used by ghs-repo-scan, ghs-backlog-score, ghs-backlog-board, and ghs-backlog-next. For canonical values, see `config.md`.

## Tier Definitions and Weights

| Tier | Label | Points per Check | Description |
|------|-------|-----------------|-------------|
| 1 | Required | 4 | Non-negotiable for any public or team-shared repo |
| 2 | Recommended | 2 | Important for maintainability and collaboration |
| 3 | Nice to Have | 1 | Polish items signaling a mature project |

## Modules

Health checks are organized into **modules**. The `core` module always runs; language-specific modules activate based on stack detection. See `checks/index.md` for the full module registry.

| Module | Checks | Max Points | Weight (with lang module) | Weight (solo) |
|--------|--------|------------|---------------------------|---------------|
| Core | 40 | 74 | 60% | 100% |
| .NET | 23 | 34 | 40% | — |

## Score Calculation Formula

### Single module (core only)

```
earned_points = sum(points for each PASS check)
possible_points = sum(points for each check that is PASS or FAIL)
percentage = round(earned_points / possible_points * 100)
```

### Multiple modules (core + language)

```
core_pct = round(core_earned / core_possible * 100)
lang_pct = round(lang_earned / lang_possible * 100)
score    = round(core_pct * 0.6 + lang_pct * 0.4)
```

- Core always contributes 60% of the combined score.
- A single language module contributes 40%.
- If multiple language modules are active, they split the 40% equally (e.g., 2 modules = 20% each).

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
| 5 | Core module items before language module items |
| 6 | Oldest issue (by creation date) for issue items |
| 7 | Alphabetical (final tiebreaker) |

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
