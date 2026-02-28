# ghs-backlog-sync

Promotes draft GitHub Project items to real GitHub Issues for team visibility and tracking.

## When to Use

Use this skill after running `ghs-repo-scan` to promote health findings from draft project items to full GitHub Issues. This makes your backlog visible to collaborators through GitHub's native issue tracker.

**Trigger phrases:** "sync backlog", "create issues from health checks", "push findings to GitHub", "publish backlog", "sync health items"

## What It Does

1. **Queries** FAIL health items from the GitHub Project via `gh project item-list`
2. **Creates labels** on the target repo (`ghs:health-check`, `tier:1/2/3`, `category:*`)
3. **Fetches** existing synced issues to avoid duplicates (title-based dedup)
4. **Creates/updates/closes** GitHub Issues matching project item status
5. **Updates project items** with the linked Issue URL via `gh project item-edit`
6. **Reports** a summary table of all sync actions

## Label Taxonomy

| Label | Color | Purpose |
|-------|-------|---------|
| `ghs:health-check` | Purple | Identifies all health check issues |
| `tier:1` | Red | Tier 1 — Required |
| `tier:2` | Yellow | Tier 2 — Recommended |
| `tier:3` | Green | Tier 3 — Nice to Have |
| `category:api-only` | Light blue | Category A fixes |
| `category:file-change` | Blue | Category B fixes |
| `category:ci` | Lavender | Category CI fixes |

## Issue Title Convention

All synced issues use the title format `[Health] {Check Name}`. This title is the dedup key — running sync multiple times will not create duplicates.

## Sync Actions

| Action | When |
|--------|------|
| **Created** | FAIL item with no matching GitHub Issue |
| **Updated** | Open issue exists but content has changed |
| **Reopened** | Closed issue but check still fails |
| **Closed** | PASS item with an open synced issue |
| **Already synced** | Open issue exists, content unchanged |

## Integration with backlog-fix

After syncing, `ghs-backlog-fix` automatically detects the linked Issue URL on project items:

- **Category B fixes**: PRs include `Fixes #{number}` for auto-close on merge
- **Category A fixes**: Issues are closed directly after applying the API change

## Example

```
You: sync backlog phmatray/my-project

## Sync Report: phmatray/my-project

| # | Item              | Tier | Action       | Issue |
|---|-------------------|------|--------------|-------|
| 1 | README            | T1   | Created      | #42   |
| 2 | LICENSE           | T1   | Created      | #43   |
| 3 | .editorconfig     | T2   | Created      | #44   |
| 4 | CI Workflow Health | T2   | Already synced | #35  |

Summary:
  Created: 3
  Already synced: 1
```

## Prerequisites

- `gh` CLI authenticated with write access to the target repo
- Issues must be enabled on the repository
- GitHub Project data must exist from a prior `ghs-repo-scan` run

## Requirements

| Tool | Required |
|------|----------|
| `gh` CLI | Yes (authenticated) |
| Network | Yes |

## Related Skills

- [ghs-repo-scan](/skills/ghs-repo-scan) --- produces the backlog items that sync publishes
- [ghs-backlog-fix](/skills/ghs-backlog-fix) --- fixes items and auto-closes synced issues
- [ghs-backlog-board](/skills/ghs-backlog-board) --- shows synced issue references in the dashboard
