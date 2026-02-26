---
name: ghs:backlog-fix
description: >
  Applies backlog item fixes to a GitHub repository using parallel worktree-based agents — clones
  the repo once, creates git worktrees for each fix, launches agents simultaneously, verifies
  acceptance criteria, and creates PRs. Use this skill whenever the user wants to apply, fix, or
  resolve a backlog item, references a backlog markdown file, or says things like "apply this
  backlog item", "fix this issue", "resolve this finding", "work on this backlog item", "apply
  tier-1--license", or points to any file under backlog/. Also trigger when the user says "apply all
  backlog items", "fix all findings", "resolve all tier 1 items", or "apply all for {repo}".
  Do NOT use for scanning repos (use ghs:repo-scan), viewing backlog status (use ghs:backlog-board), or general code review.
metadata:
  author: phmatray
  version: 4.0.0
---

# Apply Backlog Item

Read structured backlog items (health findings or GitHub issues), apply fixes using parallel worktree-based agents, verify acceptance criteria, and update item statuses.

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

Two invocation modes:

- **Single item**: A path to a backlog item markdown file
  - Health: `backlog/phmatray_Formidable/health/tier-1--license.md`
  - Issue: `backlog/phmatray_Formidable/issues/issue-42--login-bug.md`

- **Batch (repo)**: A repo identifier like `phmatray_Formidable`
  - Discovers all FAIL items in `backlog/{owner}_{repo}/health/`
  - Processes them in parallel using worktree-based agents

## Architecture

This skill uses **parallel worktree-based agents** to apply multiple fixes simultaneously. Instead of processing items one at a time (clone → branch → fix → push → PR → repeat), it creates one clone and multiple git worktrees, then spawns agents that work in parallel.

### Roles

1. **Orchestrator** (you): discovers items, classifies them, prepares the repo, creates worktrees, spawns agents, collects results, updates backlog, cleans up
2. **Category A Agent** (spawned via Task tool): handles all API-only fixes (no worktree needed)
3. **Category B Agents** (spawned via Task tool): one per file-change item, each working in its own worktree
4. **Category CI Agent** (spawned via Task tool): handles ci-workflow-health in its own worktree (diagnoses before fixing)

### Item Categories

Each health check falls into one of these categories:

| Category | Description | Worktree? | Checks |
|----------|-------------|-----------|--------|
| **A** (API-only) | Uses `gh` commands directly, no file changes | No | branch-protection, security-alerts, description, topics, delete-branch-on-merge, merge-strategy, homepage-url, stale-branches, github-releases |
| **B** (file changes) | Creates/modifies files, commits, pushes, creates PR | Yes — one per item | license, editorconfig, codeowners, issue-templates, pr-template, security-md, contributing-md, code-of-conduct, readme, gitignore, ci-cd-workflows, changelog, gitattributes, version-pinning, dependency-update-config |
| **CI** (special) | Diagnoses CI failures before fixing | Yes | ci-workflow-health |

Issue items are always Category B.

---

## Phase 1 — Discover & Classify

### Single-item mode

Parse the provided backlog item file. Determine its type and category. Skip if status is already PASS.

### Batch mode

Scan `backlog/{owner}_{repo}/health/` for all items. For each file:

1. Read the file and check the `Status` field
2. Skip items with status PASS
3. Classify each FAIL item into Category A, B, or CI based on its slug

You can parse items programmatically: `python .claude/skills/shared/scripts/parse_backlog_item.py <path>`

For detailed fix strategies per check, read `../shared/checks/index.md` for the Slug-to-Path Lookup table, then read the individual check file at `../shared/checks/{category}/{slug}.md`.

## Phase 2 — Prepare Repository

Follow `../shared/implementation-workflow.md` §1 to clone or pull the repo and detect the default branch and tech stack.

## Phase 3 — Show Batch Plan & Confirm

Display a summary table of ALL items to be processed:

```
## Batch Plan: {owner}/{repo}

| # | Item | Tier | Pts | Category | Branch | Worktree |
|---|------|------|-----|----------|--------|----------|
| 1 | LICENSE | T1 | 4 | B (file) | fix/license | repos/{o}_{r}--worktrees/fix--license/ |
| 2 | Branch Protection | T1 | 4 | A (API) | — | — |
| 3 | .editorconfig | T2 | 2 | B (file) | fix/editorconfig | repos/{o}_{r}--worktrees/fix--editorconfig/ |
| 4 | CI Workflow Health | T2 | 2 | CI | fix/ci-workflow-health | repos/{o}_{r}--worktrees/fix--ci-workflow-health/ |
...

Total items: {N} ({cat_a} API-only, {cat_b} file changes, {cat_ci} CI)
Points recoverable: {total_points}

Proceed with all? (y/n/select)
```

- **y**: proceed with all items
- **n**: cancel
- **select**: let the user pick which items to apply

For single-item mode, show a simpler plan:

```
## Plan: {Title}

Repository: {owner}/{repo}
Source:     {Health Check — Tier N | Issue #N}
Category:  {A (API-only) | B (file changes) | CI}
Branch:    fix/{slug} (from {default_branch})

### What I'll do:
{Numbered list of specific actions}

### Files to create/modify:
{List of files, or "None — API-only fix"}

Proceed? (y/n)
```

Wait for user confirmation before continuing.

### Pre-flight checks

Per `../shared/implementation-workflow.md` §5 — check for branch conflicts and existing PRs. Flag any conflicts in the plan table.

## Phase 4 — Create Worktrees

Per `../shared/implementation-workflow.md` §2 — create worktrees for each Category B and CI item.

Category A items don't need worktrees — they use `gh` API commands directly.

## Phase 5 — Launch Agents in Parallel

Spawn all agents in a **single Task tool message** for parallel execution. Each agent gets a self-contained prompt and returns structured JSON per `../shared/implementation-workflow.md` §4.

### Category A Agent Prompt

If there are Category A items, spawn **one** agent to handle all of them:

```
You are a ghs:backlog-fix agent handling API-only fixes.

Repository: {owner}/{repo}
Default branch: {default_branch}
Skills path: {path to .claude/skills}
Date: {YYYY-MM-DD}

Items to fix:
{For each Category A item:}
- Slug: {slug}
  Backlog file: {path}
  Check file: {skills_path}/shared/checks/{category}/{slug}.md (use Slug-to-Path Lookup in index.md)

Your job:
1. For each item, read the check file to understand the fix strategy
2. Apply the fix using `gh` CLI commands
3. Verify the fix took effect using the verification command from the check file

Important:
- For branch-protection: detect solo maintainer (single owner, no collaborators) and use lightweight rules
- For description/topics: inspect the repo to propose meaningful values, not placeholders
- Use `2>&1 || true` on gh commands to handle errors gracefully

Return a fenced JSON array with one object per item (see §4 of implementation-workflow.md for format).
Set "source" to "health" for all items.
```

### Category B Agent Prompt (one per item)

```
You are a ghs:backlog-fix agent handling a file-change fix.

Repository: {owner}/{repo}
Default branch: {default_branch}
Worktree path: repos/{owner}_{repo}--worktrees/fix--{slug}/
Branch: fix/{slug}
Skills path: {path to .claude/skills}
Date: {YYYY-MM-DD}

Item to fix:
- Slug: {slug}
  Backlog file: {item_path}
  Check file: {skills_path}/shared/checks/{category}/{slug}.md (use Slug-to-Path Lookup in index.md)

Your job:
1. Read the backlog item file to understand what's missing
2. Read the check file for the fix strategy (see "Backlog Content" section)
3. Inspect the repo in the worktree to understand the project (name, purpose, tech stack, build tools, existing patterns)
4. Generate thoughtful, repo-aware content — not minimal stubs
5. Stage, commit, push, and create PR (follow §3 of implementation-workflow.md)
   The PR body should reference the backlog item and include acceptance criteria as a checklist.
6. Verify acceptance criteria from the backlog item

Important:
- Work ONLY in your worktree path: {worktree_path}
- Do NOT checkout other branches or modify the main clone
- Generate quality content by inspecting the repo — not boilerplate
- If the fix requires multiple files, create all of them
- For content filter issues, see §6 of implementation-workflow.md

Return a fenced JSON object (see §4 of implementation-workflow.md for format).
Set "source" to "health". Set "item_path" to the backlog file path.
If something goes wrong, set status to "FAILED" and include the error message.
If the fix requires human judgment, set status to "NEEDS_HUMAN" and explain why in error.
```

### Category CI Agent Prompt

Same as Category B, but with an additional diagnostic step:

```
You are a ghs:backlog-fix agent handling CI workflow health fixes.

{Same header as Category B agent}

Your job:
1. Read the backlog item and check file
2. DIAGNOSE FIRST: examine the failing workflow files, recent run logs, and error patterns
   gh run list --repo {owner}/{repo} --limit 5 --json status,conclusion,name,headBranch
   gh run view {run_id} --repo {owner}/{repo} --log-failed 2>&1 | head -100
3. Determine the root cause (missing dependency, wrong version, syntax error, etc.)
4. Apply the fix in your worktree
5. Stage, commit, push, and create PR (follow §3 of implementation-workflow.md)
6. Verify the workflow file is valid YAML

{Same return contract as Category B}
```

### Launching All Agents

Use the Task tool to spawn all agents in a **single message**:

- 1 Category A agent (if any A items exist) — `subagent_type: general-purpose`
- N Category B agents (1 per file-change item) — `subagent_type: general-purpose`
- 1 Category CI agent (if ci-workflow-health is failing) — `subagent_type: general-purpose`

For issue items, use the Category B agent pattern but adapt the prompt:
- Read the full issue from GitHub: `gh issue view {number} --repo {owner}/{repo}`
- Include "Fixes #{number}" in the commit message and PR body

## Phase 6 — Collect Results & Update Backlog

After all agents complete:

1. Parse the JSON result from each agent
2. For each successful item (status = PASS):
   - Update the backlog item file: change `| **Status** | FAIL |` to `| **Status** | PASS |`
   - Check all acceptance criteria boxes
   - Add PR URL if one was created
3. For failed items (status = FAILED):
   - Leave the backlog item as FAIL
   - Log the error for the final report
4. For NEEDS_HUMAN items:
   - Leave the backlog item as FAIL
   - Note in the report that the worktree is left in place
5. Update `backlog/{owner}_{repo}/SUMMARY.md`:
   - Change status from FAIL to PASS for successful items
   - Add PR URLs where applicable
   - Recalculate the health score

You can verify the score with: `python .claude/skills/shared/scripts/calculate_score.py backlog/{owner}_{repo}`

## Phase 7 — Cleanup Worktrees

Per `../shared/implementation-workflow.md` §2 (Cleanup section):

- Remove worktrees for PASS and FAILED items
- Leave NEEDS_HUMAN worktrees in place with instructions
- Prune and remove empty worktree directory

## Phase 8 — Final Report

Display a summary table with all results:

```
## Results: {owner}/{repo}

| Item | Tier | Pts | Status | PR |
|------|------|-----|--------|----|
| LICENSE | T1 | 4 | [PASS] | #12 |
| Branch Protection | T1 | 4 | [PASS] | — (API) |
| .editorconfig | T2 | 2 | [PASS] | #13 |
| CI Workflow Health | T2 | 2 | [FAILED] | — |
| CODEOWNERS | T2 | 2 | [PASS] | #14 |
...

---

Summary:
  Applied: {n_pass}/{n_total}
  PRs created: {n_prs}
  Points recovered: {points_recovered}/{points_possible}
  New health score: {new_score}% (was {old_score}%)

{If any FAILED or NEEDS_HUMAN items:}
Remaining items:
  [FAILED] CI Workflow Health — {error}
  [NEEDS_HUMAN] ... — worktree at ...
```

## Single-Item Fast Path

When a single file path is provided:

1. Parse the item, classify as Category A, B, or CI
2. Clone/pull repo (Phase 2)
3. Show single-item plan, get `y/n` (Phase 3)
4. **Category A**: run the `gh` command directly in the orchestrator (no agent needed for a single API call)
5. **Category B/CI**: create one worktree, spawn one agent
6. Update backlog, cleanup worktree, report

## Edge Cases

- **Already PASS**: Skip the item. In batch mode, exclude from the plan table.
- **Already closed issues**: Update local backlog status to CLOSED and skip.
- **Branch already exists remotely**: Flag in plan table. If user confirms, force-create the branch (`-B` flag on worktree add).
- **Agent failure**: One agent failing doesn't block others. Mark the item FAILED in the report.
- **NEEDS_HUMAN**: Worktree left in place with instructions. Not cleaned up.
- **Re-running is safe**: Phase 1 skips already-PASS items. Idempotent.
- **WARN items**: These indicate permission issues. Before applying, check if the user now has sufficient permissions. If not, explain what's needed.
- **Complex issues**: If an issue seems too complex to auto-fix, present a plan and let the user guide the implementation.
- **Merge conflicts**: If a worktree branch has conflicts, report and let the user decide.
- **PR already exists for branch**: Check with `gh pr list --head fix/{slug}` before creating a new one.
- **Content filtering blocks agent output**: See `../shared/implementation-workflow.md` §6.

## Examples

**Example 1: Apply a single health item**
User says: "apply backlog/phmatray_Formidable/health/tier-1--license.md"
Result: Parses item (Category B), clones/pulls repo, shows plan, creates one worktree at `repos/phmatray_Formidable--worktrees/fix--license/`, spawns one agent, agent generates LICENSE file, commits, pushes, creates PR, orchestrator verifies, updates backlog to PASS, cleans up worktree.

**Example 2: Apply all items for a repo**
User says: "apply all for phmatray_Formidable"
Result: Discovers 10 FAIL items, classifies (2 Cat A, 7 Cat B, 1 Cat CI), shows batch plan table, user confirms, creates 8 worktrees, launches 10 agents in parallel (1 Cat A handling 2 items + 7 Cat B + 1 Cat CI), collects results, updates all backlog items, cleans up worktrees, shows final report with PRs and new score.

**Example 3: Apply an issue fix**
User says: "fix backlog/phmatray_Formidable/issues/issue-42--login-page-crashes.md"
Result: Parses issue (Category B), fetches full issue body from GitHub, creates worktree, spawns agent, agent implements fix with "Fixes #42" in commit, creates PR, updates backlog to PR CREATED.

**Example 4: Re-run after partial success**
User says: "apply all for phmatray_Formidable" (after a previous run where 7/10 passed)
Result: Discovers only 3 remaining FAIL items, shows smaller batch plan, processes only those.

## Troubleshooting

**Item status is already PASS**
The fix has already been applied. The skill will skip it and tell you.

**"Permission denied" when pushing branch**
You need write access to the repository. Check `gh repo view --json viewerPermission`.

**Worktree creation fails**
If the branch already exists locally: `git -C repos/{owner}_{repo} branch -D fix/{slug}` then retry.
If it exists remotely: use `-B` flag to force-create, or ask user.

**Agent returns NEEDS_HUMAN**
The fix requires human judgment. The worktree is left in place — `cd` into it and make changes manually, then push and create a PR.

**PR creation fails**
Common causes: branch already exists remotely (skill checks for this in Phase 3), or default branch is protected. Check `gh pr list --head fix/{slug}` for existing PRs.

**Worktrees not cleaned up**
Run `git -C repos/{owner}_{repo} worktree list` to see active worktrees. Remove with `git worktree remove <path>`.
