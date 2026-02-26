---
name: ghs-merge-prs
description: >
  Merges pull requests on a GitHub repository — your own PRs, Renovate/bot PRs, or all eligible PRs at once.
  Use this skill whenever the user wants to merge PRs, asks to "merge my PRs", "merge renovate PRs",
  "merge all PRs", "merge PR #42", "clean up my pull requests", "merge and delete branches",
  "batch merge", "merge bot PRs", "merge dependency updates", or anything related to merging
  open pull requests. Also trigger for "merge all for {repo}", "squash merge renovate",
  "merge passing PRs", or just "merge" in the context of pull request work.
  Do NOT use for creating PRs (use ghs-backlog-fix), reviewing code, or scanning repos (use ghs-repo-scan).
allowed-tools: "Bash(gh:*) Read"
compatibility: "Requires gh CLI (authenticated), network access"
license: MIT
metadata:
  author: phmatray
  version: 3.0.0
routes-to:
  - ghs-repo-scan
  - ghs-backlog-board
routes-from:
  - ghs-backlog-fix
  - ghs-issue-implement
---

# Merge PRs

Merge open pull requests on a GitHub repository — individually, by author type, or all at once. Supports batch operations with CI status awareness and automatic branch cleanup.

<context>
Purpose: Batch-merge open PRs with CI awareness, merge strategy selection, and automatic branch cleanup.

Roles:
1. **Merge Operator** (you) — lists PRs, classifies by author, confirms with user, merges sequentially, reports results

No sub-agents — PRs are merged sequentially to avoid race conditions on the base branch.

Shared references:
- `../shared/references/gh-cli-patterns.md` — authentication, repo detection, PR operations, error handling
- `../shared/references/output-conventions.md` — status indicators, table patterns, summary blocks
</context>

<anti-patterns>
NEVER do any of the following:

- **Merge PRs with failing CI without explicit user acknowledgment** — always highlight CI failures and get confirmation before bypassing checks
- **Merge without user confirmation on non-bot PRs** — bot PRs can be confirmed as a batch, but human-authored PRs need individual or explicit batch consent
- **Delete protected branches** — only delete head branches after merge using `--delete-branch`; never attempt to delete the default or base branch
- **Force-merge draft PRs** — drafts are not ready for review; always skip them and report their status
- **Retry in a loop on rate limits** — report the rate limit to the user and stop (see gh-cli-patterns.md error handling)
- **Merge PRs in parallel** — always merge sequentially to avoid race conditions on the base branch
</anti-patterns>

<objective>
Merge open PRs with appropriate strategy and clean up branches.

Outputs:
- PRs merged on GitHub
- Branches deleted after merge
- Terminal summary report (see output-conventions.md — merge-prs summary block)

Next routing:
- Suggest `ghs-repo-scan` to re-scan after merging — "To verify improvements: `/ghs-repo-scan {owner}/{repo}`"
- Suggest `ghs-backlog-board` to see updated dashboard
- If merge conflicts exist, suggest resolving manually or closing stale PRs
</objective>

<rules>

## Rule 1 — Merge Strategy Selection

Select the merge strategy based on PR author type. The user can always override.

| PR Author | Strategy | Flag | Rationale |
|-----------|----------|------|-----------|
| Renovate / Dependabot / bot | Squash merge | `--squash` | Single dependency bump — squashing keeps history clean |
| User's own PRs | Regular merge | `--merge` | Preserves full commit history from the feature branch |
| External contributors | Regular merge | `--merge` | Preserves attribution and commit history |
| User override | As requested | varies | User explicitly asks for a specific strategy |

**Trigger:** "squash merge renovate", "rebase merge #42", "merge my PRs with squash"
**Example:** User says "squash merge renovate PRs" → use `--squash` for all Renovate PRs, confirm batch, merge sequentially.

---

## Rule 2 — PR Categorization

Classify PRs into three categories for display and confirmation.

| Category | Detection | Confirmation |
|----------|-----------|-------------|
| **Bot PRs** | author login contains `renovate`, `dependabot`, `copilot-swe-agent`, or `is_bot: true` | Batch confirmation OK |
| **Own PRs** | author login matches `gh api user --jq '.login'` | Batch confirmation OK with summary |
| **Other PRs** | Any remaining external contributors | Explicit confirmation per PR or explicit batch consent |

**Trigger:** "merge my PRs", "merge bot PRs", "merge all PRs"
**Example:** User says "merge all PRs" → display all three categories, confirm each category, merge sequentially.

---

## Rule 3 — CI Check Requirements

CI status determines merge eligibility and warning level.

| CI Status | Derived From | Merge Eligible | Action |
|-----------|-------------|----------------|--------|
| **PASS** | All checks `conclusion: "SUCCESS"` | Yes | Merge normally |
| **FAIL** | Any check `conclusion: "FAILURE"` | Yes, with warning | Warn user, require explicit confirmation, use `--admin` if needed |
| **PENDING** | Any check `status: "IN_PROGRESS"` or `"QUEUED"` | Defer | Suggest waiting for checks to complete |
| **NONE** | Empty `statusCheckRollup` array | Yes | Merge normally (no checks configured) |

**Trigger:** "merge passing PRs", "merge even if CI fails"
**Example:** User says "merge passing PRs" → filter to CI=PASS only, skip FAIL/PENDING, merge eligible PRs.

---

## Rule 4 — Skip Conditions

Always skip these PRs automatically — report them but do not attempt to merge.

| Condition | Field | Action |
|-----------|-------|--------|
| Draft PR | `isDraft: true` | Skip — drafts are not ready |
| Merge conflict | `mergeable: "CONFLICTING"` | Skip — cannot merge, suggest manual resolution |
| Changes requested | `reviewDecision: "CHANGES_REQUESTED"` | Skip unless user explicitly confirms |

</rules>

<process>

## Input

The user may provide:
- A specific PR number: "merge PR #42"
- A filter: "merge renovate PRs", "merge my PRs", "merge all PRs"
- A repo: "merge PRs on phmatray/Formidable" — if not provided, detect from `gh repo view` (see gh-cli-patterns.md)
- A URL: "merge PRs from https://github.com/owner/repo/pulls"

If no filter is given, default to showing all open PRs and letting the user choose.

## Phase 1 — Detect Repository and List PRs

1. Detect the repository (`owner/repo`) from input or git remote (see gh-cli-patterns.md — Repo Detection)
2. Fetch all open PRs with relevant metadata:

```bash
gh pr list --repo {owner}/{repo} --state open --json number,title,author,headRefName,statusCheckRollup,mergeable,reviewDecision,isDraft --limit 100
```

3. Classify each PR per Rule 2 (PR Categorization)

## Phase 2 — Display PR Overview

Present a summary table per category (see output-conventions.md — Table Patterns):

```
## Open PRs: {owner}/{repo}

### Your PRs ({count})

| # | Title | Branch | CI | Mergeable |
|---|-------|--------|----|-----------|
| 31 | Add global.json for .NET SDK version pinning | fix/version-pinning | FAIL | Yes |

### Bot PRs ({count})

| # | Title | Branch | CI | Mergeable | Bot |
|---|-------|--------|----|-----------|-----|
| 33 | chore(deps): update opentelemetry... | renovate/opentelemetry... | FAIL | Unknown | renovate |

### Other PRs ({count})
(none)

---
CI Legend: PASS = all checks passed | FAIL = one or more checks failed | PENDING = checks still running | NONE = no checks configured
```

## Phase 3 — Determine What to Merge

Apply user intent to the classified PRs:

| User says | Action |
|-----------|--------|
| "merge PR #42" | Merge that specific PR |
| "merge renovate PRs" / "merge bot PRs" | Merge all bot PRs |
| "merge my PRs" | Merge all user's own PRs |
| "merge all PRs" | Merge all PRs (own + bot + other) |
| "merge passing PRs" | Merge only PRs where CI = PASS |
| No specific filter | Show the overview, ask what to merge |

Apply Rule 4 skip conditions to filter out ineligible PRs.

## Phase 4 — Confirm Before Merging

Always show what will be merged before doing it.

<examples>

### GOOD — Clear confirmation with warnings

```
## Ready to merge 3 PRs:

| # | Title | Strategy | CI | Note |
|---|-------|----------|----|------|
| 33 | chore(deps): update opentelemetry... | squash | PASS | — |
| 34 | chore(deps): update xunit | squash | PASS | — |
| 31 | Add global.json... | merge | FAIL | CI failing — will bypass checks |

⚠ WARNING: 1 PR has failing CI checks. Merging will bypass status checks.

Branches will be deleted after merge.

Proceed? (y/n)
```

### BAD — Vague confirmation without details

```
Merge 3 PRs? (y/n)
```

### BAD — No CI warning

```
## Ready to merge 3 PRs:

| # | Title | Strategy |
|---|-------|----------|
| 33 | chore(deps): update opentelemetry... | squash |
| 31 | Add global.json... | merge |

Proceed?
```

</examples>

Wait for user confirmation. This is the critical safety gate.

## Phase 5 — Merge PRs Sequentially

Merge one at a time — sequential prevents race conditions when multiple PRs touch the same base branch.

```bash
# For bot PRs (squash merge) — see gh-cli-patterns.md PR Operations
gh pr merge {number} --repo {owner}/{repo} --squash --delete-branch

# For user's own PRs (regular merge)
gh pr merge {number} --repo {owner}/{repo} --merge --delete-branch

# If CI is failing and user confirmed, add --admin to bypass status checks
gh pr merge {number} --repo {owner}/{repo} --squash --delete-branch --admin
```

If `--admin` fails (user is not admin), try without it — GitHub may still allow the merge if branch protection doesn't strictly require passing checks.

Report progress as each PR merges:

```
[1/3] Merging #33 (chore(deps): update opentelemetry...) ... merged
[2/3] Merging #34 (chore(deps): update xunit) ... merged
[3/3] Merging #31 (Add global.json...) ... FAILED: merge conflict
```

## Phase 6 — Summary Report

Follow output-conventions.md summary block pattern:

```
## Merge Summary: {owner}/{repo}

Merged:  2 PRs
Failed:  1 PR
Skipped: 0 PRs

| # | Title | Status | Note |
|---|-------|--------|------|
| 33 | chore(deps): update opentelemetry... | Merged | branch deleted |
| 34 | chore(deps): update xunit | Merged | branch deleted |
| 31 | Add global.json... | Failed | merge conflict — resolve manually |

Remaining open PRs: {N}
```

</process>

## Edge Cases

- **No open PRs**: Tell the user there's nothing to merge.
- **All PRs are drafts**: Report that all PRs are drafts and suggest marking them ready first.
- **Merge conflicts**: Skip conflicting PRs, report them, and suggest resolving manually.
- **No admin access for failing CI**: If `--admin` fails and branch protection blocks the merge, report it and suggest fixing CI or adjusting branch protection.
- **PR requires review approval**: If `reviewDecision` is `CHANGES_REQUESTED` or review is required but not approved, flag it and skip unless user explicitly confirms.
- **Rate limiting**: If `gh` commands fail with rate limit errors, report and suggest waiting (see gh-cli-patterns.md — Error Handling Conventions).
- **Cascading conflicts**: After merging one PR, others may develop conflicts. Continue with remaining PRs and report all failures at the end.
