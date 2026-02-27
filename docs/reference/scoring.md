# Scoring

GHS uses a modular, tiered scoring system to measure repository health.

## Modules

| Module | Checks | Max Points | Weight (with lang module) | Weight (solo) |
|--------|--------|------------|---------------------------|---------------|
| Core | 40 scored + 3 INFO | 74 | 60% | 100% |
| .NET | 20 scored + 3 INFO | 34 | 40% | --- |

## Point Values

| Tier | Points | Description |
|------|--------|-------------|
| Tier 1 | 4 | Required --- fundamental quality |
| Tier 2 | 2 | Recommended --- professional standards |
| Tier 3 | 1 | Nice to Have --- polish and completeness |

## Core Module Maximum

| Tier | Checks | Points Each | Subtotal |
|------|--------|-------------|----------|
| Tier 1 | 4 | 4 | 16 |
| Tier 2 | 22 | 2 | 44 |
| Tier 3 | 14 | 1 | 14 |
| **Total** | **40** | | **74** |

## .NET Module Maximum

| Tier | Checks | Points Each | Subtotal |
|------|--------|-------------|----------|
| Tier 1 | 2 | 4 | 8 |
| Tier 2 | 8 | 2 | 16 |
| Tier 3 | 10 | 1 | 10 |
| **Total** | **20** | | **34** |

## Calculation

### Single module (core only)

```
score = earned_points / possible_points x 100
```

### Multiple modules (core + language)

Each module is scored independently, then combined:

```
core_pct = core_earned / core_possible x 100
lang_pct = lang_earned / lang_possible x 100
combined = round(core_pct x 0.6 + lang_pct x 0.4)
```

All percentages rounded to the nearest integer.

## Special Rules

### WARN Exclusion
If a check returns WARN (cannot verify), it is excluded from both earned AND possible totals. This prevents penalizing repos for checks that can't be verified (e.g., permission issues).

### INFO Exclusion
INFO checks carry no points and are purely informational:

**Core:** Funding, Discussions Enabled, Commit Signoff

**.NET:** Target Framework, Package Count, Build System

### Module Priority
When recommending next actions, core module items take priority over language module items at the same tier and point value.

## Progress Bar

Scores are visualized with an 8-character progress bar:
```
Score: 52/74 (70%) ██████░░
```

Characters: filled with `█` and empty with `░`. Filled = `round(percentage / 100 x 8)`.

## Score Interpretation

| Range | Meaning |
|-------|---------|
| 90-100% | Excellent --- repo follows best practices |
| 70-89% | Good --- some improvements available |
| 50-69% | Fair --- notable gaps in repo quality |
| Below 50% | Needs attention --- fundamental issues |
