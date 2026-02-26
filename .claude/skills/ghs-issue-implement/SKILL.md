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
  version: 1.0.0
---

# Issue Implementation

Implement GitHub issues using parallel worktree-based agents. Creates branches, spawns agents to write code, verifies results, and opens PRs with auto-close references.

## Prerequisites

See `../shared/gh-prerequisites.md` for authentication, repo detection, and error handling.

See `../shared/implementation-workflow.md` for:
- §1 Repository Preparation (clone/pull, default branch, tech stack)
- §2 Worktree Management (path convention, creation, cleanup)
- §3 Branch/Commit/Push/PR Workflow (agent instructions)
- §4 Agent Result Contract (JSON format)
- §5 Pre-flight Checks (branch conflicts, existing PRs)
- §6 Content Filter Workaround

The user must have **write access** to the target repository (required for pushing branches and creating PRs).

## Input

Three invocation modes:

- **Single issue**: `implement issue #42` or `implement #42`
- **Batch by label**: `implement all triaged issues` — fetches issues with `status:triaged` label
- **Batch by type**: `implement all bugs` — fetches issues with `type:bug` label

## Architecture

This skill uses the same **parallel worktree-based agent** pattern as `ghs-backlog-fix`.

### Roles

1. **Orchestrator** (you): fetches issues, prepares repo, creates worktrees, spawns agents, collects results, updates labels, cleans up
2. **Implementation Agents** (spawned via Task tool): one per issue, each working in its own worktree

### Branch Naming

Branch prefix is determined by the issue's type label:

| Type Label | Branch Prefix | Example |
|-----------|---------------|---------|
| `type:bug` | `fix/` | `fix/42-login-crash` |
| `type:feature` | `feat/` | `feat/15-dark-mode` |
| `type:docs` | `docs/` | `docs/18-update-readme` |
| `type:hotfix` | `fix/` | `fix/99-security-vuln` |
| (default) | `impl/` | `impl/50-misc-task` |

Branch naming pattern: `{prefix}/{issue-number}-{short-slug}`

Where `{short-slug}` is derived from the issue title: lowercase, non-alphanumeric replaced with `-`, truncated to 40 chars.

### Worktree Path Convention

Per `../shared/implementation-workflow.md` §2:

```
repos/{owner}_{repo}--worktrees/{prefix}--{issue-number}-{short-slug}/
```

---

## Phase 1 — Fetch Issues

### Single issue mode

```bash
gh issue view {number} --repo {owner}/{repo} \
  --json number,title,body,labels,comments,assignees,state
```

Skip if the issue is closed (unless user explicitly requests).

### Batch mode

```bash
gh issue list --repo {owner}/{repo} --state open --label "{filter_label}" \
  --json number,title,body,labels,comments --limit 50
```

For each issue, extract:
- Number, title, body
- Type label (for branch prefix)
- Priority label (for ordering — critical first)
- Comments (check for analysis comments from `ghs-issue-analyze`)

### Analysis Context

If an issue has a comment starting with `## Issue Analysis` (from `ghs-issue-analyze`), extract it and include it as context for the implementation agent. This provides:
- Affected files and line numbers
- Suggested approach
- Complexity assessment
- Risks and dependencies

## Phase 2 — Prepare Repository

Follow `../shared/implementation-workflow.md` §1:
1. Clone or pull the repo to `repos/{owner}_{repo}/`
2. Detect default branch
3. Detect tech stack

## Phase 3 — Show Plan & Confirm

Display a summary of what will be implemented:

### Batch plan

```
## Implementation Plan: {owner}/{repo}

| # | Issue | Type | Priority | Branch | Has Analysis? |
|---|-------|------|----------|--------|---------------|
| 1 | #42 Login crashes | bug | high | fix/42-login-crash | Yes |
| 2 | #15 Add dark mode | feature | medium | feat/15-dark-mode | No |
| 3 | #18 Update README | docs | low | docs/18-update-readme | Yes |

Total: {N} issues ({n_bug} bugs, {n_feature} features, {n_docs} docs)

Proceed with all? (y/n/select)
```

### Single issue plan

```
## Plan: #{number} — {title}

Repository: {owner}/{repo}
Type:       {type_label}
Priority:   {priority_label}
Branch:     {prefix}/{number}-{slug} (from {default_branch})
Analysis:   {Yes — see comment | No — will analyze during implementation}

### What I'll do:
{Numbered list of implementation steps — from analysis comment if available, otherwise AI-determined}

### Files to create/modify:
{List of files from analysis, or "Will determine during implementation"}

Proceed? (y/n)
```

Wait for user confirmation.

### Pre-flight checks

Per `../shared/implementation-workflow.md` §5:
- Check for branch conflicts
- Check for existing PRs

## Phase 4 — Create Worktrees

Per `../shared/implementation-workflow.md` §2:

```bash
mkdir -p repos/{owner}_{repo}--worktrees

git -C repos/{owner}_{repo} worktree add \
  ../repos/{owner}_{repo}--worktrees/{prefix}--{number}-{slug} \
  -b {prefix}/{number}-{slug}
```

## Phase 5 — Launch Agents in Parallel

Spawn all agents in a **single Task tool message** using `subagent_type: general-purpose`.

### Agent Prompt Template

```
You are a ghs-issue-implement agent implementing a GitHub issue.

Repository: {owner}/{repo}
Default branch: {default_branch}
Tech stack: {detected_stack}
Worktree path: repos/{owner}_{repo}--worktrees/{prefix}--{number}-{slug}/
Branch: {prefix}/{number}-{slug}
Date: {YYYY-MM-DD}

Issue:
- Number: #{number}
- Title: {title}
- Body: {body}

{If analysis comment exists:}
Previous Analysis:
{analysis_comment_content}

{If issue has useful comments:}
Issue Comments:
{relevant_comments}

Your job:
1. Understand the issue and what needs to change
2. Inspect the repo in the worktree to understand existing patterns, architecture, and conventions
3. Implement the fix/feature following the project's existing style and patterns
4. Write/update tests if the project has a test suite and the change is testable
5. Stage, commit, and push:
   git -C {worktree_path} add {files}
   git -C {worktree_path} commit -m "{type}: {descriptive message}

   Fixes #{number}"
   git -C {worktree_path} push -u origin {prefix}/{number}-{slug}
6. Create a PR:
   gh pr create --repo {owner}/{repo} \
     --head {prefix}/{number}-{slug} --base {default_branch} \
     --title "{type}: {concise title}" \
     --body "## Summary

   {description of changes}

   Fixes #{number}

   ## Changes
   {list of changes}

   ## Testing
   {testing notes}"

Important:
- Work ONLY in your worktree path
- Do NOT checkout other branches or modify the main clone
- Follow the project's existing code style, patterns, and conventions
- If the project uses TypeScript, write TypeScript. If it uses Python typing, use type hints. Etc.
- Write meaningful commit messages that explain WHY, not just WHAT
- If the issue is too complex or ambiguous, set status to NEEDS_HUMAN and explain why
- For content filter issues, see §6 of implementation-workflow.md

Return a fenced JSON object:
{
  "source": "issue",
  "slug": "{number}-{short_slug}",
  "status": "PASS",
  "pr_url": "https://github.com/{owner}/{repo}/pull/N",
  "verification": ["List of checks performed"],
  "error": null
}
```

## Phase 6 — Collect Results & Update Labels

After all agents complete:

1. Parse the JSON result from each agent
2. For each successful item (status = PASS):
   - Update issue label: remove `status:triaged` or `status:analyzing`, add `status:in-progress`
   ```bash
   gh issue edit {number} --repo {owner}/{repo} \
     --remove-label "status:triaged,status:analyzing" \
     --add-label "status:in-progress"
   ```
3. For FAILED items:
   - Leave labels unchanged
   - Log the error for the final report
4. For NEEDS_HUMAN items:
   - Leave labels unchanged
   - Note that the worktree is left in place

## Phase 7 — Cleanup Worktrees

Per `../shared/implementation-workflow.md` §2 (Cleanup section):

- Remove worktrees for PASS and FAILED items
- Leave NEEDS_HUMAN worktrees in place with instructions
- Prune and remove empty worktree directory

## Phase 8 — Final Report

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

{If any FAILED or NEEDS_HUMAN:}
Remaining:
  [NEEDS_HUMAN] #15 Add dark mode — worktree at repos/{o}_{r}--worktrees/feat--15-dark-mode/
    Reason: Feature requires design decisions about theme system architecture
```

## Edge Cases

- **Issue is closed**: Skip by default. Warn the user if they explicitly request a closed issue.
- **Issue is a pull request**: Warn and skip — PRs should be reviewed, not re-implemented.
- **No type label**: Use `impl/` prefix. Suggest running `ghs-issue-triage` first.
- **Branch already exists**: Flag in plan table. If confirmed, force-create with `-B`.
- **PR already exists for branch**: Report existing PR, skip creating a new one.
- **Issue too complex**: Agent sets NEEDS_HUMAN — worktree left in place for manual work.
- **Agent failure**: One agent failing doesn't block others. Mark FAILED in report.
- **Content filter blocks output**: Orchestrator handles per §6 of implementation-workflow.md.
- **Issue has no analysis**: Agent performs its own investigation — it just takes slightly longer.
- **Merge conflicts**: If the branch has conflicts with the default branch, report and let user decide.
- **Re-running is safe**: Issues already with `status:in-progress` and an open PR are skipped in batch mode.

## Examples

**Example 1: Implement a single bug fix**
User says: "implement issue #42"
Result: Fetches issue (type:bug), clones/pulls repo, shows plan, creates worktree at `repos/o_r--worktrees/fix--42-login-crash/`, spawns agent, agent fixes the bug with tests, commits with "Fixes #42", pushes, creates PR, label updated to status:in-progress, worktree cleaned up.

**Example 2: Implement all triaged issues**
User says: "implement all triaged issues"
Result: Fetches issues with status:triaged, shows batch plan ordered by priority, user confirms, creates worktrees, spawns agents in parallel, collects results, updates labels, cleans up, shows report.

**Example 3: Implement all bugs**
User says: "implement all bugs"
Result: Fetches issues with type:bug label, same flow as batch.

**Example 4: Implement with prior analysis**
User says: "implement #42" (issue has an analysis comment from ghs-issue-analyze)
Result: Agent receives the analysis as context, uses suggested approach and affected files to guide implementation. Faster and more targeted than without analysis.
