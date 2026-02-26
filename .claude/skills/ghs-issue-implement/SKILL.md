---
name: ghs-issue-implement
description: >
  Implement a GitHub issue using worktree-based agents, then create a PR. Clones the repo, creates
  a worktree, spawns an agent to implement the fix/feature, verifies the result, and opens a PR
  with auto-close references. Use this skill whenever the user wants to implement an issue, fix
  a bug from an issue, build a feature from an issue, or says things like "implement issue #42",
  "fix issue #42", "implement #42", "build feature from issue #15", "implement all triaged issues",
  "implement all bugs", "work on issue #42", or "code issue #42".
  Do NOT use for triaging/labeling issues (use ghs-issue-triage), analyzing issues
  (use ghs-issue-analyze), applying backlog health items (use ghs-backlog-fix), or scanning
  repos (use ghs-repo-scan).
allowed-tools: "Bash(gh:*) Bash(git:*) Read Write Edit Glob Grep Task"
compatibility: "Requires gh CLI (authenticated), git, network access"
license: MIT
metadata:
  author: phmatray
  version: 4.0.0
routes-to:
  - ghs-merge-prs
routes-from:
  - ghs-issue-triage
  - ghs-issue-analyze
  - ghs-backlog-board
---

# Issue Implementation

Implement GitHub issues using parallel worktree-based agents. Creates branches, spawns agents to write code, verifies results, and opens PRs with auto-close references.

<context>
Purpose: Implement GitHub issues using parallel worktree-based agents — creates branches, spawns agents to write code, verifies results, and opens PRs with auto-close references.

### Shared References

| Reference | Path | Use For |
|-----------|------|---------|
| Agent spawning | `../shared/references/agent-spawning.md` | Worktree creation, agent spawning, context budgeting, result contract, bounded retries, cleanup |
| gh CLI patterns | `../shared/references/gh-cli-patterns.md` | Authentication, repo detection, error handling |
| Output conventions | `../shared/references/output-conventions.md` | Status indicators, table formats, summary blocks |
| Edge cases | `../shared/references/edge-cases.md` | Rate limiting, content filters, permission errors, bounded retries |

The user must have **write access** to the target repository.
</context>

<anti-patterns>

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Implement without reading full issue + comments | Fetch issue with `--json body,comments` and read everything before planning | Misses acceptance criteria, duplicate context, or design decisions discussed in thread |
| Modify files outside issue scope | Only touch files directly required by the issue — log new discoveries as separate issues | Causes merge conflicts with other agents, introduces unreviewed changes |
| Skip verification before creating PR | Run tests, lint, and type-check before pushing | Broken PRs waste reviewer time and erode trust in automation |
| Create PR for incomplete work | Set `NEEDS_HUMAN` status instead — partial worktree is more useful than a broken PR | Incomplete PRs block the merge queue and confuse reviewers |
| Pass entire scan/backlog to subagent | Pass only: issue details, repo structure, acceptance criteria, tech stack | Bloats agent context, causes confusion and hallucination |

</anti-patterns>

## Scope Boundary

Only implement what the issue describes. If the agent discovers adjacent problems (outdated deps, missing tests for unrelated code, style inconsistencies), it must **not** fix them inline. Instead, note them in the PR body under a "Discovered Issues" section so they can be filed separately.

## Circuit Breaker

| Attempt | Action |
|---------|--------|
| 1st failure | Re-run agent with error context appended to prompt |
| 2nd failure | Re-run with error + stricter constraints (smaller scope, explicit file list) |
| 3rd failure | Mark `NEEDS_HUMAN`, preserve worktree, report failure details |

After 3 failures on the same issue, stop retrying. The worktree is left in place for manual continuation. See `../shared/references/agent-spawning.md` § Bounded Retries.

## Context Budget

What to pass to each implementation agent:

| Pass | Do Not Pass |
|------|-------------|
| `{owner}`, `{repo}`, `{default_branch}` | Other issues in the batch |
| Issue number, title, body, comments | Full scan/backlog results |
| Analysis comment (if present from ghs-issue-analyze) | Other agents' output or status |
| Tech stack detection results | Repository-wide metrics |
| Worktree path and branch name | Unrelated backlog items |
| Acceptance criteria extracted from issue | Previous session history |

<objective>
Implement GitHub issues and create PRs with auto-close references.

Outputs:
- PRs created on GitHub for each implemented issue
- Labels updated on implemented issues (`status:in-progress`)
- Terminal report with implementation results
- NEEDS_HUMAN items listed with failure details

Next routing:
- Suggest `ghs-merge-prs` to merge the created PRs — "To merge: `/ghs-merge-prs {owner}/{repo}`"
</objective>

## Input

Three invocation modes — the trigger phrase determines which:

| Trigger | Mode | What It Fetches |
|---------|------|-----------------|
| `implement issue #42`, `fix #42`, `code issue #42` | Single issue | One issue by number |
| `implement all triaged issues` | Batch by label | Issues with `status:triaged` |
| `implement all bugs` | Batch by type | Issues with `type:bug` |

### Rule/Trigger/Example Triples

**Rule:** A single issue number resolves to single-issue mode.
**Trigger:** User says "implement #42" or "fix issue #42".
**Example:** Fetch issue #42, show single-issue plan, create one worktree, spawn one agent.

**Rule:** "all" + a label keyword resolves to batch mode.
**Trigger:** User says "implement all triaged issues" or "implement all bugs".
**Example:** Fetch all open issues matching the label, show batch plan sorted by priority, spawn N agents in parallel.

**Rule:** A closed issue is skipped unless explicitly requested.
**Trigger:** User says "implement #42" but #42 is closed.
**Example:** Warn the user and skip. If user insists, proceed with a note.

## Branch Naming

Branch prefix is determined by the issue's type label:

| Type Label | Branch Prefix | Example |
|-----------|---------------|---------|
| `type:bug` | `fix/` | `fix/42-login-crash` |
| `type:feature` | `feat/` | `feat/15-dark-mode` |
| `type:docs` | `docs/` | `docs/18-update-readme` |
| `type:hotfix` | `fix/` | `fix/99-security-vuln` |
| (no type label) | `impl/` | `impl/50-misc-task` |

Pattern: `{prefix}/{issue-number}-{short-slug}`
Where `{short-slug}` = issue title, lowercased, non-alphanumeric replaced with `-`, truncated to 40 chars.

<process>

### Phase 1 — Fetch Issues

**Single issue mode:**

```bash
gh issue view {number} --repo {owner}/{repo} \
  --json number,title,body,labels,comments,assignees,state
```

Skip if closed (unless user explicitly requests).

**Batch mode:**

```bash
gh issue list --repo {owner}/{repo} --state open --label "{filter_label}" \
  --json number,title,body,labels,comments --limit 50
```

For each issue, extract: number, title, body, type label (for branch prefix), priority label (for ordering — critical first), comments (check for analysis from `ghs-issue-analyze`).

**Analysis context:** If an issue has a comment starting with `## Issue Analysis` (from `ghs-issue-analyze`), extract and pass it to the agent. This provides affected files, suggested approach, and complexity assessment.

### Phase 2 — Prepare Repository

Per `../shared/references/agent-spawning.md` § Repository Cloning:

1. Clone or pull the repo to `repos/{owner}_{repo}/`
2. Detect default branch
3. Detect tech stack (language, framework, test runner, linter)

### Phase 3 — Show Plan & Confirm

**Batch plan:**

```
## Implementation Plan: {owner}/{repo}

| # | Issue | Type | Priority | Branch | Has Analysis? |
|---|-------|------|----------|--------|---------------|
| 1 | #42 Login crashes | bug | high | fix/42-login-crash | Yes |
| 2 | #15 Add dark mode | feature | medium | feat/15-dark-mode | No |

Total: {N} issues ({n_bug} bugs, {n_feature} features, {n_docs} docs)

Proceed with all? (y/n/select)
```

**Single issue plan:**

```
## Plan: #{number} — {title}

Repository: {owner}/{repo}
Type:       {type_label}
Priority:   {priority_label}
Branch:     {prefix}/{number}-{slug} (from {default_branch})
Analysis:   {Yes — see comment | No — will analyze during implementation}

### What I'll do:
{Numbered list of implementation steps}

### Files to create/modify:
{List of files from analysis, or "Will determine during implementation"}

Proceed? (y/n)
```

Wait for user confirmation before continuing.

**Pre-flight checks** (per `../shared/references/agent-spawning.md` § Pre-flight Checks):

| Check | Command | If Conflict |
|-------|---------|-------------|
| Existing remote branch | `git ls-remote --heads origin 'refs/heads/{prefix}/*'` | Flag in plan, use `-B` if user confirms |
| Existing PR for branch | `gh pr list --head {prefix}/{slug} --json number,url` | Report existing PR, skip |

### Phase 4 — Create Worktrees

Per `../shared/references/agent-spawning.md` § Worktree Creation:

```
repos/{owner}_{repo}/                                  <- main clone
repos/{owner}_{repo}--worktrees/{prefix}--{number}-{slug}/  <- worktree
```

```bash
mkdir -p repos/{owner}_{repo}--worktrees

git -C repos/{owner}_{repo} worktree add \
  ../repos/{owner}_{repo}--worktrees/{prefix}--{number}-{slug} \
  -b {prefix}/{number}-{slug}
```

### Phase 5 — Launch Agents in Parallel

Spawn all agents in a **single Task tool message** using `subagent_type: general-purpose`. See `../shared/references/agent-spawning.md` § Parallel Execution Pattern.

Read `agents/implementation-agent.md` for the prompt template. Substitute: `{owner}`, `{repo}`, `{default_branch}`, `{detected_stack}`, `{prefix}`, `{number}`, `{slug}`, `{title}`, `{body}`, and optionally `{analysis_comment_content}`.

### Phase 6 — Collect Results & Update Labels

After all agents complete, parse JSON results per `../shared/references/agent-spawning.md` § Agent Result Contract.

**On success (PASS):**

```bash
gh issue edit {number} --repo {owner}/{repo} \
  --remove-label "status:triaged,status:analyzing" \
  --add-label "status:in-progress"
```

**On failure:** Apply the circuit breaker (up to 3 attempts). If still failing, mark `NEEDS_HUMAN`.

**Label update rules:**

| Agent Status | Label Action | Worktree |
|---|---|---|
| `PASS` | Remove `status:triaged`/`status:analyzing`, add `status:in-progress` | Remove |
| `FAILED` (retries exhausted) | Leave unchanged | Remove |
| `NEEDS_HUMAN` | Leave unchanged | Preserve with instructions |

### Phase 7 — Cleanup Worktrees

Per `../shared/references/agent-spawning.md` § Worktree Cleanup:

- Remove worktrees for PASS and FAILED items
- Leave NEEDS_HUMAN worktrees in place
- Prune stale references, remove empty directory

### Phase 8 — Final Report

```
## Results: {owner}/{repo}

| # | Issue | Type | Status | PR |
|---|-------|------|--------|----|
| #42 | Login crashes | bug | [PASS] | #101 |
| #15 | Add dark mode | feature | [NEEDS_HUMAN] | — |
| #18 | Update README | docs | [PASS] | #102 |

---

Summary:
  Implemented: {n_pass}/{n_total}
  PRs created: {n_prs}
  By type: {n_bug} bugs, {n_feature} features, {n_docs} docs

{If any NEEDS_HUMAN:}
Remaining:
  [NEEDS_HUMAN] #15 Add dark mode — worktree at repos/{o}_{r}--worktrees/feat--15-dark-mode/
    Reason: Feature requires design decisions about theme system architecture
```

**Routing suggestion:** `To merge created PRs: /ghs-merge-prs {owner}/{repo}`

### Verification Checklist

Before marking any issue as PASS, the agent must confirm:

| Check | Required |
|-------|----------|
| Implementation matches issue requirements | Always |
| Code follows project's existing style/patterns | Always |
| Tests added/updated (if project has test suite) | When testable |
| Commit message includes `Fixes #{number}` | Always |
| PR body has Summary, Changes, Testing sections | Always |
| No files modified outside issue scope | Always |
| Linter/type-checker passes (if configured) | When available |

### Goal-Backward Verification

| Level | Check | Method |
|-------|-------|--------|
| Existence | Output artifact exists | File/PR/API response check |
| Substance | Contains correct content | Diff review, body inspection |
| Wiring | Properly connected | Correct branch target, auto-close refs |

### PR Template

```
## Summary
{1-2 sentence description of what was implemented}

Fixes #{number}

## Changes
- {file}: {what changed and why}
- {file}: {what changed and why}

## Testing
- {how the changes were verified}

## Discovered Issues
{Any adjacent problems found but NOT fixed — to be filed separately}
```

</process>

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Issue is closed | Skip by default; warn if user explicitly requests |
| Issue is a pull request | Warn and skip — PRs are reviewed, not re-implemented |
| No type label | Use `impl/` prefix; suggest `ghs-issue-triage` first |
| Branch already exists | Flag in plan; force-create with `-B` if user confirms |
| PR already exists for branch | Report existing PR, skip creating new one |
| Issue too complex | Agent sets `NEEDS_HUMAN`; worktree left for manual work |
| Agent failure | One failure doesn't block others; mark `FAILED` in report |
| Content filter blocks output | Retry with download-based approach (see `../shared/references/edge-cases.md`) |
| Issue has no analysis | Agent investigates on its own — slightly slower |
| Re-running on existing items | Issues with `status:in-progress` + open PR are skipped in batch |

## Examples

**Example 1: Single bug fix**
User: "implement issue #42"
Flow: Fetch #42 (type:bug) -> show plan -> create worktree `fix--42-login-crash` -> agent fixes bug with tests -> commit with `Fixes #42` -> create PR -> update label -> cleanup -> report with `[PASS]`.

**Example 2: Batch triaged issues**
User: "implement all triaged issues"
Flow: Fetch issues with `status:triaged` -> show batch plan (priority order) -> user confirms -> create worktrees -> spawn agents in parallel -> collect results -> update labels -> cleanup -> report.

**Example 3: Issue with prior analysis**
User: "implement #42" (has analysis comment from ghs-issue-analyze)
Flow: Same as Example 1, but agent receives analysis as context (affected files, suggested approach). Faster and more targeted implementation.
