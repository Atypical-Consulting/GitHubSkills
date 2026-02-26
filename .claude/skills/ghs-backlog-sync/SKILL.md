---
name: ghs-backlog-sync
description: >
  Syncs local health backlog items to GitHub Issues — creates issues for FAIL items, updates existing
  synced issues, closes resolved ones. Use this skill whenever the user wants to sync backlog items
  to GitHub, create issues from health checks, push findings to GitHub, publish backlog items, or
  says things like "sync backlog", "create issues from health checks", "push findings to GitHub",
  "publish backlog", "sync health items", "sync findings to issues", or "create GitHub issues from scan".
  Do NOT use for scanning repos (use ghs-repo-scan), applying fixes (use ghs-backlog-fix), or viewing backlog (use ghs-backlog-board).
allowed-tools: "Bash(gh:*) Bash(python3:*) Read Write Edit Glob Grep"
compatibility: "Requires gh CLI (authenticated), python3, network access. Target repo must have Issues enabled."
license: MIT
metadata:
  author: phmatray
  version: 2.0.0
routes-to:
  - ghs-backlog-fix
  - ghs-backlog-board
routes-from:
  - ghs-repo-scan
  - ghs-backlog-board
---

# Backlog Sync

Sync local health backlog items to GitHub Issues for team visibility and tracking.

## Anti-Patterns

- **Never create duplicate issues.** Title-based dedup (`[Health] {Check Name}`) is the sole guard — always check existing issues before creating.
- **Never close issues manually reopened by users.** If a PASS item's synced issue was reopened by a human after the skill closed it, leave it open.
- **Never sync PASS items as new issues.** Only FAIL items become issues. PASS items only trigger closing of their previously-synced issue.
- **Never modify backlog item content during sync.** Only add/update `Synced Issue` and `Issue URL` metadata rows. The backlog files are owned by `ghs-repo-scan`.
- **Never retry in a loop on rate limits.** Report progress so far and tell the user to re-run later.

## Scope Boundary

This skill is a **one-way publisher**: local backlog health findings go to GitHub Issues. It does not pull issue state back into backlog files, change item statuses, or apply fixes. The only local writes are the two sync metadata rows (`Synced Issue`, `Issue URL`).

## References

> Shared docs consumed by this skill — read them for full field definitions and patterns.

| Reference | What It Provides |
|-----------|-----------------|
| `shared/references/gh-cli-patterns.md` | Auth check, repo detection, issue CRUD, label creation, error codes |
| `shared/references/backlog-format.md` | Directory layout, file naming, metadata table schema, status values |
| `shared/sync-format.md` | Label taxonomy, issue title convention, body template, hidden metadata comment |
| `shared/item-categories.md` | Category A/B/CI classification for label assignment |
| `shared/references/output-conventions.md` | Status indicators, table formats, summary block pattern |
| `shared/edge-cases.md` | Rate limiting, permission errors, bounded retries |

## Sync Status Mapping

| Backlog Status | Has Synced Issue? | GitHub Issue State | Action |
|---------------|-------------------|-------------------|--------|
| FAIL | No | — | **Create** new issue |
| FAIL | Yes | Open | **Update** if content changed, else skip |
| FAIL | Yes | Closed | **Reopen** with comment |
| PASS | Yes | Open | **Close** with comment |
| PASS | Yes | Closed | Skip (already resolved) |
| PASS | No | — | Skip (nothing to sync) |
| WARN / INFO | Any | Any | Skip (not actionable) |

## Issue Template Fields

Issues created by this skill follow the body template in `shared/sync-format.md`:

| Field | Source | Example |
|-------|--------|---------|
| Hidden metadata comment | Slug, tier, points, category, detected date | `<!-- ghs-sync:metadata slug:license tier:1 ... -->` |
| Tier | Backlog item metadata | `1 — Required` |
| Points | Backlog item metadata | `4` |
| Category | `shared/item-categories.md` lookup | `B (file changes)` |
| Detected | Backlog item metadata | `2026-01-15` |
| What's Missing | Backlog item section | Content from item |
| Why It Matters | Backlog item section | Content from item |
| How to Fix | Backlog item section | Content from item |
| Acceptance Criteria | Backlog item section | Checklist from item |

## Good and Bad Examples

### Issue Titles

| Example | Verdict | Why |
|---------|---------|-----|
| `[Health] LICENSE` | GOOD | Matches convention, dedup-safe |
| `[Health] Branch Protection` | GOOD | Matches convention |
| `Missing LICENSE file` | BAD | Breaks title-based dedup, will create duplicates |
| `[Health] license` | BAD | Case mismatch — won't match existing `[Health] LICENSE` |

### Issue Bodies

**GOOD** — includes hidden metadata, structured fields, acceptance criteria:
```markdown
<!-- ghs-sync:metadata
slug: license
tier: 1
points: 4
category: B
detected: 2026-01-15
-->

| Field | Value |
|-------|-------|
| **Tier** | 1 — Required |
| **Points** | 4 |
| **Category** | B (file changes) |
| **Detected** | 2026-01-15 |

## What's Missing

No LICENSE file found in the repository root.

## How to Fix

Add a LICENSE file matching the project's declared license.

## Acceptance Criteria

- [ ] LICENSE file exists in repository root
- [ ] License type matches package metadata
```

**BAD** — no metadata comment, no structure, unactionable:
```markdown
This repo needs a license. Please add one.
```

## Process

### Input

The user provides a repo identifier: `owner/repo` or `owner_repo`.

If not provided, detect from the current git remote (see `shared/references/gh-cli-patterns.md` — Repo Detection).

### Phase 1 — Discover Local Items

**Rule:** Only FAIL items become issues. PASS items with a synced issue trigger closing. WARN/INFO items are always skipped.

**Trigger:** Backlog directory `backlog/{owner}_{repo}/health/` exists and contains item files.

Scan all items and parse each with:
```bash
python3 .claude/skills/shared/scripts/parse_backlog_item.py <path>
```

Build two lists:

| List | Criteria | Purpose |
|------|----------|---------|
| FAIL items | Status = FAIL | Candidates for issue creation/update |
| Resolved items | Status = PASS AND has `Synced Issue` field | Candidates for issue closing |

**Example:** If `tier-1--license.md` has Status=FAIL and no Synced Issue, it goes into the FAIL list for creation. If `tier-2--editorconfig.md` has Status=PASS and Synced Issue=#43, it goes into the Resolved list for closing.

If the backlog directory does not exist, abort: `No backlog found for {owner}/{repo}. Run /ghs-repo-scan first.`

If all items are PASS, report: `All checks passing — nothing to sync.` Then handle any resolved items that need closing.

### Phase 2 — Ensure Labels Exist

Pre-check: verify the target repo has issues enabled (see `shared/references/gh-cli-patterns.md` — Issues enabled).

If issues are disabled, abort:
```
Issues are disabled on {owner}/{repo}. Enable them in Settings > General > Features > Issues, then re-run sync.
```

Create labels from the taxonomy in `shared/sync-format.md` using idempotent commands (see `shared/references/gh-cli-patterns.md` — Label Operations):

```bash
gh label create "ghs:health-check" --color "7057ff" --description "Health check finding from ghs-repo-scan" --repo {owner}/{repo} 2>&1 || true
gh label create "tier:1" --color "d73a4a" --description "Tier 1 — Required" --repo {owner}/{repo} 2>&1 || true
gh label create "tier:2" --color "fbca04" --description "Tier 2 — Recommended" --repo {owner}/{repo} 2>&1 || true
gh label create "tier:3" --color "0e8a16" --description "Tier 3 — Nice to Have" --repo {owner}/{repo} 2>&1 || true
gh label create "category:api-only" --color "c5def5" --description "Fix requires API calls only" --repo {owner}/{repo} 2>&1 || true
gh label create "category:file-change" --color "bfd4f2" --description "Fix requires file changes" --repo {owner}/{repo} 2>&1 || true
gh label create "category:ci" --color "d4c5f9" --description "Fix requires CI workflow changes" --repo {owner}/{repo} 2>&1 || true
```

### Phase 3 — Fetch Existing Synced Issues

Query GitHub for all issues with the `ghs:health-check` label (see `shared/references/gh-cli-patterns.md` — Issue Operations):

```bash
gh issue list --label "ghs:health-check" --state all --json number,title,state,body --limit 500 --repo {owner}/{repo}
```

Build a lookup map: `title -> {number, state, body}`.

This enables title-based dedup per the convention in `shared/sync-format.md`.

### Phase 4 — Sync Loop

For each item, apply the action from the **Sync Status Mapping** table above.

#### Creating a New Issue

**Rule:** Only create when no matching `[Health] {Check Name}` title exists in any state.

1. Build the issue body from `shared/sync-format.md` — Issue Body Template
2. Classify the item using `shared/item-categories.md` to determine the `category:*` label
3. Create:
   ```bash
   gh issue create --title "[Health] {Check Name}" --body "{body}" --label "ghs:health-check,tier:{N},category:{cat}" --repo {owner}/{repo}
   ```

#### Updating an Existing Open Issue

**Rule:** Only update if the hidden metadata comment shows tier, points, or category has changed. Never overwrite user edits to visible content unless metadata diverges.

1. Compare hidden `<!-- ghs-sync:metadata ... -->` in existing body with current item data
2. If changed: `gh issue edit {number} --body "{new_body}" --repo {owner}/{repo}`
3. If unchanged: skip

#### Reopening a Closed Issue

**Rule:** Only reopen if the check still fails. The issue was closed (either by sync or manually) but the underlying problem persists.

```bash
gh issue reopen {number} --repo {owner}/{repo}
gh issue comment {number} --body "This check is still failing as of {date}. Reopening." --repo {owner}/{repo}
```

#### Closing a Resolved Issue

**Rule:** Only close issues where the local item status changed to PASS. Never close issues that were manually reopened by users without a corresponding PASS status.

```bash
gh issue close {number} --comment "Check now passes as of {date}. Closing." --repo {owner}/{repo}
```

### Phase 5 — Update Local Files

For each item that was created or matched to an issue, add or update the sync metadata rows in the local backlog item (see `shared/references/backlog-format.md` — Health Item Metadata):

```markdown
| **Synced Issue** | #{number} |
| **Issue URL** | https://github.com/{owner}/{repo}/issues/{number} |
```

If the rows already exist, update them in place. If they don't exist, append them after the `| **Detected** |` row.

Update `SUMMARY.md` if any statuses changed during the sync.

### Phase 6 — Report

Display a summary table following `shared/references/output-conventions.md`:

```
## Sync Report: {owner}/{repo}

| # | Item | Tier | Action | Issue |
|---|------|------|--------|-------|
| 1 | README | T1 | Created | #42 |
| 2 | LICENSE | T1 | Already synced | #38 |
| 3 | Branch Protection | T1 | Updated | #39 |
| 4 | .editorconfig | T2 | Created | #43 |
| 5 | CI Workflow Health | T2 | Closed (resolved) | #35 |

---

Summary:
  Created: {n_created}
  Updated: {n_updated}
  Reopened: {n_reopened}
  Closed: {n_closed}
  Already synced: {n_synced}
  Skipped: {n_skipped}

To fix items: /ghs-backlog-fix {owner}/{repo}
To see dashboard: /ghs-backlog-board
```

## Edge Cases

- **Idempotent**: Title-based dedup prevents duplicate issues. Running sync multiple times is safe.
- **Issues disabled**: Pre-check in Phase 2 detects this and aborts with a clear message.
- **User-edited issue bodies**: The hidden `<!-- ghs-sync:metadata ... -->` comment is preserved. Visible content is not overwritten unless the metadata (tier, points, slug) has changed.
- **Rate limiting**: Follow `shared/edge-cases.md` retry pattern. Do not loop — if rate-limited, report progress so far and suggest re-running later.
- **Missing local items**: If the backlog directory doesn't exist, suggest running `ghs-repo-scan` first.
- **No FAIL items**: Report "All checks passing — nothing to sync" and handle any open issues that should be closed.
- **Large repos**: Process items sequentially to avoid rate limits. Do not parallelize API calls.
