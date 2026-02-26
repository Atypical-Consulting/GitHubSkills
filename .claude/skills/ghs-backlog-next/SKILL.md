---
name: ghs-backlog-next
description: >
  Recommends the highest-impact next backlog item to fix across all audited repositories. Use this
  skill whenever the user wants a quick recommendation, asks "what should I work on next", "next item",
  "what's the most important fix", "highest impact item", "what to fix next", "priority item",
  "next action", or "recommend something to fix". Also trigger for "what's next" or just "next"
  in the context of backlog work.
  Do NOT use for full dashboards (use ghs-backlog-board), scanning repos (use ghs-repo-scan),
  or applying fixes directly (use ghs-backlog-fix).
allowed-tools: "Bash(python3:*) Read Glob"
compatibility: "Requires python3. Backlog data must exist from a prior ghs-repo-scan run."
license: MIT
metadata:
  author: phmatray
  version: 3.0.0
routes-to:
  - ghs-backlog-fix
  - ghs-repo-scan
routes-from:
  - ghs-backlog-board
---

# Backlog Next

Quickly find and recommend the **single** highest-impact backlog item to work on next. Returns one recommendation with the command to apply it.

No sub-agents — this is a lightweight, read-only skill.

## References

- `../shared/references/scoring-logic.md` — tier weights, priority algorithm, score formula
- `../shared/references/backlog-format.md` — directory layout, file naming, metadata format
- `../shared/references/output-conventions.md` — status indicators, table patterns, progress bars
- `../shared/config.md` — tier point values, stale scan threshold

## Anti-Patterns

| Anti-Pattern | Why It Fails | Do Instead |
|-------------|-------------|------------|
| Recommend an already-fixed (PASS) item | Wastes the user's time on completed work | Always check current status from backlog files before recommending |
| Recommend without verifying item still exists | File may have been deleted after a fix | Confirm the backlog file is present and status is FAIL or OPEN |
| Show multiple recommendations as a list | Defeats the purpose of "next ONE item" — causes decision paralysis | Return exactly one item; show a single runner-up line only if multiple repos exist |
| Guess the score instead of calculating | Produces wrong priority ordering | Always run `calculate_score.py` for accurate scores |
| Recommend WARN items as actionable | WARN means permission-blocked, user cannot fix it | Skip WARN items; only mention them if nothing else remains |

## Input

No input required. Scans all `backlog/` subdirectories automatically.

Optional: the user may specify a repo to limit the search — "next for phmatray/Formidable".

| Trigger | Example | Behavior |
|---------|---------|----------|
| General next | "what should I work on next?" | Scan all repos, pick the single best item |
| Repo-scoped next | "next for phmatray/Formidable" | Limit search to that repo only |
| After a fix | "next" | Previous fix is now PASS, pick the next best item |

## Process

### Phase 1 — Discover Failing Items

Scan `backlog/{owner}_{repo}/health/` across all repos (or the specified repo) for items with status **FAIL**.

For each item, extract:

| Field | Source |
|-------|--------|
| Repository | `owner/repo` from metadata table |
| Check name | From item title |
| Tier | From filename (`tier-{N}--{slug}.md`) |
| Points | Per tier: Tier 1 = 4, Tier 2 = 2, Tier 3 = 1 (see `scoring-logic.md`) |
| Status | Only keep FAIL; skip PASS, WARN, INFO |

Also check `backlog/{owner}_{repo}/issues/` for items with status **OPEN** — issues are secondary to health items.

Parse items programmatically:

```bash
python .claude/skills/shared/scripts/parse_backlog_item.py <path>
```

### Phase 2 — Select the Highest-Impact Item

Apply the priority algorithm (see `scoring-logic.md` for canonical definition):

| Priority | Rule |
|----------|------|
| 1 | Lowest health score percentage repo first |
| 2 | Health items over issues (structural foundation) |
| 3 | Lowest tier number (Tier 1 before Tier 2 before Tier 3) |
| 4 | Highest point value within same tier |
| 5 | Oldest issue (by creation date) for issue items |
| 6 | Alphabetical (final tiebreaker) |

Calculate per-repo scores:

```bash
python .claude/skills/shared/scripts/calculate_score.py backlog/{owner}_{repo}
```

Tie between repos with same score: pick the one with the most failing items.

### Phase 3 — Display Recommendation

#### Standard recommendation

```
## Next: {Check Name}

Repository:  {owner}/{repo} ({score}% health)
Source:      Health Check — Tier {N} ({Required|Recommended|Nice to Have})
Points:      {points}
Category:    {A (API-only) | B (file changes) | CI}

Why this item: {one sentence — e.g., "Lowest-scoring repo, highest-tier failing check."}

To apply:
  /ghs-backlog-fix backlog/{owner}_{repo}/health/tier-{N}--{slug}.md

{If item has a synced issue:}
GitHub Issue: https://github.com/{owner}/{repo}/issues/{number}
```

If there are multiple repos, also show the runner-up (one line only):

```
Runner-up: {Check Name} for {owner}/{repo} ({score}% health, Tier {N}, {points} pts)
```

#### All caught up

If all health items are PASS and all issues are CLOSED or have PRs:

```
## All caught up!

All health checks are passing and all issues have been addressed.
To re-scan for changes: /ghs-repo-scan {owner}/{repo}
```

## Good and Bad Examples

### Good: Clear single recommendation

```
## Next: LICENSE

Repository:  phmatray/Formidable (32% health)
Source:      Health Check — Tier 1 (Required)
Points:      4
Category:    B (file changes)

Why this item: Lowest-scoring repo, highest-tier failing check worth 4 points.

To apply:
  /ghs-backlog-fix backlog/phmatray_Formidable/health/tier-1--license.md
```

### Bad: Multiple recommendations dumped as a list

```
Here are the top 5 items you should work on:
1. LICENSE for phmatray/Formidable
2. README for phmatray/Formidable
3. .editorconfig for phmatray/Formidable
4. SECURITY.md for phmatray/Formidable
5. Branch protection for phmatray/Formidable
```

Why it is bad: defeats the purpose of "next ONE item" and creates decision paralysis. Use `ghs-backlog-board` for full lists.

### Bad: Recommending a PASS item

```
## Next: README.md

Repository:  phmatray/Formidable (75% health)
Source:      Health Check — Tier 1 (Required)
Points:      4

To apply:
  /ghs-backlog-fix backlog/phmatray_Formidable/health/tier-1--readme.md
```

Why it is bad: README already has status PASS. Always verify the item's current status before recommending.

## Edge Cases

| Situation | Action |
|-----------|--------|
| No `backlog/` directory | Tell user no scans have been run; suggest `/ghs-repo-scan {owner}/{repo}` |
| All items passing | Display the "All caught up!" message |
| Only WARN items left | Explain remaining items are permission-blocked; suggest checking access |
| Multiple repos tied on score | Pick the one with the most failing items |
| Stale data (scan > 30 days old) | Note it and suggest re-scanning: `/ghs-repo-scan {owner}/{repo}` |

## Routing

| After This Skill | Suggest |
|-----------------|---------|
| User wants to apply the fix | `/ghs-backlog-fix backlog/{owner}_{repo}/health/tier-{N}--{slug}.md` |
| Everything is done | `/ghs-repo-scan {owner}/{repo}` to re-scan for changes |
| User wants a full overview | `/ghs-backlog-board` for the multi-repo dashboard |
