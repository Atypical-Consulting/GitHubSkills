# ghs-review-pr

Review a GitHub pull request — fetch the diff, analyze code changes against the codebase, and post a structured review comment with findings by severity.

::: info Skill Info
**Version:** 1.0.0
**Arguments:** `[owner/repo] [--pr <number>] [--all] [--author <name>]`
**Trigger phrases:** "review PR #42", "review my PRs", "code review", "check PR #42", "review all open PRs", "review PRs by renovate", "is PR #42 safe to merge", "review draft PRs", "review ready PRs"
:::

## What It Does

`ghs-review-pr` fetches a PR diff and metadata, clones the repo for context, analyzes code changes across 6 review categories, and posts a structured review comment on the PR with a verdict.

### Review Categories

| Category | What to Check | Severity if Found |
|----------|--------------|-------------------|
| **Security** | SQL injection, XSS, hardcoded secrets, path traversal, SSRF | Critical |
| **Correctness** | Logic errors, null handling, race conditions, missing validation | Critical / Warning |
| **Performance** | N+1 queries, unbounded loops, memory leaks, missing pagination | Warning |
| **Style** | Naming conventions, dead code, inconsistent patterns | Suggestion |
| **Tests** | Missing coverage, brittle assertions, untested edge cases | Warning / Suggestion |
| **Docs** | Missing/outdated docs for API changes, unclear comments | Suggestion |

### Scope Boundary

**Review-only** — this skill never modifies code, creates branches, or merges PRs. The sole write actions are:

1. Posting a GitHub review comment on the PR (via `gh pr review`)
2. Optionally approving or requesting changes

### Process

1. **Parse input** — Extract PR number(s), repo, author/label/draft filters
2. **Fetch metadata** — PR title, body, author, branches, files, existing reviews
3. **Fetch diff** — Full diff via `gh pr diff`
4. **Prepare repo** — Clone/pull for surrounding code context
5. **Analyze** — Review each changed file against the 6 categories
6. **Generate review** — Structured comment with findings by severity
7. **Post review** — Comment, approve, or request changes based on verdict
8. **Display** — Show the same review in the terminal

### Verdict Decision

| Condition | Verdict |
|-----------|---------|
| Any Critical findings | Request Changes |
| Warnings only, no Critical | Comment Only |
| Suggestions and Praise only | Approve |
| No findings, code is clean | Approve |

### Input Modes

- **Single PR**: `review PR #42`
- **Multiple PRs**: `review PRs #42, #43, #45` — processes each sequentially
- **All open PRs**: `review all open PRs`
- **Filtered**: `review PRs by renovate`, `review draft PRs`, `review ready PRs`

## Example

```
## Review: PR #42 — Add user authentication

Author: @alice | Branch: feat/auth → main
Files: 5 | +230 / -12

### Findings

#### Critical (must fix)
- `src/auth/jwt.ts:L23` — Token secret is hardcoded as "mysecret".
  Use an environment variable with a minimum 256-bit key.

#### Warnings (should fix)
- `src/auth/middleware.ts:L45` — Token expiry check uses `<` instead
  of `<=`, allowing use at exact expiry timestamp.
- `src/auth/login.ts:L67` — Missing rate limiting on login endpoint.

#### Suggestions (nice to have)
- `src/auth/types.ts:L12` — `UserPayload` duplicates fields from
  `User` — consider extending it.

#### Praise
- Clean middleware pattern with proper next() handling
- Comprehensive test suite covering token refresh edge cases

### Verdict: Request Changes

---
Review posted: https://github.com/owner/repo/pull/42#pullrequestreview-123
```

### Batch Mode

When reviewing multiple PRs, a summary table is shown after all reviews:

```
## Review Summary: owner/repo

| # | PR | Author | Files | Findings | Verdict |
|---|-----|--------|-------|----------|---------|
| #42 | Add auth | @alice | 5 | 1C 2W 1S | Request Changes |
| #43 | Fix typo | @bob | 1 | 0C 0W 1S | Approve |
| #45 | Update deps | @renovate | 2 | 0C 1W 0S | Comment Only |

Summary: 3 PRs reviewed, 1 approved, 1 changes requested, 1 comment
```

## Routes To

After reviewing, GHS suggests:

- **[ghs-merge-prs](/skills/ghs-merge-prs)** — to merge approved PRs

## Routes From

- **[ghs-issue-implement](/skills/ghs-issue-implement)** — review PRs created by implementation
- **[ghs-backlog-fix](/skills/ghs-backlog-fix)** — review PRs created by fix agents

## Technical Details

| Property | Value |
|----------|-------|
| Allowed tools | `Bash(gh:*)`, `Bash(git:*)`, `Read`, `Glob`, `Grep` |
| Spawns sub-agents | No — review requires accumulated context |
| Phases | 8 (Parse, Fetch metadata, Fetch diff, Prepare, Analyze, Generate, Post, Display) |
| Bias guards | Anchoring, Confirmation, Availability, Familiarity, Halo effect, Recency |
| Requires | `gh` CLI (authenticated), `git`, network access |
