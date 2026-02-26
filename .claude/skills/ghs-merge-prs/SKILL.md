---
name: ghs:merge-prs
description: >
  Merges pull requests on a GitHub repository — your own PRs, Renovate/bot PRs, or all eligible PRs at once.
  Use this skill whenever the user wants to merge PRs, asks to "merge my PRs", "merge renovate PRs",
  "merge all PRs", "merge PR #42", "clean up my pull requests", "merge and delete branches",
  "batch merge", "merge bot PRs", "merge dependency updates", or anything related to merging
  open pull requests. Also trigger for "merge all for {repo}", "squash merge renovate",
  "merge passing PRs", or just "merge" in the context of pull request work.
  Do NOT use for creating PRs (use ghs:backlog-fix), reviewing code, or scanning repos (use ghs:repo-scan).
metadata:
  author: phmatray
  version: 1.0.0
---

# Merge PRs

Merge open pull requests on a GitHub repository — individually, by author type, or all at once. Supports batch operations with CI status awareness and automatic branch cleanup.

## Prerequisites

- The `gh` CLI must be authenticated (`gh auth status`)
- The user must have write/merge access to the target repository

For prerequisites, error handling, and repo detection, read `../shared/gh-prerequisites.md`.

## Input

The user may provide:
- A specific PR number: "merge PR #42"
- A filter: "merge renovate PRs", "merge my PRs", "merge all PRs"
- A repo: "merge PRs on phmatray/Formidable" — if not provided, detect from `gh repo view`
- A URL: "merge PRs from https://github.com/owner/repo/pulls"

If no filter is given, default to showing all open PRs and letting the user choose.

## Merge Strategy

- **Renovate / bot PRs**: Squash merge (`--squash`) — keeps history clean since each PR is a single dependency bump
- **User's own PRs**: Regular merge (`--merge`) — preserves the full commit history from the feature branch
- The user can override the strategy if they ask for something specific

## Execution

### Step 1 — Detect Repository and List PRs

1. Detect the repository (`owner/repo`) from input or git remote
2. Fetch all open PRs with relevant metadata:

```bash
gh pr list --repo {owner}/{repo} --state open --json number,title,author,headRefName,statusCheckRollup,mergeable,reviewDecision,isDraft --limit 100
```

3. Classify each PR:
   - **Bot PRs**: author login contains `renovate`, `dependabot`, `copilot-swe-agent`, or `is_bot: true`
   - **Own PRs**: author login matches the authenticated user (`gh api user --jq '.login'`)
   - **Other**: any remaining PRs from external contributors

### Step 2 — Display PR Overview

Present a clear summary table:

```
## Open PRs: {owner}/{repo}

### Your PRs ({count})

| # | Title | Branch | CI | Mergeable |
|---|-------|--------|----|-----------|
| 31 | Add global.json for .NET SDK version pinning | fix/version-pinning | FAIL | Yes |
| 30 | Improve Renovate configuration | fix/dependency-update-config | FAIL | Unknown |

### Bot PRs ({count})

| # | Title | Branch | CI | Mergeable | Bot |
|---|-------|--------|----|-----------|-----|
| 33 | chore(deps): update opentelemetry-dotnet-contrib monorepo | renovate/opentelemetry... | FAIL | Unknown | renovate |

### Other PRs ({count})
(none)

---
CI Legend: PASS = all checks passed | FAIL = one or more checks failed | PENDING = checks still running | NONE = no checks configured
```

CI status is derived from `statusCheckRollup`:
- **PASS**: all checks have `conclusion: "SUCCESS"`
- **FAIL**: any check has `conclusion: "FAILURE"`
- **PENDING**: any check has `status: "IN_PROGRESS"` or `"QUEUED"`
- **NONE**: empty `statusCheckRollup` array

Mergeable status from the `mergeable` field: `MERGEABLE`, `CONFLICTING`, or `UNKNOWN`.

### Step 3 — Determine What to Merge

Based on the user's request:

| User says | Action |
|-----------|--------|
| "merge PR #42" | Merge that specific PR |
| "merge renovate PRs" / "merge bot PRs" | Merge all bot PRs |
| "merge my PRs" | Merge all user's own PRs |
| "merge all PRs" | Merge all PRs (own + bot + other) |
| "merge passing PRs" | Merge only PRs where CI = PASS |
| No specific filter | Show the overview, ask what to merge |

Skip PRs that are:
- **Draft**: always skip drafts
- **CONFLICTING**: cannot be merged — report and skip

### Step 4 — Confirm Before Merging

Always show what will be merged before doing it:

```
## Ready to merge {N} PRs:

| # | Title | Strategy | CI | Note |
|---|-------|----------|----|------|
| 31 | Add global.json... | merge | FAIL | CI failing — will force merge |
| 33 | chore(deps): update opentelemetry... | squash | FAIL | CI failing — will force merge |

Branches will be deleted after merge.

Proceed? (y/n)
```

**If any PRs have failing CI**, highlight this clearly:

```
WARNING: {N} PRs have failing CI checks. Merging will bypass status checks.
```

Wait for user confirmation before proceeding. This is the critical safety gate.

### Step 5 — Merge PRs Sequentially

For each confirmed PR, merge one at a time (sequential to avoid race conditions on the base branch):

```bash
# For bot PRs (squash merge)
gh pr merge {number} --repo {owner}/{repo} --squash --delete-branch

# For user's own PRs (regular merge)
gh pr merge {number} --repo {owner}/{repo} --merge --delete-branch

# If CI is failing, add --admin to bypass status checks (requires admin access)
gh pr merge {number} --repo {owner}/{repo} --squash --delete-branch --admin
```

If `--admin` fails (user is not admin), try without it — GitHub may still allow the merge if branch protection doesn't strictly require passing checks.

Report progress as each PR merges:

```
[1/3] Merging #31 (Add global.json...) ... merged
[2/3] Merging #33 (chore(deps): update opentelemetry...) ... merged
[3/3] Merging #32 (chore(deps): update opentelemetry...) ... FAILED: merge conflict
```

### Step 6 — Summary Report

After all merges complete:

```
## Merge Summary: {owner}/{repo}

Merged:  2 PRs
Failed:  1 PR
Skipped: 0 PRs

| # | Title | Status | Note |
|---|-------|--------|------|
| 31 | Add global.json... | Merged | branch deleted |
| 33 | chore(deps): update opentelemetry... | Merged | branch deleted |
| 32 | chore(deps): update opentelemetry... | Failed | merge conflict — resolve manually |

Remaining open PRs: {N}
```

## Edge Cases

- **No open PRs**: Tell the user there's nothing to merge.
- **All PRs are drafts**: Report that all PRs are drafts and suggest marking them ready first.
- **Merge conflicts**: Skip conflicting PRs, report them, and suggest resolving manually.
- **No admin access for failing CI**: If `--admin` fails and branch protection blocks the merge, report it clearly and suggest the user either fix CI or adjust branch protection rules.
- **PR requires review approval**: If `reviewDecision` is `CHANGES_REQUESTED` or review is required but not approved, flag it and skip unless user explicitly confirms.
- **Rate limiting**: If `gh` commands fail with rate limit errors, report and suggest waiting.
- **Cascading conflicts**: After merging one PR, others may develop conflicts. If a merge fails mid-batch, continue with remaining PRs and report all failures at the end.

## Examples

**Example 1: Merge a specific PR**
User says: "merge PR #31 on phmatray/Formidable"
Result: Shows PR details, confirms, merges with appropriate strategy, deletes branch.

**Example 2: Merge all Renovate PRs**
User says: "merge renovate PRs"
Result: Lists all Renovate bot PRs, confirms (warns about failing CI if applicable), squash-merges each, deletes branches.

**Example 3: Merge everything**
User says: "merge all PRs on phmatray/Formidable"
Result: Shows overview of all PRs, confirms the batch, merges sequentially (squash for bots, merge for own), reports results.

**Example 4: Merge only passing PRs**
User says: "merge passing PRs"
Result: Filters to only PRs with CI = PASS, confirms, merges them. If none are passing, reports that.
