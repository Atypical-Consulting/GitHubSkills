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
  version: 1.0.0
routes-to:
  - ghs-backlog-fix
  - ghs-backlog-board
routes-from:
  - ghs-repo-scan
  - ghs-backlog-board
---

# Backlog Sync

Sync local health backlog items to GitHub Issues for team visibility and tracking. Creates issues for FAIL items, updates existing synced issues, and closes resolved ones.

<context>
Purpose: Publish health check findings as GitHub Issues so they are visible to collaborators and manageable through GitHub's native UI.

Roles:
1. **Syncer** (you) — reads local backlog items, creates/updates/closes GitHub Issues, updates local files with sync metadata

No sub-agents — this is a single-actor skill that orchestrates GitHub API calls.

Shared docs:
- `../shared/gh-prerequisites.md` — authentication, repo detection, error handling
- `../shared/backlog-format.md` — file naming, metadata formats, status values
- `../shared/sync-format.md` — label taxonomy, issue title convention, body template, local metadata additions
- `../shared/edge-cases.md` — rate limiting, permission errors, bounded retries
- `../shared/item-categories.md` — item classification (Category A/B/CI)
</context>

<objective>
Sync local health backlog items to GitHub Issues.

Outputs:
- GitHub Issues created/updated/closed on the target repository
- Local backlog item files updated with `Synced Issue` and `Issue URL` metadata
- Updated SUMMARY.md if statuses changed
- Terminal report with sync actions taken

Next routing:
- Suggest `ghs-backlog-fix` to apply fixes — "To fix items: `/ghs-backlog-fix {owner}/{repo}`"
- Suggest `ghs-backlog-board` to see the updated dashboard
</objective>

<process>

## Input

The user provides a repo identifier: `owner/repo` or `owner_repo`.

If not provided, detect from the current git remote:
```bash
gh repo view --json nameWithOwner -q '.nameWithOwner'
```

## Phase 1 — Discover Local Items

Scan `backlog/{owner}_{repo}/health/` for all items. Parse each with:
```bash
python .claude/skills/shared/scripts/parse_backlog_item.py <path>
```

Build two lists:
1. **FAIL items**: Items with status FAIL — candidates for issue creation
2. **Resolved items**: Items with status PASS that have a `Synced Issue` field — candidates for issue closing

Skip items with status WARN or INFO — these are not actionable.

## Phase 2 — Ensure Labels Exist

Pre-check: verify the target repo has issues enabled:
```bash
gh repo view {owner}/{repo} --json hasIssuesEnabled -q '.hasIssuesEnabled'
```

If issues are disabled, abort with a clear message:
```
Issues are disabled on {owner}/{repo}. Enable them in Settings → General → Features → Issues, then re-run sync.
```

Create the label taxonomy defined in `../shared/sync-format.md` using idempotent commands:
```bash
gh label create "ghs:health-check" --color "7057ff" --description "Health check finding from ghs-repo-scan" --repo {owner}/{repo} 2>&1 || true
gh label create "tier:1" --color "d73a4a" --description "Tier 1 — Required" --repo {owner}/{repo} 2>&1 || true
gh label create "tier:2" --color "fbca04" --description "Tier 2 — Recommended" --repo {owner}/{repo} 2>&1 || true
gh label create "tier:3" --color "0e8a16" --description "Tier 3 — Nice to Have" --repo {owner}/{repo} 2>&1 || true
gh label create "category:api-only" --color "c5def5" --description "Fix requires API calls only" --repo {owner}/{repo} 2>&1 || true
gh label create "category:file-change" --color "bfd4f2" --description "Fix requires file changes" --repo {owner}/{repo} 2>&1 || true
gh label create "category:ci" --color "d4c5f9" --description "Fix requires CI workflow changes" --repo {owner}/{repo} 2>&1 || true
```

## Phase 3 — Fetch Existing Synced Issues

Query GitHub for all issues with the `ghs:health-check` label:
```bash
gh issue list --label "ghs:health-check" --state all --json number,title,state,body --limit 500 --repo {owner}/{repo}
```

Build a lookup map keyed by title: `title → {number, state, body}`.

This enables dedup — matching is done by the `[Health] {Check Name}` title convention from `../shared/sync-format.md`.

## Phase 4 — Sync Loop

### For each FAIL item:

Construct the expected issue title: `[Health] {Check Name}` (using the item's H1 title).

Look up the title in the existing issues map:

**No matching issue — Create:**
1. Build the issue body from the template in `../shared/sync-format.md`
2. Determine labels: `ghs:health-check`, `tier:{N}`, and the appropriate `category:*` label based on the item's category (use `../shared/item-categories.md` to classify)
3. Create the issue:
   ```bash
   gh issue create --title "[Health] {Check Name}" --body "{body}" --label "ghs:health-check,tier:{N},category:{cat}" --repo {owner}/{repo}
   ```
4. Record the action: `Created`

**Open matching issue — Update (if changed):**
1. Compare the hidden metadata comment in the existing body with current item data
2. If content has changed (tier, points, or section content differs), update the body:
   ```bash
   gh issue edit {number} --body "{new_body}" --repo {owner}/{repo}
   ```
3. If content unchanged, skip
4. Record the action: `Updated` or `Already synced`

**Closed matching issue (check still fails) — Reopen:**
1. Reopen the issue with a comment explaining the check still fails:
   ```bash
   gh issue reopen {number} --repo {owner}/{repo}
   gh issue comment {number} --body "This check is still failing as of {date}. Reopening." --repo {owner}/{repo}
   ```
2. Record the action: `Reopened`

### For each PASS item with `Synced Issue`:

Look up the synced issue number:
```bash
gh issue view {number} --json state -q '.state' --repo {owner}/{repo}
```

**Issue still open — Close:**
```bash
gh issue close {number} --comment "Check now passes as of {date}. Closing." --repo {owner}/{repo}
```
Record the action: `Closed (resolved)`

**Issue already closed — Skip:**
Record the action: `Already closed`

## Phase 5 — Update Local Files

For each item that was created or matched to an issue:

1. Add or update `Synced Issue` and `Issue URL` rows in the local backlog item's metadata table:
   ```markdown
   | **Synced Issue** | #{number} |
   | **Issue URL** | https://github.com/{owner}/{repo}/issues/{number} |
   ```
2. If the rows already exist, update them in place. If they don't exist, append them after the `| **Detected** |` row.

Update `SUMMARY.md` if any statuses changed during the sync (e.g., a PASS item's issue was closed).

## Phase 6 — Report

Display a summary table:

```
## Sync Report: {owner}/{repo}

| # | Item | Tier | Action | Issue |
|---|------|------|--------|-------|
| 1 | README | T1 | Created | #42 |
| 2 | LICENSE | T1 | Already synced | #38 |
| 3 | Branch Protection | T1 | Updated | #39 |
| 4 | .editorconfig | T2 | Created | #43 |
| 5 | CI Workflow Health | T2 | Closed (resolved) | #35 |
...

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

</process>

## Edge Cases

- **Idempotent**: Title-based dedup prevents duplicate issues. Running sync multiple times is safe.
- **Issues disabled**: Pre-check in Phase 2 detects this and aborts with a clear message.
- **User-edited issue bodies**: The hidden `<!-- ghs-sync:metadata ... -->` comment is preserved. Visible content is not overwritten unless the metadata (tier, points, slug) has changed. Use `--force` flag to overwrite all content.
- **Rate limiting**: Follow `../shared/edge-cases.md` retry pattern. Do not loop — if rate-limited, report progress so far and suggest re-running later.
- **Missing local items**: If the backlog directory doesn't exist, suggest running `ghs-repo-scan` first.
- **No FAIL items**: If all items are PASS, report "All checks passing — nothing to sync" and handle any open issues that should be closed.
- **Large repos**: If there are many health items, process them sequentially to avoid rate limits.

## Examples

**Example 1: First sync**
User says: "sync backlog phmatray/NewSLN"
Result: Creates labels, creates GitHub Issues for all FAIL health items, updates local files with issue references, displays report.

**Example 2: Re-sync after fixes**
User says: "sync backlog phmatray/NewSLN"
Result: Detects existing issues, closes ones where checks now pass, reopens ones that regressed, creates new ones for new failures.

**Example 3: Sync after backlog-fix**
User says: "publish backlog"
Result: Closes synced issues for items that backlog-fix changed to PASS, keeps remaining FAIL issues open.

## Troubleshooting

**"Issues are disabled"**
Enable Issues in the repo's Settings → General → Features → Issues.

**"Label already exists" warnings**
These are expected — label creation is idempotent. The `2>&1 || true` suffix suppresses the error.

**Duplicate issues created**
This shouldn't happen if the title convention is followed. If it does, manually close duplicates and ensure titles match `[Health] {Check Name}` exactly.

**Rate limit errors**
GitHub's API has rate limits. If hit, the skill reports progress so far. Wait for the rate limit window to reset and re-run.
