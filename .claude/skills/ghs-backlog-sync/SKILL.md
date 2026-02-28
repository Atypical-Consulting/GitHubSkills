---
name: ghs-backlog-sync
description: >
  Promotes draft health items in a GitHub Project to real GitHub Issues for team visibility.
  Creates issues from draft items in the Todo column with Source = Health Check, replaces drafts
  with linked issues in the project, and copies custom field values.
  Use this skill whenever the user wants to sync health findings to GitHub Issues, promote draft
  project items to real issues, create issues from health checks, push findings to GitHub, publish
  health items for the team, or says things like "sync backlog", "create issues from health checks",
  "push findings to GitHub", "publish backlog", "sync health items", "sync findings to issues",
  "promote drafts", or "create GitHub issues from scan".
  Do NOT use for scanning repos (use ghs-repo-scan), applying fixes (use ghs-backlog-fix), or viewing backlog (use ghs-backlog-board).
allowed-tools: "Bash(gh:*) Bash(jq:*) Read Write Edit Glob Grep"
compatibility: "Requires gh CLI (authenticated, with project scope), jq, network access. Target repo must have Issues enabled."
license: MIT
metadata:
  author: phmatray
  version: 4.0.0
routes-to:
  - ghs-backlog-fix
  - ghs-backlog-board
routes-from:
  - ghs-repo-scan
  - ghs-backlog-board
---

# Backlog Sync

Promote draft health items in a GitHub Project to real GitHub Issues for team visibility and tracking.

<context>
Purpose: Promoter — draft health findings in a GitHub Project become real GitHub Issues. Deletes the draft from the project, creates a real issue, then re-links the issue back into the project with the same custom field values.

All data comes from the GitHub Project (`[GHS] {owner}/{repo}`) — there are no local backlog files. Draft items (type `DraftIssue`) in the `Todo` column with `Source = Health Check` are the promotion targets.

### Shared References

| Reference | Path | Use For |
|-----------|------|---------|
| gh CLI patterns | `../shared/references/gh-cli-patterns.md` | Auth check, project operations, repo detection, issue CRUD, label creation, error codes |
| Projects format | `../shared/references/projects-format.md` | Project naming, item types, custom fields, Status values, field provisioning |
| Sync format | `../shared/references/sync-format.md` | Label taxonomy, issue title convention, body template, hidden metadata comment |
| State persistence | `../shared/references/state-persistence.md` | Session state stored as a real GitHub Issue (`[GHS State]`) on the target repo |
| Item categories | `../shared/references/item-categories.md` | Category A/B/CI classification for label assignment |
| Output conventions | `../shared/references/output-conventions.md` | Status indicators, table formats, summary block pattern |
| Edge cases | `../shared/references/edge-cases.md` | Rate limiting, permission errors, bounded retries |

The user must have **write access** to the target repository, Issues must be enabled, and the `project` scope must be authorized on the gh CLI token.
</context>

<anti-patterns>

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Read local `backlog/` files or use glob patterns to find markdown items | Query the GitHub Project via `gh project item-list` and filter with `jq` | The backlog is stored in the GitHub Project, not on disk |
| Create duplicate issues | Title-based dedup (`[Health] {Check Name}`) — always query existing `ghs:health-check` issues before creating | Duplicates confuse teams and break tracking |
| Close issues manually reopened by users | If a Done item's linked issue was reopened by a human, leave it open | Respect human overrides — they may have context the skill lacks |
| Promote Done items as new issues | Only Todo draft items become issues; Done items only trigger closing of previously-promoted issues | Creating issues for passing checks is noise |
| Leave the draft in the project after promoting | Delete the draft, then re-add the real issue URL via `item-add` | Duplicate entries (draft + real issue) confuse the board |
| Retry in a loop on rate limits | Report progress so far and tell the user to re-run later | Tight retry loops hit secondary rate limits |

</anti-patterns>

## Scope Boundary

This skill is a **Promoter**: draft project items become real GitHub Issues with project linking. It does not pull issue state back into the project beyond what `item-add` provides, change item statuses arbitrarily, or apply fixes. The only writes are: issue creation, draft deletion, issue re-linking, and custom field value copying.

<objective>
Promote draft health items to real GitHub Issues and re-link them in the project.

Inputs:
- `owner/repo` identifier (or detected from git remote)
- GitHub Project `[GHS] {owner}/{repo}` with draft items in the `Todo` column

Outputs:
- Real GitHub Issues created for Todo draft Health Check items
- Drafts replaced with linked real issues in the `[GHS] {owner}/{repo}` project
- Custom field values (Tier, Points, Slug, Category, Module, Detected) copied from draft to linked item
- Existing promoted issues updated or closed as appropriate
- Terminal report with promotion results

Next routing:
- Suggest `ghs-backlog-fix` to fix items — "To fix items: `/ghs-backlog-fix {owner}/{repo}`"
- Suggest `ghs-backlog-board` to see dashboard — "To see dashboard: `/ghs-backlog-board`"
</objective>

## Promotion Status Mapping

| Item Status | Has Linked Issue? | GitHub Issue State | Action |
|-------------|-------------------|-------------------|--------|
| Todo (draft) | No | — | **Promote**: create real issue, delete draft, re-add issue to project |
| Todo (draft) | Yes (already promoted) | Open | **Update** if metadata changed, else skip |
| Todo (draft) | Yes (already promoted) | Closed | **Reopen** with comment |
| Done | Yes | Open | **Close** with comment |
| Done | Yes | Closed | Skip (already resolved) |
| Done | No | — | Skip (nothing to promote) |

Draft items in Todo with `Source = Health Check` are the primary promotion targets. "Already promoted" means a real issue with a matching `[Health] {Check Name}` title already exists.

## Issue Template Fields

Issues created by this skill follow the body template in `../shared/references/sync-format.md`. All field values come from the draft item's custom fields in the GitHub Project:

| Field | Source | Example |
|-------|--------|---------|
| Hidden metadata comment | Draft item custom fields (Slug, Tier, Points, Category, Detected) | `<!-- ghs-sync:metadata slug:license tier:1 ... -->` |
| Tier | Draft item's `Tier` custom field | `1 — Required` |
| Points | Draft item's `Points` custom field | `4` |
| Category | Draft item's `Category` custom field | `B (file changes)` |
| Detected | Draft item's `Detected` custom field | `2026-01-15` |
| What's Missing | Draft item body content | Parsed from project draft body |
| Why It Matters | Draft item body content | Parsed from project draft body |
| How to Fix | Draft item body content | Parsed from project draft body |
| Acceptance Criteria | Draft item body content | Checklist parsed from project draft body |

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

## Why It Matters

Without a license, the repository is legally closed-source by default — contributors and consumers cannot determine their rights.

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

**BAD** — reads from local disk instead of project:
```bash
# WRONG: reading local backlog files
for f in backlog/{owner}_{repo}/health/*.md; do
  slug=$(grep "^slug:" "$f" | cut -d: -f2)
done
```

**GOOD** — queries the GitHub Project:
```bash
# CORRECT: query the project for draft items
ITEMS=$(gh project item-list $PROJECT_NUM --owner {owner} --format json --limit 500)
DRAFT_ITEMS=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .status == "Todo" and .type == "DraftIssue")]')
```

<process>

### Input

The user provides a repo identifier: `owner/repo` or `owner_repo`.

If not provided, detect from the current git remote (see `../shared/references/gh-cli-patterns.md` — Repo Detection).

### Phase 1 — Find Project & Discover Draft Items

**Rule:** Only Todo draft items with `Source = Health Check` are promotion candidates. Done items with a linked issue may trigger closing. Items in other states are always skipped.

**Trigger:** Project `[GHS] {owner}/{repo}` exists and contains draft items with `Source = Health Check` in the `Todo` column.

Pre-flight: verify the `project` scope is authorized:

```bash
gh auth status 2>&1 | grep -q "project" || {
  echo "[FAIL] Missing project scope. Run: gh auth refresh -s project"
  exit 1
}
```

Find the project and list items:

```bash
PROJECT_NUM=$(gh project list --owner {owner} --format json \
  --jq '.projects[] | select(.title == "[GHS] {owner}/{repo}") | .number')

if [ -z "$PROJECT_NUM" ]; then
  echo "No project found for {owner}/{repo}. Run /ghs-repo-scan first."
  exit 1
fi

ITEMS=$(gh project item-list $PROJECT_NUM --owner {owner} --format json --limit 500)

# Filter to promotion candidates: Source = Health Check, Status = Todo, type = DraftIssue
DRAFT_ITEMS=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .status == "Todo" and .type == "DraftIssue")]')

# Filter to close candidates: Source = Health Check, Status = Done, linked issue exists (not DraftIssue)
DONE_ITEMS=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .status == "Done" and .type != "DraftIssue")]')
```

Build two lists:

| List | Criteria | Purpose |
|------|----------|---------|
| Draft items | Source = Health Check, Status = Todo, type = DraftIssue | Candidates for issue creation |
| Done items | Source = Health Check, Status = Done, type = linked Issue | Candidates for issue closing |

If the project does not exist, abort: `No project found for {owner}/{repo}. Run /ghs-repo-scan first.`

If all draft items are already promoted (no DraftIssues in Todo), report: `All health items already promoted — nothing to sync.` Then handle any Done items that need closing.

### Phase 2 — Ensure Labels Exist

Pre-check: verify the target repo has issues enabled (see `../shared/references/gh-cli-patterns.md` — Issues enabled).

If issues are disabled, abort:
```
Issues are disabled on {owner}/{repo}. Enable them in Settings > General > Features > Issues, then re-run sync.
```

Create labels from the taxonomy in `../shared/references/sync-format.md` using idempotent commands (see `../shared/references/gh-cli-patterns.md` — Label Operations):

```bash
gh label create "ghs:health-check" --color "7057ff" --description "Health check finding from ghs-repo-scan" --repo {owner}/{repo} 2>&1 || true
gh label create "tier:1" --color "d73a4a" --description "Tier 1 — Required" --repo {owner}/{repo} 2>&1 || true
gh label create "tier:2" --color "fbca04" --description "Tier 2 — Recommended" --repo {owner}/{repo} 2>&1 || true
gh label create "tier:3" --color "0e8a16" --description "Tier 3 — Nice to Have" --repo {owner}/{repo} 2>&1 || true
gh label create "category:api-only" --color "c5def5" --description "Fix requires API calls only" --repo {owner}/{repo} 2>&1 || true
gh label create "category:file-change" --color "bfd4f2" --description "Fix requires file changes" --repo {owner}/{repo} 2>&1 || true
gh label create "category:ci" --color "d4c5f9" --description "Fix requires CI workflow changes" --repo {owner}/{repo} 2>&1 || true
```

### Phase 3 — Fetch Existing Promoted Issues

Query GitHub for all issues with the `ghs:health-check` label (see `../shared/references/gh-cli-patterns.md` — Issue Operations):

```bash
EXISTING_ISSUES=$(gh issue list \
  --label "ghs:health-check" \
  --state all \
  --json number,title,state,body \
  --limit 500 \
  --repo {owner}/{repo})
```

Build a lookup map using `jq`: `title -> {number, state, body}`.

This enables title-based dedup per the convention in `../shared/references/sync-format.md`. If `[Health] {Check Name}` already exists in any state, it is matched to the project draft rather than creating a duplicate.

```bash
# Example: look up whether a draft item already has a promoted issue
TITLE="[Health] LICENSE"
MATCH=$(echo "$EXISTING_ISSUES" | jq --arg t "$TITLE" '.[] | select(.title == $t)')
```

### Phase 4 — Promotion Loop

For each draft item in the promotion candidates list, apply the action from the **Promotion Status Mapping** table above.

#### Promoting a Draft Item (Creating a New Issue)

**Rule:** Only promote when no matching `[Health] {Check Name}` title exists in any state among real issues.

1. Extract field values from the draft item using `jq`:
   ```bash
   CHECK_NAME=$(echo "$DRAFT" | jq -r '.title | ltrimstr("[Health] ")')
   SLUG=$(echo "$DRAFT" | jq -r '.slug // ""')
   TIER_NUM=$(echo "$DRAFT" | jq -r '.tier // ""' | grep -o '[0-9]')
   POINTS=$(echo "$DRAFT" | jq -r '.points // ""')
   CATEGORY=$(echo "$DRAFT" | jq -r '.category // ""')
   DETECTED=$(echo "$DRAFT" | jq -r '.detected // ""')
   ITEM_BODY=$(echo "$DRAFT" | jq -r '.body // ""')
   DRAFT_NODE_ID=$(echo "$DRAFT" | jq -r '.id')
   ```
2. Build the issue body from the draft item's body content and custom fields, following the template in `../shared/references/sync-format.md`
3. Determine the `category:*` label from the item's `Category` custom field (see `../shared/references/item-categories.md`)
4. Create the real issue:
   ```bash
   ISSUE_URL=$(gh issue create \
     --title "[Health] {Check Name}" \
     --body "{body}" \
     --label "ghs:health-check,tier:{N},category:{cat}" \
     --repo {owner}/{repo} \
     --json url --jq '.url')
   ```
5. Delete the draft from the project:
   ```bash
   gh project item-delete $PROJECT_NUM --owner {owner} --id {draft_item_node_id}
   ```
6. Re-add the real issue to the project:
   ```bash
   NEW_ITEM=$(gh project item-add $PROJECT_NUM --owner {owner} --url $ISSUE_URL --format json)
   ```
7. Copy custom field values (Tier, Points, Slug, Category, Module, Detected) from the draft to the newly linked item using `gh project item-edit` with the 3-ID lookup pattern (see `../shared/references/gh-cli-patterns.md` — The 3-ID Lookup Pattern):
   ```bash
   # Get the new item node ID
   NEW_ITEM_ID=$(gh project item-list $PROJECT_NUM --owner {owner} --format json --limit 500 \
     | jq -r --arg url "$ISSUE_URL" '.items[] | select(.url == $url) | .id')

   # Set each custom field (use cached field/option IDs from project metadata)
   gh project item-edit --project-id {project_node_id} --id $NEW_ITEM_ID \
     --field-id {tier_field_id} --single-select-option-id {tier_option_id}
   gh project item-edit --project-id {project_node_id} --id $NEW_ITEM_ID \
     --field-id {points_field_id} --number {points_value}
   gh project item-edit --project-id {project_node_id} --id $NEW_ITEM_ID \
     --field-id {slug_field_id} --text "{slug_value}"
   gh project item-edit --project-id {project_node_id} --id $NEW_ITEM_ID \
     --field-id {category_field_id} --single-select-option-id {category_option_id}
   gh project item-edit --project-id {project_node_id} --id $NEW_ITEM_ID \
     --field-id {module_field_id} --single-select-option-id {module_option_id}
   gh project item-edit --project-id {project_node_id} --id $NEW_ITEM_ID \
     --field-id {detected_field_id} --date "{detected_date}"
   ```

#### Updating an Already-Promoted Issue (Open)

**Rule:** Only update if the hidden metadata comment shows tier, points, or category has changed. Never overwrite user edits to visible content unless metadata diverges.

1. Compare hidden `<!-- ghs-sync:metadata ... -->` in existing issue body with current project item data (extract via `jq`)
2. If changed: `gh issue edit {number} --body "{new_body}" --repo {owner}/{repo}`
3. If unchanged: skip

#### Reopening a Closed Promoted Issue

**Rule:** Only reopen if the project item is still in Todo. The issue was closed but the underlying problem persists.

```bash
gh issue reopen {number} --repo {owner}/{repo}
gh issue comment {number} --body "This check is still failing as of {date}. Reopening." --repo {owner}/{repo}
```

#### Closing a Resolved Issue

**Rule:** Only close issues where the project item's Status is Done. Never close issues that were manually reopened by users without a corresponding Done status.

```bash
gh issue close {number} --comment "Check now passes as of {date}. Closing." --repo {owner}/{repo}
```

### Phase 5 — Report

Display a summary table following `../shared/references/output-conventions.md`:

```
## Sync Report: {owner}/{repo}

| # | Item | Tier | Action | Issue |
|---|------|------|--------|-------|
| 1 | [Health] README | T1 | Promoted | #42 |
| 2 | [Health] LICENSE | T1 | Already promoted | #38 |
| 3 | [Health] Branch Protection | T1 | Updated | #39 |
| 4 | [Health] .editorconfig | T2 | Promoted | #43 |
| 5 | [Health] CI Workflow Health | T2 | Closed (resolved) | #35 |

---

Summary:
  Promoted: {n_promoted}
  Updated: {n_updated}
  Reopened: {n_reopened}
  Closed: {n_closed}
  Already promoted: {n_already}
  Skipped: {n_skipped}

To fix items: /ghs-backlog-fix {owner}/{repo}
To see dashboard: /ghs-backlog-board
```

</process>

## Edge Cases

- **Idempotent**: Title-based dedup prevents duplicate issues. Running sync multiple times is safe.
- **Issues disabled**: Pre-check in Phase 2 detects this and aborts with a clear message.
- **project scope missing**: Pre-flight in Phase 1 catches this. Instruct user: `gh auth refresh -s project`.
- **User-edited issue bodies**: The hidden `<!-- ghs-sync:metadata ... -->` comment is preserved. Visible content is not overwritten unless the metadata (tier, points, slug) has changed.
- **Rate limiting**: Follow `../shared/references/edge-cases.md` retry pattern. Do not loop — if rate-limited, report progress so far and suggest re-running later.
- **No project found**: If `[GHS] {owner}/{repo}` doesn't exist, suggest running `ghs-repo-scan` first.
- **No draft items**: Report "All health items already promoted — nothing to sync" and handle any Done items that need closing.
- **Large repos**: Process items sequentially to avoid rate limits. Do not parallelize API calls.
- **Draft deletion fails**: If `item-delete` returns an error, skip deletion and report the draft as "promotion partial" — the real issue was still created and linked.
- **Field copy failures**: If copying a custom field fails (e.g., option ID mismatch), log the failure per field and continue — the issue and link are the critical outputs.
- **Score record item**: The `[GHS Score]` draft item in the project has `Source` unset — it must be excluded from all promotion loops by filtering on `Source = Health Check` only.
- **State issue**: The `[GHS State]` issue on the target repo is a real GitHub Issue (not a project item) — never attempt to promote or close it via this skill.
