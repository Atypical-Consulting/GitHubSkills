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
  version: 2.0.0
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
Purpose: Implement GitHub issues by spawning worktree-based agents that write code, run tests, and create PRs.

Roles:
1. **Orchestrator** (you) — fetches issues, prepares repo, creates worktrees, spawns agents, collects results, updates labels, cleans up
2. **Implementation Agents** (spawned via Task tool) — one per issue, each working in its own worktree

Agent prompt: `agents/implementation-agent.md`

Shared docs:
- `../shared/gh-prerequisites.md` — authentication, repo detection, error handling
- `../shared/implementation-workflow.md` — §1 Repo Prep, §2 Worktree Mgmt, §3 Branch/Commit/Push/PR, §4 Agent Result Contract, §5 Pre-flight, §6 Content Filter
- `../shared/edge-cases.md` — rate limiting, content filters, permission errors, bounded retries
- `../shared/agent-result-contract.md` — universal agent response format

The user must have **write access** to the target repository.
</context>

<objective>
Implement GitHub issues and create PRs with auto-close references.

Outputs:
- PRs created on GitHub for each implemented issue
- Issue labels updated to `status:in-progress`
- Terminal report with results table

Next routing:
- Suggest `ghs-merge-prs` to merge the created PRs — "To merge: `/ghs-merge-prs {owner}/{repo}`"
- If issues lack type/priority labels, suggest `ghs-issue-triage` first — "Run `/ghs-issue-triage` to classify issues before implementing"
- For complex issues, suggest `ghs-issue-analyze` first — "Run `/ghs-issue-analyze #{number}` for a detailed breakdown"
</objective>

<process>

## Input

Three invocation modes:

- **Single issue**: `implement issue #42` or `implement #42`
- **Batch by label**: `implement all triaged issues` — fetches issues with `status:triaged` label
- **Batch by type**: `implement all bugs` — fetches issues with `type:bug` label

## Branch Naming

Branch prefix is determined by the issue's type label — this keeps the git log readable:

| Type Label | Branch Prefix | Example |
|-----------|---------------|---------|
| `type:bug` | `fix/` | `fix/42-login-crash` |
| `type:feature` | `feat/` | `feat/15-dark-mode` |
| `type:docs` | `docs/` | `docs/18-update-readme` |
| `type:hotfix` | `fix/` | `fix/99-security-vuln` |
| (default) | `impl/` | `impl/50-misc-task` |

Branch naming pattern: `{prefix}/{issue-number}-{short-slug}`
Where `{short-slug}` is derived from the issue title: lowercase, non-alphanumeric replaced with `-`, truncated to 40 chars.

Worktree path per `../shared/implementation-workflow.md` §2:
```
repos/{owner}_{repo}--worktrees/{prefix}--{issue-number}-{short-slug}/
```

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

If an issue has a comment starting with `## Issue Analysis` (from `ghs-issue-analyze`), extract it and include it as context for the implementation agent. This provides affected files, suggested approach, and complexity assessment — saving the agent significant investigation time.

## Phase 2 — Prepare Repository

Follow `../shared/implementation-workflow.md` §1:
1. Clone or pull the repo to `repos/{owner}_{repo}/`
2. Detect default branch
3. Detect tech stack

## Phase 3 — Show Plan & Confirm

### Batch plan

```
## Implementation Plan: {owner}/{repo}

| # | Issue | Type | Priority | Branch | Has Analysis? |
|---|-------|------|----------|--------|---------------|
| 1 | #42 Login crashes | bug | high | fix/42-login-crash | Yes |
| 2 | #15 Add dark mode | feature | medium | feat/15-dark-mode | No |
...

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
{Numbered list of implementation steps}

### Files to create/modify:
{List of files from analysis, or "Will determine during implementation"}

Proceed? (y/n)
```

Wait for user confirmation.

### Pre-flight checks

Per `../shared/implementation-workflow.md` §5 — check for branch conflicts and existing PRs.

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

Read `agents/implementation-agent.md` for the prompt template. Substitute `{owner}`, `{repo}`, `{default_branch}`, `{detected_stack}`, `{prefix}`, `{number}`, `{slug}`, `{title}`, `{body}`, and optionally `{analysis_comment_content}` placeholders.

## Phase 6 — Collect Results & Update Labels

After all agents complete:

1. Parse the JSON result from each agent

**Bounded retries**: If an agent returns status FAILED and the error suggests a transient issue (content filter, timeout, malformed output):
- Retry once with the error message appended to the agent prompt
- If the retry also fails, mark as NEEDS_HUMAN — two failures on the same item indicate a problem that needs human judgment
- See `../shared/edge-cases.md` for the full retry protocol

2. For each successful item (status = PASS):
   - Update issue label: remove `status:triaged` or `status:analyzing`, add `status:in-progress`
   ```bash
   gh issue edit {number} --repo {owner}/{repo} \
     --remove-label "status:triaged,status:analyzing" \
     --add-label "status:in-progress"
   ```
3. For FAILED items: leave labels unchanged, log the error
4. For NEEDS_HUMAN items: leave labels unchanged, note worktree is preserved

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

</process>

## Edge Cases

- **Issue is closed**: Skip by default. Warn the user if they explicitly request a closed issue.
- **Issue is a pull request**: Warn and skip — PRs should be reviewed, not re-implemented.
- **No type label**: Use `impl/` prefix. Suggest running `ghs-issue-triage` first.
- **Branch already exists**: Flag in plan table. If confirmed, force-create with `-B`.
- **PR already exists for branch**: Report existing PR, skip creating a new one.
- **Issue too complex**: Agent sets NEEDS_HUMAN — worktree left in place for manual work.
- **Agent failure**: One agent failing doesn't block others. Mark FAILED in report.
- **Content filter blocks output**: The orchestrator detects content filter failures and retries with a download-based approach. See `../shared/edge-cases.md` for the workaround pattern.
- **Issue has no analysis**: Agent performs its own investigation — it just takes slightly longer.
- **Re-running is safe**: Issues already with `status:in-progress` and an open PR are skipped in batch mode.

## Examples

**Example 1: Implement a single bug fix**
User says: "implement issue #42"
Result: Fetches issue (type:bug), clones/pulls repo, shows plan, creates worktree, spawns agent, agent fixes the bug with tests, commits with "Fixes #42", creates PR, label updated.

**Example 2: Implement all triaged issues**
User says: "implement all triaged issues"
Result: Fetches issues with status:triaged, shows batch plan ordered by priority, user confirms, creates worktrees, spawns agents in parallel, collects results, shows report.

**Example 3: Implement with prior analysis**
User says: "implement #42" (issue has an analysis comment from ghs-issue-analyze)
Result: Agent receives the analysis as context, uses suggested approach and affected files. Faster and more targeted.
