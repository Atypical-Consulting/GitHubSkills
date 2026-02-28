---
name: ghs-review-pr
description: >
  Review a GitHub pull request by fetching the diff, analyzing code changes against the
  codebase, and posting a structured review comment with findings by severity. Use this
  skill whenever the user wants to review a PR, check code quality, or says things like
  "review PR #42", "review my PRs", "code review", "check PR #42", "review all open PRs",
  "review PRs by renovate", "what does PR #42 change", "is PR #42 safe to merge",
  "review draft PRs", or "review ready PRs".
  Do NOT use for merging PRs (use ghs-merge-prs), implementing issues (use ghs-issue-implement),
  or scanning repo health (use ghs-repo-scan).
allowed-tools: "Bash(gh:*) Bash(git:*) Read Glob Grep"
compatibility: "Requires gh CLI (authenticated), git, network access"
license: MIT
metadata:
  author: phmatray
  version: 1.0.0
routes-to:
  - ghs-merge-prs
routes-from:
  - ghs-issue-implement
  - ghs-backlog-fix
---

# Code Review for GitHub PRs

Fetch a GitHub PR diff and metadata, clone the repo for context, analyze code changes, and post a structured review comment with findings categorized by severity.

<context>
Purpose: Review GitHub pull requests by inspecting the actual diff against the codebase, producing actionable review comments that catch bugs, security issues, and quality problems before merge.

Roles:
1. **Reviewer** (you) — fetches the PR, clones the repo, analyzes the diff in context, produces the review, posts the comment

This skill does not spawn sub-agents — the review requires accumulated context from reading the diff and surrounding code that doesn't parallelize well.

Shared references:

| Reference | Purpose |
|-----------|---------|
| `../shared/references/gh-cli-patterns.md` | Authentication, repo detection, PR operations, error handling |
| `../shared/references/output-conventions.md` | Status indicators, table formats, routing suggestions |
| `../shared/references/implementation-workflow.md` | Repository clone/pull logic (§1) |
| `../shared/references/edge-cases.md` | Rate limiting, permission errors, bounded retries |
</context>

<anti-patterns>

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Merge or modify the PR during review | Route to `ghs-merge-prs` for merge operations | This skill is review-only — merging belongs in `ghs-merge-prs` |
| Review without reading the actual diff | Always fetch the diff with `gh pr diff` and read surrounding code | A review without reading code is just guessing |
| Post a review on a closed/merged PR | Warn the user and ask before proceeding | Closed PRs don't need reviews |
| Rubber-stamp with only praise | Always look for at least one actionable finding or explicitly state the code is clean | Empty praise reviews provide no value |
| Flag style nits as Critical | Use the severity table — style issues are Suggestions at most | Misclassified severity erodes trust in the review |
| Duplicate an existing review comment | Check for `## Code Review: PR #` in existing comments before posting | Avoids cluttering the PR with redundant reviews |
| Guess what code does without reading context files | Use Glob/Grep/Read to inspect imports, callers, and related files | Findings without context lead to false positives |
| Review huge diffs (500+ changed lines) without chunking | Break large diffs into logical sections (by file or module) and review each | Reviewing everything at once causes missed findings |

</anti-patterns>

## Scope Boundary

This skill **reviews only** — it never modifies code, creates branches, or merges PRs. The sole write actions are:

1. Posting a GitHub review comment on the PR (via `gh pr review`)
2. Optionally approving or requesting changes (via `gh pr review --approve` or `--request-changes`)

Everything else is read-only investigation.

<objective>
Produce a structured review comment on the GitHub PR with findings categorized by severity, and optionally submit an approval or change-request verdict.

Outputs:
- GitHub review comment posted on the PR with structured findings
- Terminal display of the same review
- Verdict: Approve / Request Changes / Comment Only

Next routing (see `output-conventions.md` § Routing Suggestions):
- Suggest `ghs-merge-prs` to merge — "To merge: `/ghs-merge-prs #{number}`"
- If the PR addresses an issue, suggest reviewing the linked issue
- For batch reviews, show a summary table
</objective>

<process>

## Input

- **Single PR**: `review PR #42` or `review #42`
- **Multiple PRs**: `review PRs #42, #43, #45` — processes each sequentially
- **All open PRs**: `review all open PRs` — fetches all open PRs for the repo
- **Filtered**: `review PRs by renovate`, `review draft PRs`, `review ready PRs`
- **With filters**: `--author {user}`, `--label {label}`, `--draft` / `--ready`

## Phase 1 — Parse Input and Detect Filters

Extract from user input:

| Parameter | Source | Default |
|-----------|--------|---------|
| PR number(s) | Explicit `#N` in input | None (required unless "all") |
| Repository | `gh repo view` auto-detect or explicit `owner/repo` | Auto-detect |
| Author filter | `--author {user}` or "by {user}" | None |
| Label filter | `--label {label}` | None |
| Draft filter | `--draft` or "draft PRs" | None |
| Ready filter | `--ready` or "ready PRs" | None |

### Rule/Trigger/Example Triples

| Rule | Trigger | Example |
|------|---------|---------|
| Single PR = direct fetch | User specifies `#N` | "review PR #42" → fetch PR #42 directly |
| "all open" = list + iterate | User says "all open PRs" | "review all open PRs" → `gh pr list --state open` then review each |
| Author keyword = filter | User says "by {user}" or "--author" | "review PRs by renovate" → `gh pr list --author renovate` |
| Draft keyword = filter | User says "draft PRs" | "review draft PRs" → `gh pr list --draft` |

## Phase 2 — Fetch PR Metadata

Retrieve the PR details (see `gh-cli-patterns.md` § PR Operations):

```bash
gh pr view {number} --repo {owner}/{repo} \
  --json number,title,body,author,headRefName,baseRefName,files,additions,deletions,commits,labels,reviewDecision,isDraft,state,comments,reviewRequests,mergeStateStatus
```

Extract:
- Title and body (the PR description)
- Author and branch names
- File change summary (additions, deletions, file count)
- Existing labels and review state
- Whether it's a draft
- Comments (may contain context or prior review feedback)

**Guard rails:**
- If the PR is **closed or merged**, warn the user and ask whether to proceed — do not review silently
- If the PR is a **draft**, note it but proceed (drafts benefit from early review)
- If an existing comment starts with `## Code Review: PR #`, ask whether to update or add a new one
- If the PR has 0 changed files, warn and skip

## Phase 3 — Fetch PR Diff

Retrieve the full diff:

```bash
gh pr diff {number} --repo {owner}/{repo}
```

For very large diffs (500+ lines), break the review into sections by file or module.

## Phase 4 — Prepare Repository

Follow `../shared/references/implementation-workflow.md` §1 — clone or pull the repo to `repos/{owner}_{repo}/`.

Checkout the base branch to understand the context around changed code.

## Phase 5 — Analyze Diff

For each changed file in the diff, perform the following analysis:

### Review Criteria Table

| Category | What to Check | Severity if Found |
|----------|--------------|-------------------|
| **Security** | SQL injection, XSS, command injection, hardcoded secrets, insecure deps, path traversal, SSRF, insecure deserialization | Critical |
| **Correctness** | Logic errors, off-by-one, null/undefined handling, race conditions, missing validation, type mismatches, incorrect error handling | Critical / Warning |
| **Performance** | N+1 queries, unbounded loops, memory leaks, missing pagination, unnecessary re-renders, blocking I/O on main thread | Warning |
| **Style** | Naming conventions, dead code, TODO comments, inconsistent patterns, overly complex expressions | Suggestion |
| **Tests** | Missing test coverage for new code, brittle assertions, untested edge cases, test-only code in production paths | Warning / Suggestion |
| **Docs** | Missing/outdated docs for public API changes, unclear comments, changelog entries | Suggestion |

### Analysis Process

1. **Read the diff** — understand what changed and why (from PR description)
2. **Read surrounding code** — use Read/Grep/Glob to inspect the unchanged context around each change
3. **Trace dependencies** — check imports, callers, and consumers of changed functions/types
4. **Check test coverage** — verify tests exist for new/changed logic
5. **Cross-reference PR description** — ensure the code matches what the PR claims to do

### Cognitive Bias Guards

| Bias | Antidote |
|------|----------|
| Anchoring | Don't let PR size dictate severity — small PRs can have critical bugs |
| Confirmation | Actively look for bugs even in well-written code |
| Availability | Check actual usage patterns, not just commonly-known issues |
| Familiarity | Don't assume known libraries are used correctly — verify |
| Halo effect | Review code quality independently of the author's reputation |
| Recency | Don't over-focus on the last file in the diff — review all files equally |

### Confidence Levels

Include a confidence indicator for findings:

| Confidence | Criteria |
|------------|----------|
| High | Verified by reading source code and tracing execution path |
| Medium | Likely issue based on patterns, but full impact not confirmed |
| Low | Possible concern that warrants author attention |

## Phase 6 — Produce Structured Review

Generate the review with these sections:

### Review Comment Structure

```markdown
## Code Review: PR #{number}

### Summary
{1-2 sentence summary of what the PR does and overall assessment}

### Findings

#### Critical (must fix)
- `file.ts:L42` — SQL injection via unsanitized input in query builder
- `auth.ts:L15` — Hardcoded API key exposed in source

#### Warnings (should fix)
- `api.ts:L15` — Missing error handling for network timeout
- `service.ts:L88` — Unbounded loop could cause performance issues

#### Suggestions (nice to have)
- `utils.ts:L8` — Could use `Array.from()` instead of spread for better readability
- `types.ts:L3` — Consider extracting shared type to reduce duplication

#### Praise
- Clean separation of concerns in the new service layer
- Good test coverage for edge cases

### Verdict: {Approve / Request Changes / Comment Only}
---
*Automated review by ghs-review-pr — human review recommended.*
```

### Verdict Decision Table

| Condition | Verdict |
|-----------|---------|
| Any Critical findings | Request Changes |
| Warnings only, no Critical | Comment Only (let author decide) |
| Suggestions and Praise only | Approve |
| No findings, code is clean | Approve |

### Good and Bad Review Examples

**Good review comment** (specific, actionable, severity-calibrated):

```markdown
## Code Review: PR #42

### Summary
Adds user authentication via JWT tokens. Implementation is solid but has one critical security issue and a few suggestions.

### Findings

#### Critical (must fix)
- `src/auth/jwt.ts:L23` — Token secret is hardcoded as `"mysecret"`. Use an environment variable (`process.env.JWT_SECRET`) with a minimum 256-bit key.

#### Warnings (should fix)
- `src/auth/middleware.ts:L45` — Token expiry check uses `<` instead of `<=`, allowing tokens to be used at the exact expiry timestamp.
- `src/auth/login.ts:L67` — Missing rate limiting on login endpoint. Consider adding `express-rate-limit`.

#### Suggestions (nice to have)
- `src/auth/types.ts:L12` — `UserPayload` interface duplicates fields from `User` — consider extending it.

#### Praise
- Clean middleware pattern with proper next() handling
- Comprehensive test suite covering token refresh edge cases

### Verdict: Request Changes
---
*Automated review by ghs-review-pr — human review recommended.*
```

**Bad review comment** (vague, unsupported, wrong severity):

```markdown
## Code Review: PR #42

### Summary
Looks okay but could be better.

### Findings

#### Critical (must fix)
- The variable names could be more descriptive
- Missing a comment on line 12

#### Praise
- Good job!

### Verdict: Approve
```

Problems: style nits classified as Critical, no file/line references, vague praise, approving despite "Critical" findings.

## Phase 7 — Post GitHub Review

Post the review on the PR using `gh pr review`:

```bash
# Comment only (no verdict)
gh pr review {number} --repo {owner}/{repo} --comment --body "$(cat <<'EOF'
## Code Review: PR #{number}

{review_content}

---
*Automated review by ghs-review-pr — human review recommended.*
EOF
)"

# Approve
gh pr review {number} --repo {owner}/{repo} --approve --body "$(cat <<'EOF'
## Code Review: PR #{number}

{review_content}

---
*Automated review by ghs-review-pr — human review recommended.*
EOF
)"

# Request changes
gh pr review {number} --repo {owner}/{repo} --request-changes --body "$(cat <<'EOF'
## Code Review: PR #{number}

{review_content}

---
*Automated review by ghs-review-pr — human review recommended.*
EOF
)"
```

## Phase 8 — Terminal Output

Show the same review in the terminal (see `output-conventions.md` § Table Patterns):

```
## Review: PR #{number} — {title}

Author: @{author} | Branch: {head} → {base}
Files: {file_count} | +{additions} / -{deletions}

### Findings

#### Critical (must fix)
- `file.ts:L42` — {description}

#### Warnings (should fix)
- `api.ts:L15` — {description}

#### Suggestions (nice to have)
- `utils.ts:L8` — {description}

#### Praise
- {description}

### Verdict: {verdict}

---
Review posted: https://github.com/{owner}/{repo}/pull/{number}#pullrequestreview-{id}

Summary:
  Findings:   {critical} critical, {warnings} warnings, {suggestions} suggestions
  Verdict:    {verdict}
```

</process>

## Batch Mode

When reviewing multiple PRs:

1. Process each PR sequentially — codebase context accumulates, making later reviews faster
2. After all reviews, show a summary table:

```
## Review Summary: {owner}/{repo}

| # | PR | Author | Files | Findings | Verdict | Review |
|---|-----|--------|-------|----------|---------|--------|
| #42 | Add auth | @user | 5 | 1C 2W 1S | Request Changes | Posted |
| #43 | Fix typo | @user | 1 | 0C 0W 1S | Approve | Posted |
| #45 | Update deps | @renovate | 2 | 0C 1W 0S | Comment Only | Posted |

Summary:
  Reviewed:  3 PRs
  Approved:  1
  Changes:   1
  Comments:  1
```

## Edge Cases

- **PR has no diff** (0 changed files): Warn and skip — nothing to review.
- **Very large diff (500+ lines)**: Break into sections by file. Note in the review that the diff is large and the review may not be exhaustive.
- **PR is a draft**: Proceed with review but note it's a draft. Drafts benefit from early feedback.
- **PR is already merged or closed**: Warn the user and ask whether to proceed.
- **PR has merge conflicts**: Note the conflicts but review the diff as-is. Suggest resolving conflicts first.
- **Binary files in diff**: Skip binary files. Note them in the review as "not reviewed (binary)".
- **PR references external URLs**: Note them but don't fetch external content.
- **PR already has a review comment from this tool**: Check for existing comments starting with `## Code Review: PR #`. If found, ask the user whether to update or add a new one.
- **Author is a bot (renovate, dependabot)**: Focus review on dependency version changes, changelog notes, and breaking changes rather than code style.
- **PR has failing CI checks**: Note the failing checks in the review. Suggest fixing CI before merge.
- **No write access to repo**: Post review as a comment instead of a formal review if `gh pr review` fails with 403.

## Examples

**Example 1: Review a single PR**
User says: "review PR #42"
Result: Fetches PR, clones/pulls repo, analyzes diff, posts structured review, shows review in terminal.

**Example 2: Review all open PRs**
User says: "review all open PRs"
Result: Fetches open PRs, reviews each sequentially, posts reviews, shows batch summary.

**Example 3: Review PRs by a specific author**
User says: "review PRs by renovate"
Result: Fetches PRs authored by renovate, reviews each, focuses on dependency changes, shows batch summary.

**Example 4: Quick safety check**
User says: "is PR #42 safe to merge?"
Result: Same as review — produces full review with verdict indicating whether it's safe to merge.
