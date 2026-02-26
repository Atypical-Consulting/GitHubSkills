# ghs-backlog-next

Recommends the single highest-impact backlog item to fix across all audited repositories.

::: info Skill Info
**Version:** 2.0.0
**Trigger phrases:** "what should I fix next?", "what's the highest impact fix?", "next item", "priority item", "next action", "recommend something to fix"
:::

## What It Does

`ghs-backlog-next` scans all backlog data and returns one recommendation: the single most impactful item you should fix next. It is fast and focused -- no dashboard, no tables, just a clear recommendation with the exact command to apply it.

### Priority Algorithm

The algorithm selects the highest-impact item by applying these rules in order:

1. **Lowest health score percentage repo first** — the repo that needs the most help
2. **Health items over issues** — health items improve the repo's structural foundation
3. **Lowest tier number** — Tier 1 (Required) before Tier 2 (Recommended) before Tier 3 (Nice to Have)
4. **Highest point value** — within the same tier, pick the item worth more points
5. **Oldest issue** — for issues, pick the oldest by creation date
6. **Alphabetical** — final tiebreaker

## Example

```
## Next: LICENSE

Repository:  phmatray/Formidable (22% health)
Source:      Health Check — Tier 1 (Required)
Points:      4
Category:    B (file changes)

Why this item: Lowest-scoring repo, highest-tier failing check.

To apply:
  /ghs-backlog-fix backlog/phmatray_Formidable/health/tier-1--license.md

Runner-up: README for phmatray/NewSLN (67% health, Tier 1, 4 pts)
```

When everything is done:

```
## All caught up!

All health checks are passing and all issues have been addressed.
To re-scan for changes: /ghs-repo-scan phmatray/Formidable
```

## Routes To

After seeing the recommendation, GHS suggests:

- **[ghs-backlog-fix](/skills/ghs-backlog-fix)** — with the exact command to apply the recommended item
- **[ghs-repo-scan](/skills/ghs-repo-scan)** — if everything is done or data is stale

## Technical Details

| Property | Value |
|----------|-------|
| Allowed tools | `Bash(python3:*)`, `Read`, `Glob` |
| Spawns sub-agents | No — lightweight read-only recommender |
| Phases | 3 (Discover Failing Items, Select Highest-Impact, Display Recommendation) |
| Requires | `python3`, backlog data from a prior `ghs-repo-scan` run |
| Re-run safe | Yes — read-only, no side effects |
