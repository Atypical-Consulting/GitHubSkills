# Scoring

GHS uses a tiered scoring system to measure repository health.

## Point Values

| Tier | Points | Description |
|------|--------|-------------|
| Tier 1 | 4 | Required --- fundamental repo quality |
| Tier 2 | 2 | Recommended --- professional standards |
| Tier 3 | 1 | Nice to Have --- polish and completeness |

## Maximum Score

| Tier | Checks | Points Each | Subtotal |
|------|--------|-------------|----------|
| Tier 1 | 4 | 4 | 16 |
| Tier 2 | 22 | 2 | 44 |
| Tier 3 | 14 | 1 | 14 |
| **Total** | **40** | | **74** |

## Calculation

```
score = earned_points / possible_points x 100
```

Rounded to the nearest integer.

## Special Rules

### WARN Exclusion
If a check returns WARN (cannot verify), it is excluded from both earned AND possible totals. This prevents penalizing repos for checks that can't be verified (e.g., permission issues).

### INFO Exclusion
Three checks are INFO-only and carry no points:
- Funding (documentation)
- Discussions Enabled (repo-settings)
- Commit Signoff (repo-settings)

These are reported but don't affect the score.

## Progress Bar

Scores are visualized with an 8-character progress bar:
```
Score: 52/74 (70%) ██████░░
```

Characters: filled with `█` and empty with `░`.

## Score Interpretation

| Range | Meaning |
|-------|---------|
| 90-100% | Excellent --- repo follows best practices |
| 70-89% | Good --- some improvements available |
| 50-69% | Fair --- notable gaps in repo quality |
| Below 50% | Needs attention --- fundamental issues |
