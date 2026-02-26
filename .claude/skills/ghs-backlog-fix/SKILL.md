---
name: ghs-backlog-fix
description: >
  Applies backlog item fixes to a GitHub repository using parallel worktree-based agents — clones
  the repo once, creates git worktrees for each fix, launches agents simultaneously, verifies
  acceptance criteria, and creates PRs. Use this skill whenever the user wants to apply, fix, or
  resolve a backlog item, references a backlog markdown file, or says things like "apply this
  backlog item", "fix this issue", "resolve this finding", "work on this backlog item", "apply
  tier-1--license", or points to any file under backlog/. Also trigger when the user says "apply all
  backlog items", "fix all findings", "resolve all tier 1 items", or "apply all for {repo}".
  Do NOT use for scanning repos (use ghs-repo-scan), viewing backlog status (use ghs-backlog-board), or general code review.
allowed-tools: "Bash(gh:*) Bash(git:*) Bash(python3:*) Read Write Edit Glob Grep Task"
compatibility: "Requires gh CLI (authenticated), git, python3, network access"
license: MIT
metadata:
  author: phmatray
  version: 5.0.0
routes-to:
  - ghs-merge-prs
  - ghs-backlog-board
  - ghs-repo-scan
routes-from:
  - ghs-repo-scan
  - ghs-backlog-board
  - ghs-backlog-next
---

# Apply Backlog Item

Read structured backlog items (health findings or GitHub issues), apply fixes using parallel worktree-based agents, verify acceptance criteria, and update item statuses.

<context>
Purpose: Apply backlog item fixes using parallel worktree-based agents — one clone, multiple worktrees, simultaneous agents.

Roles:
1. **Orchestrator** (you) — discovers items, classifies them, prepares the repo, creates worktrees, spawns agents, collects results, updates backlog, cleans up
2. **Category A Agent** — handles all API-only fixes (no worktree needed)
3. **Category B Agents** — one per file-change item, each working in its own worktree
4. **Category CI Agent** — handles ci-workflow-health in its own worktree (diagnoses before fixing)

Agent prompts: `agents/category-a-agent.md`, `agents/category-b-agent.md`, `agents/category-ci-agent.md`

Shared docs:
- `../shared/gh-prerequisites.md` — authentication, repo detection, error handling
- `../shared/implementation-workflow.md` — §1 Repo Prep, §2 Worktree Mgmt, §3 Branch/Commit/Push/PR, §4 Agent Result Contract, §5 Pre-flight, §6 Content Filter
- `../shared/config.md` — scoring constants
- `../shared/backlog-format.md` — file formats and status values
- `../shared/item-categories.md` — item classification (Category A/B/CI) and routing rules
- `../shared/edge-cases.md` — rate limiting, content filters, permission errors, bounded retries
- `../shared/agent-result-contract.md` — universal agent response format

The user must have **write access** to the target repository — required for pushing branches and creating PRs.
</context>

<objective>
Apply fixes to FAIL backlog items and create PRs for file changes.

Outputs:
- PRs created on GitHub for each Category B/CI item
- API settings applied for Category A items
- Updated backlog item files (status changed from FAIL to PASS)
- Updated SUMMARY.md with new score
- Terminal report with results table

Next routing:
- Suggest `ghs-merge-prs` to merge the created PRs — "To merge: `/ghs-merge-prs {owner}/{repo}`"
- Suggest `ghs-backlog-board` to see updated dashboard
- Suggest `ghs-repo-scan` to re-scan and verify all fixes
</objective>

<process>

## Input

Two invocation modes:

- **Single item**: A path to a backlog item markdown file
  - Health: `backlog/phmatray_Formidable/health/tier-1--license.md`
  - Issue: `backlog/phmatray_Formidable/issues/issue-42--login-bug.md`

- **Batch (repo)**: A repo identifier like `phmatray_Formidable`
  - Discovers all FAIL items in `backlog/{owner}_{repo}/health/`
  - Processes them in parallel using worktree-based agents

## Item Categories

See `../shared/item-categories.md` for the full classification table (Category A/B/CI) and routing rules. Issue items are always Category B.

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
...

Total items: {N} ({cat_a} API-only, {cat_b} file changes, {cat_ci} CI)
Points recoverable: {total_points}

Proceed with all? (y/n/select)
```

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

Read the agent prompt templates and substitute placeholders:
- `agents/category-a-agent.md` — for Category A items (one agent handles all)
- `agents/category-b-agent.md` — for each Category B item (one agent per item)
- `agents/category-ci-agent.md` — for Category CI items

For issue items, use the Category B agent pattern but adapt the prompt:
- Read the full issue from GitHub: `gh issue view {number} --repo {owner}/{repo}`
- Include "Fixes #{number}" in the commit message and PR body — this triggers GitHub's auto-close

All agents use `subagent_type: general-purpose`.

## Phase 6 — Collect Results & Update Backlog

After all agents complete:

1. Parse the JSON result from each agent

**Bounded retries**: If an agent returns status FAILED and the error suggests a transient issue (content filter, timeout, malformed output):
- Retry once with the error message appended to the agent prompt
- If the retry also fails, mark as NEEDS_HUMAN — two failures on the same item indicate a problem that needs human judgment
- See `../shared/edge-cases.md` for the full retry protocol

2. For each successful item (status = PASS):
   - Update the backlog item file: change `| **Status** | FAIL |` to `| **Status** | PASS |`
   - Check all acceptance criteria boxes
   - Add PR URL if one was created
3. For failed items (status = FAILED):
   - Leave the backlog item as FAIL
   - Log the error for the final report
4. For NEEDS_HUMAN items:
   - Leave the backlog item as FAIL
   - Note in the report that the worktree is left in place — the user can continue manually
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

</process>

## Single-Item Fast Path

When a single file path is provided:

1. Parse the item, classify as Category A, B, or CI
2. Clone/pull repo (Phase 2)
3. Show single-item plan, get `y/n` (Phase 3)
4. **Category A**: run the `gh` command directly in the orchestrator — no agent needed for a single API call
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
- **Content filtering blocks agent output**: The orchestrator detects content filter failures and retries with a download-based approach. See `../shared/edge-cases.md` for the workaround pattern.

## Examples

**Example 1: Apply a single health item**
User says: "apply backlog/phmatray_Formidable/health/tier-1--license.md"
Result: Parses item (Category B), clones/pulls repo, shows plan, creates one worktree, spawns one agent, agent generates LICENSE file, commits, pushes, creates PR, orchestrator verifies, updates backlog to PASS, cleans up worktree.

**Example 2: Apply all items for a repo**
User says: "apply all for phmatray_Formidable"
Result: Discovers 10 FAIL items, classifies (2 Cat A, 7 Cat B, 1 Cat CI), shows batch plan table, user confirms, creates 8 worktrees, launches 10 agents in parallel, collects results, updates all backlog items, cleans up worktrees, shows final report.

**Example 3: Apply an issue fix**
User says: "fix backlog/phmatray_Formidable/issues/issue-42--login-page-crashes.md"
Result: Parses issue (Category B), fetches full issue body from GitHub, creates worktree, spawns agent, agent implements fix with "Fixes #42" in commit, creates PR, updates backlog.

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
