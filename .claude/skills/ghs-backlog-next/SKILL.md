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
allowed-tools: "Bash(gh:*) Bash(jq:*) Bash(bc:*)"
compatibility: "Requires gh CLI (authenticated) with project scope. Project data must exist from a prior ghs-repo-scan run."
license: MIT
metadata:
  author: phmatray
  version: 6.0.0
routes-to:
  - ghs-backlog-fix
  - ghs-repo-scan
routes-from:
  - ghs-backlog-board
---

# Backlog Next

Quickly find and recommend the **single** highest-impact backlog item to work on next. Returns one recommendation with the command to apply it.

No sub-agents — this is a lightweight, read-only skill.

<context>
Purpose: Read-only recommendation engine that selects the single highest-impact project item using the priority algorithm.

Roles:
1. **Recommender** (you) — queries GitHub Project items, applies priority algorithm, displays the top recommendation

No sub-agents — this is a lightweight, read-only skill.

### Shared References

| Reference | Path | Purpose |
|-----------|------|---------|
| Scoring Logic | `../shared/references/scoring-logic.md` | Tier weights, priority algorithm, score formula |
| Projects Format | `../shared/references/projects-format.md` | Project naming, item schema, jq scoring pipelines, state issue lookup |
| Output Conventions | `../shared/references/output-conventions.md` | Status indicators, table patterns, progress bars |
| State Persistence | `../shared/references/state-persistence.md` | State issue format, blocker/decision/session data for filtering |
| Config | `../shared/references/config.md` | Scoring constants, display thresholds |
| gh CLI Patterns | `../shared/references/gh-cli-patterns.md` | Project Operations section — auth check, project discovery, item queries |
</context>

<anti-patterns>

## Anti-Patterns

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Recommend an already-fixed (Done) item | Always check current Status from the project item before recommending | Wastes the user's time on completed work |
| Recommend without verifying item still exists | Confirm the project item is present and status is `Todo` | Item may have been deleted or moved to Done after a fix |
| Show multiple recommendations as a list | Return exactly one item; show a single runner-up line only if multiple repos exist | Defeats the purpose of "next ONE item" — causes decision paralysis |
| Guess the score instead of calculating | Always use the jq pipeline from `projects-format.md` for accurate scores | Produces wrong priority ordering |
| Recommend WARN items as actionable | Skip WARN items (they are never in the project); only mention them if nothing else remains | WARN means permission-blocked; user cannot fix it |
| Recommend items with ACTIVE blockers in the state issue | Read the state issue and exclude blocked/recently-failed/skipped items | Wastes time on items that are known to be unresolvable right now |
| Ignore the state issue when it exists | Always check the state issue before recommending — it has blockers, failures, and skip decisions | Missing context leads to recommending items that will fail again |

</anti-patterns>

## Input

No input required. Discovers all `[GHS]` projects for the owner automatically.

Optional: the user may specify a repo to limit the search — "next for phmatray/Formidable".

| Trigger | Example | Behavior |
|---------|---------|----------|
| General next | "what should I work on next?" | Scan all `[GHS]` projects, pick the single best item |
| Repo-scoped next | "next for phmatray/Formidable" | Limit search to `[GHS] phmatray/Formidable` project only |
| After a fix | "next" | Previous fix is now Done, pick the next best item |

## Pre-flight

Verify project scope before any project API call:

```bash
gh auth status 2>&1 | grep -q "project" || echo "[FAIL] Run: gh auth refresh -s project"
```

<process>

## Process

### Phase 1 — Discover Failing Items

Discover all `[GHS]` projects for the owner (or the specified project):

```bash
gh project list --owner {owner} --format json \
  --jq '.projects[] | select(.title | startswith("[GHS]"))'
```

For each project, query all items and filter for health check items in the `Todo` column:

```bash
ITEMS=$(gh project item-list $PROJECT_NUM --owner {owner} --format json --limit 500)

# Health check items that need fixing
FAIL_ITEMS=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .status == "Todo")]')
```

For each failing item, extract:

| Field | Source |
|-------|--------|
| Repository | From project title (strip `[GHS] ` prefix) |
| Check name | From item title (strip `[Health] ` prefix) |
| Tier | From item `tier` field (`1 — Required`, `2 — Recommended`, `3 — Nice to Have`) |
| Points | From item `points` field (4, 2, or 1) |
| Slug | From item `slug` field |
| Category | From item `category` field |
| Status | `Todo` only; skip `Done` and `In Progress` |

Also look for `GitHub Issue` items in the `Todo` column — issues are secondary to health items:

```bash
OPEN_ISSUES=$(echo "$ITEMS" | jq '[.items[] | select(.source == "GitHub Issue" and .status == "Todo")]')
```

### Phase 1.5 — Filter Using State Issue

For each repo, look up the state issue if it exists:

```bash
gh issue list --repo {owner}/{repo} --label "ghs:state" --state open \
  --json number,title,body --limit 1
```

Use the state issue body to exclude items from the candidate pool:

| State Issue Data | Filter Rule |
|-----------------|-------------|
| **Active blockers** | Exclude items listed in the `Affected Items` column of ACTIVE blockers |
| **Last session failures** | Exclude items that FAILED in the most recent session (unless user says "retry") |
| **Decisions with skip** | Exclude items the user explicitly decided to skip |

> **Rule:** State issue filtering happens before the priority algorithm. Only unblocked, non-failed, non-skipped items enter the ranking.
>
> **Trigger:** State issue exists for the repo being evaluated
>
> **Example:** State issue has `branch-protection` as affected by an ACTIVE blocker "No admin access" — skip `[Health] Branch Protection` project item even though it is Tier 1 with 4 points.

If no state issue exists for the repo, skip this phase — all Todo health items are candidates.

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

Calculate per-repo scores using the jq pipeline from `projects-format.md`:

```bash
ITEMS=$(gh project item-list $PROJECT_NUM --owner {owner} --format json --limit 500)
EARNED=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .status == "Done") | .points] | add // 0')
POSSIBLE=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and (.status == "Todo" or .status == "Done")) | .points] | add // 0')
SCORE=$(echo "scale=0; $EARNED * 100 / $POSSIBLE" | bc)
```

Alternatively, read the cached score from the `[GHS Score]` item for efficiency:

```bash
SCORE_BODY=$(echo "$ITEMS" | jq -r '.items[] | select(.title == "[GHS Score]") | .body' | jq '.score')
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
{If items were filtered by state issue:}
Skipped: {N} items excluded (blocked: {b}, recent failures: {f}, user-skipped: {s})

To apply:
  /ghs-backlog-fix {owner}/{repo} --item {slug}

{If item has a linked GitHub issue:}
GitHub Issue: https://github.com/{owner}/{repo}/issues/{number}
```

If there are multiple repos, also show the runner-up (one line only):

```
Runner-up: {Check Name} for {owner}/{repo} ({score}% health, Tier {N}, {points} pts)
```

#### All caught up

If all health items are Done and all issues are Done or In Progress:

```
## All caught up!

All health checks are passing and all issues have been addressed.
To re-scan for changes: /ghs-repo-scan {owner}/{repo}
```

</process>

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
  /ghs-backlog-fix phmatray/Formidable --item license
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

### Bad: Recommending a Done item

```
## Next: README.md

Repository:  phmatray/Formidable (75% health)
Source:      Health Check — Tier 1 (Required)
Points:      4

To apply:
  /ghs-backlog-fix phmatray/Formidable --item readme
```

Why it is bad: README project item has status `Done`. Always verify the item's current Status field before recommending.

## Edge Cases

| Situation | Action |
|-----------|--------|
| No GitHub Projects found | Tell user no scans have been run; suggest `/ghs-repo-scan {owner}/{repo}` |
| All items Done | Display the "All caught up!" message |
| Only WARN items left | Explain remaining items are permission-blocked (not in project); suggest checking access |
| Multiple repos tied on score | Pick the one with the most failing items |
| Stale data (`[GHS Score]` updated > 30 days ago) | Note it and suggest re-scanning: `/ghs-repo-scan {owner}/{repo}` |
| All Todo items blocked by state issue | Show "All remaining items are blocked" with blocker summary; suggest resolving blockers |
| User says "retry" after blocked recommendation | Ignore state issue filters for that item and recommend it anyway |
| No state issue exists | Normal flow — all Todo items are candidates (no filtering) |

## Routing

| After This Skill | Suggest |
|-----------------|---------|
| User wants to apply the fix | `/ghs-backlog-fix {owner}/{repo} --item {slug}` |
| Everything is done | `/ghs-repo-scan {owner}/{repo}` to re-scan for changes |
| User wants a full overview | `/ghs-backlog-board` for the multi-repo dashboard |
