# ghs-merge-prs

Merges open pull requests with CI-aware confirmation, batch support, and automatic branch cleanup.

::: info Skill Info
**Version:** 2.0.0
**Trigger phrases:** "merge my PRs", "merge the Renovate PRs", "merge all PRs", "merge PR #42", "batch merge", "merge bot PRs", "merge passing PRs"
:::

## What It Does

`ghs-merge-prs` lists open PRs, classifies them by author type, lets you choose which to merge, and processes them sequentially with automatic branch deletion.

### Merge Strategy

The merge method is chosen based on the PR author:

| PR Author | Strategy | Rationale |
|-----------|----------|-----------|
| Renovate / Dependabot / bot | Squash merge | Single dependency bump -- squashing keeps history clean |
| Your own PRs | Regular merge | Preserves full commit history from the feature branch |
| External contributors | Regular merge | Preserves attribution and commit history |
| User override | As requested | You explicitly ask for a specific strategy |

### Filter Options

| You say | What gets merged |
|---------|-----------------|
| "merge PR #42" | That specific PR |
| "merge renovate PRs" | All bot PRs |
| "merge my PRs" | All your own PRs |
| "merge all PRs" | Everything eligible |
| "merge passing PRs" | Only PRs where CI passes |

Draft PRs and conflicting PRs are always skipped.

### Process

1. Detect repository and fetch all open PRs with metadata
2. Classify PRs by author (bot, own, other)
3. Display PR overview table with CI status
4. Determine what to merge based on your request
5. Show confirmation with merge strategies and CI warnings
6. Merge PRs sequentially (to avoid race conditions)
7. Display summary report

## Example

```
## Open PRs: phmatray/my-project

### Your PRs (2)

| # | Title                        | Branch             | CI   | Mergeable |
|---|------------------------------|--------------------|------|-----------|
| 12| Add LICENSE file              | fix/license        | PASS | Yes       |
| 13| Add .editorconfig             | fix/editorconfig   | PASS | Yes       |

### Bot PRs (1)

| # | Title                        | Branch              | CI   | Mergeable | Bot       |
|---|------------------------------|----------------------|------|-----------|-----------|
| 14| chore(deps): update lodash   | renovate/lodash-4.x | PASS | Yes       | renovate  |

---

## Ready to merge 3 PRs:

| # | Title                        | Strategy | CI   |
|---|------------------------------|----------|------|
| 12| Add LICENSE file              | merge    | PASS |
| 13| Add .editorconfig             | merge    | PASS |
| 14| chore(deps): update lodash   | squash   | PASS |

Branches will be deleted after merge.

Proceed? (y/n)
```

After merging:

```
## Merge Summary: phmatray/my-project

Merged:  3 PRs
Failed:  0 PRs
Skipped: 0 PRs

| # | Title                        | Status | Note            |
|---|------------------------------|--------|-----------------|
| 12| Add LICENSE file              | Merged | branch deleted  |
| 13| Add .editorconfig             | Merged | branch deleted  |
| 14| chore(deps): update lodash   | Merged | branch deleted  |

Remaining open PRs: 0
```

## Routes To

After merging, GHS suggests:

- **[ghs-repo-scan](/skills/ghs-repo-scan)** — to re-scan and verify the improvements
- **[ghs-backlog-board](/skills/ghs-backlog-board)** — to see the updated dashboard

## Technical Details

| Property | Value |
|----------|-------|
| Allowed tools | `Bash(gh:*)`, `Read` |
| Spawns sub-agents | No — PRs are merged sequentially to avoid race conditions |
| Phases | 6 (Detect Repo & List PRs, Display Overview, Determine What to Merge, Confirm, Merge Sequentially, Summary Report) |
| Requires | `gh` CLI (authenticated), network access |
| Re-run safe | Yes — already-merged PRs won't appear in the list |
