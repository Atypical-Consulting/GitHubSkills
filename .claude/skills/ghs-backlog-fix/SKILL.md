---
name: ghs-backlog-fix
description: >
  Applies backlog item fixes to a GitHub repository using parallel worktree-based agents — clones
  the repo once, creates git worktrees for each fix, launches agents simultaneously, verifies
  acceptance criteria, and creates PRs. Uses dependency-aware wave execution to prevent conflicts
  between related items and recalculates health scores after each wave for incremental progress.
  Persists session state for multi-session continuity.
  Use this skill whenever the user wants to apply, fix, or
  resolve a backlog item, references a project item, or says things like "apply this
  backlog item", "fix this issue", "resolve this finding", "work on this backlog item", "apply
  tier-1--license", or references an item in a GitHub Project. Also trigger when the user says "apply all
  backlog items", "fix all findings", "resolve all tier 1 items", or "apply all for {repo}".
  Do NOT use for scanning repos (use ghs-repo-scan), viewing backlog status (use ghs-backlog-board), or general code review.
argument-hint: "[owner/repo] [--item <slug>] [--tier 1|2|3] [--all] [--dry-run]"
allowed-tools: "Bash(gh:*) Bash(git:*) Bash(jq:*) Read Write Edit Glob Grep Task"
compatibility: "Requires gh CLI (authenticated, with project scope), git, jq, network access"
license: MIT
metadata:
  author: phmatray
  version: 9.0.0
routes-to:
  - ghs-merge-prs
  - ghs-backlog-board
  - ghs-repo-scan
routes-from:
  - ghs-repo-scan
  - ghs-backlog-board
  - ghs-backlog-next
  - ghs-backlog-sync
---

# Apply Backlog Item

Read structured project items (health findings or GitHub issues), apply fixes using wave-based parallel agents, verify acceptance criteria, and update item statuses. Uses dependency-aware wave execution to prevent conflicts and persists session state across conversations.

<anti-patterns>

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Modify files outside the fix scope | Only touch what the project item describes | Out-of-scope changes cause merge conflicts and unreviewed modifications |
| Chain fixes — one project item per agent, no side-quests | Keep each agent focused on its single assigned item | Side-quests bloat diffs and bypass acceptance criteria |
| Retry failed fixes more than 3 times | Mark as failed and move on after 3 attempts | Infinite retry loops waste time and API quota |
| Skip verification before creating a PR | Every fix must pass its acceptance criteria before PR creation | Broken PRs waste reviewer time and erode trust |
| Create PRs for incomplete fixes | Partial work stays local until complete | Incomplete PRs block the merge queue and confuse reviewers |
| Spawn all agents flat when dependencies exist | Build dependency graph and execute in waves | CI workflow fixes may depend on .editorconfig; contributing guide links to LICENSE |
| Ignore state issue at start | Read state issue for blockers and previous attempts | Re-trying known-blocked items wastes time; re-trying same approach on failed items is pointless |
| Skip score recalculation between waves | Recalculate after each wave completes using jq pipeline | Users need incremental progress feedback; blocked items in later waves need accurate state |

</anti-patterns>

## Scope Boundary

Only fix what the project item describes. Pre-existing issues, linting warnings, or
unrelated findings are out of scope. Log discoveries to deferred-items if needed.

## Context Budget

What to pass to each subagent:

| Pass | Do NOT Pass |
|------|-------------|
| The specific project item title, body, and custom field values | All project items for the repo |
| Repository structure overview (tech stack, default branch) | Full scan results |
| Acceptance criteria for this item | Other agents' output |
| Worktree path (for B/CI agents) | Unrelated check details |
| Synced issue number (if applicable) | Previous run history |
| Active blockers affecting this item (from state issue) | Full state issue contents |

See `../shared/references/agent-spawning.md` for the full agent spawning protocol, context budgeting, and worktree management patterns.

## Circuit Breaker

| Attempt | Action |
|---------|--------|
| 1st failure | Re-run agent with error context appended to prompt |
| 2nd failure | Re-run with error + stricter constraints |
| 3rd failure | Mark as `NEEDS_HUMAN`, preserve worktree, stop retrying |

After 3 failures on the same item, the orchestrator moves on. The worktree is left in place for manual continuation.

## Deviation Handling

| Rule | Trigger | Example |
|------|---------|---------|
| One item per agent | Agent prompt mentions multiple slugs | Agent assigned `license` starts modifying `.editorconfig` — reject, re-prompt with scope reminder |
| No unrelated changes | Diff contains files outside acceptance criteria | Agent adds a linting fix alongside the LICENSE — strip unrelated commits before PR |
| Verify before PR | Agent returns PASS without running checks | Agent claims PASS but acceptance criteria unchecked — re-run verification, mark FAILED if criteria unmet |
| Respect circuit breaker | Same item fails 3 times | Agent fails on `ci-workflow-health` 3 times — mark NEEDS_HUMAN, do not spawn a 4th attempt |
| Branch hygiene | Branch already exists with unrelated commits | Pre-flight detects stale branch — flag in plan, ask user before force-creating |

<context>
<execution_context>
References:
- ../shared/references/gh-cli-patterns.md
- ../shared/references/output-conventions.md
- ../shared/references/ui-brand.md
- ../shared/references/argument-parsing.md
- ../shared/references/agent-spawning.md
- ../shared/references/implementation-workflow.md
- ../shared/references/projects-format.md
- ../shared/references/scoring-logic.md
- ../shared/references/config.md
- ../shared/references/edge-cases.md
- ../shared/references/item-categories.md
- ../shared/references/state-persistence.md
- ../shared/references/checkpoint-patterns.md
- ../shared/references/agent-result-contract.md
</execution_context>

Purpose: Apply project item fixes using wave-based parallel agents — one clone, dependency-aware waves, simultaneous agents per wave.

Roles:
1. **Orchestrator** (you) — discovers items, classifies them, builds dependency graph, prepares the repo, creates worktrees, spawns agents in waves, collects results, updates project items, writes state issue, cleans up
2. **Category A Agent** — handles all API-only fixes (no worktree needed)
3. **Category B Agents** — one per file-change item, each working in its own worktree
4. **Category CI Agent** — handles ci-workflow-health in its own worktree (diagnoses before fixing)

Agent prompts: `agents/category-a-agent.md`, `agents/category-b-agent.md`, `agents/category-ci-agent.md`

### Shared References

| Reference | Path | Use For |
|-----------|------|---------|
| Agent spawning | `../shared/references/agent-spawning.md` | Worktree creation, agent spawning, context budgeting, result contract, bounded retries, cleanup, wave-based execution |
| State persistence | `../shared/references/state-persistence.md` | State issue lifecycle, reading/writing session state |
| Projects format | `../shared/references/projects-format.md` | Project item schema, custom fields, status values, scoring via jq |
| gh CLI patterns | `../shared/references/gh-cli-patterns.md` | Authentication, repo detection, project operations, error handling |
| Output conventions | `../shared/references/output-conventions.md` | Status indicators, table formats, summary blocks |
| Implementation workflow | `../shared/references/implementation-workflow.md` | Repo prep, worktree mgmt, branch/commit/push/PR, agent result contract, pre-flight, content filter |
| Config | `../shared/references/config.md` | Scoring constants and display thresholds |
| Sync format | `../shared/references/sync-format.md` | Sync metadata contract (synced issue fields) |
| Item categories | `../shared/references/item-categories.md` | Item classification (Category A/B/CI) and routing rules |
| Edge cases | `../shared/references/edge-cases.md` | Rate limiting, content filters, permission errors, bounded retries |
| Agent result contract | `../shared/references/agent-result-contract.md` | Universal agent response format |

The user must have **write access** to the target repository — required for pushing branches and creating PRs. The `project` scope must be authorized on the gh CLI token.
</context>

<objective>
Apply fixes to Todo project items and create PRs for file changes.

Outputs:
- PRs created on GitHub for each Category B/CI item
- API settings applied for Category A items
- Project items moved from Todo → Done (status updated via built-in Status field)
- PR URL written to the `PR URL` custom field on each resolved item
- State issue updated with session comment and score change
- `[GHS Score]` project item updated with new health score
- Terminal report with results table and per-wave progress

Next routing:
- Suggest `ghs-merge-prs` to merge the created PRs — "To merge: `/ghs-merge-prs {owner}/{repo}`"
- Suggest `ghs-backlog-board` to see updated dashboard
- Suggest `ghs-repo-scan` to re-scan and verify all fixes
</objective>

<required_reading>
- Read project items via `gh project item-list` before any operation
- Check state issue for blockers and previous session context
</required_reading>

<process>

## Input

Two invocation modes:

- **Single item**: A project item reference — title, slug, or description
  - Health: `{owner}/{repo} [Health] LICENSE`
  - Issue: `{owner}/{repo} issue #42`

- **Batch (repo)**: A repo identifier like `phmatray/Formidable`
  - Discovers all Todo items in the `[GHS] {owner}/{repo}` project with `Source = Health Check`
  - Processes them in waves using worktree-based agents

### Dry-Run Mode
When `--dry-run` is present in $ARGUMENTS:
- Show the execution plan (items, waves, agents) but do not spawn agents
- Show what PRs/issues would be created but do not create them
- Display the dry-run indicator box from ui-brand.md
- Exit after the plan display

## Item Categories

See `../shared/references/item-categories.md` for the full classification table (Category A/B/CI) and routing rules. Issue items are always Category B.

## Phase 1 — Read State & Discover Items

### Read State Issue

Per `../shared/references/state-persistence.md` § Reading State:

```bash
# 1. Find state issue
STATE_ISSUE=$(gh issue list --repo {owner}/{repo} --label "ghs:state" --state open \
  --json number,body --limit 1)

# 2. Parse the JSON from the HTML comment in the body
#    Extract active blockers → skip blocked items in plan
#    Extract decisions → apply user preferences (merge method, skip list)
#    Extract last session comment → show "Last activity: {date} — {summary}"
gh issue view {state_number} --repo {owner}/{repo} \
  --json comments --jq '.comments | sort_by(.createdAt) | reverse | .[0:1]'
```

### Single-item mode

Look up the project item by title/slug in the `[GHS] {owner}/{repo}` project:

```bash
# Find project number
PROJECT_NUM=$(gh project list --owner {owner} --format json \
  --jq '.projects[] | select(.title == "[GHS] {owner}/{repo}") | .number')

# List items and filter by title or slug
gh project item-list $PROJECT_NUM --owner {owner} --format json --limit 500 \
  | jq '.items[] | select(.title == "[Health] {Check Name}")'
```

Determine the item's category from its `Category` custom field. Skip if the item's Status is already `Done`. Skip if the state issue has an active blocker for this item's slug (unless user explicitly asks to retry).

If the item is a linked GitHub issue (Source = `GitHub Issue`):
1. Fetch latest state: `gh issue view {number} --json state,body --repo {owner}/{repo}`
2. If the issue is closed and the check passes → skip
3. If the issue is closed but item is still Todo → warn the user, process anyway
4. Store the issue number for agent prompts (Phase 6)

### Batch mode

Query the project for all Todo health items:

```bash
PROJECT_NUM=$(gh project list --owner {owner} --format json \
  --jq '.projects[] | select(.title == "[GHS] {owner}/{repo}") | .number')

ITEMS=$(gh project item-list $PROJECT_NUM --owner {owner} --format json --limit 500)

# Filter to actionable items: Source = Health Check, Status = Todo
echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .status == "Todo")]'
```

For each item in the filtered list:

1. Extract slug, tier, points, category from the item's custom fields
2. Skip items with active blockers in the state issue (unless user insists)
3. Classify each item into Category A, B, or CI based on its `Category` field
4. For linked GitHub issues (Source = `GitHub Issue`), fetch issue state and store the number for agent prompts

For detailed fix strategies per check, determine the module from the item's `Module` field:
- Core items: read `../shared/checks/core/index.md` for the Slug-to-Path Lookup, then `../shared/checks/core/{category}/{slug}.md`
- .NET items: read `../shared/checks/dotnet/index.md` for the Slug-to-Path Lookup, then `../shared/checks/dotnet/{category}/{slug}.md`

See `../shared/references/item-categories.md` for module-specific category routing (core vs .NET).

## Phase 2 — Build Dependency Graph

Per `../shared/references/agent-spawning.md` § Wave-Based Execution:

### Known Dependencies

| Item | Depends On | Reason |
|------|-----------|--------|
| ci-workflow-health | editorconfig, gitignore | Workflows may reference these files |
| action-version-pinning | ci-cd-workflows | Must have workflows to pin actions in |
| workflow-permissions | ci-cd-workflows | Must have workflows to set permissions on |
| workflow-naming | ci-cd-workflows | Must have workflows to rename |
| workflow-timeouts | ci-cd-workflows | Must have workflows to set timeouts on |
| workflow-concurrency | ci-cd-workflows | Must have workflows to set concurrency on |
| contributing-md | license, readme | Contributing guide links to these files |
| codeowners | — (but needs team/user context) | References teams/users that must exist |
| branch-protection (status checks) | ci-cd-workflows | Status checks require passing workflows |

### Wave Construction Algorithm

```
1. For each item in the batch:
   a. Look up dependencies from the table above
   b. If any dependency is also in the batch and hasn't been assigned → item must wait
   c. If all dependencies are already Done or not in the batch → assign to Wave 1
2. Items with no dependencies → Wave 1
3. Items whose dependencies are all in Wave 1 → Wave 2
4. Repeat until all items assigned
5. Items with circular dependencies → flag as NEEDS_HUMAN
```

### Flat vs Wave Decision

If the dependency graph has no edges (all items independent), use flat parallel execution — a single wave. This is the common case and preserves backward compatibility with v8.0 behavior.

Category A items are always in Wave 1 (API-only, no dependencies on file changes).

## Phase 3 — Prepare Repository

Follow `../shared/references/implementation-workflow.md` §1 to clone or pull the repo and detect the default branch and tech stack.

See `../shared/references/agent-spawning.md` (Repository Cloning section) for the clone/pull pattern.

## Phase 4 — Show Plan & Confirm

Display a summary table organized by waves:

```
## Batch Plan: {owner}/{repo}

### Wave 1 ({n} items — independent)
| # | Item | Tier | Pts | Category | Issue | Branch | Worktree |
|---|------|------|-----|----------|-------|--------|----------|
| 1 | [Health] LICENSE | T1 | 4 | B (file) | #42 | fix/license | repos/{o}_{r}--worktrees/fix--license/ |
| 2 | [Health] Branch Protection | T1 | 4 | A (API) | — | — | — |
| 3 | [Health] .editorconfig | T2 | 2 | B (file) | — | fix/editorconfig | repos/{o}_{r}--worktrees/fix--editorconfig/ |

### Wave 2 ({n} items — depends on Wave 1)
| # | Item | Tier | Pts | Category | Depends On | Branch | Worktree |
|---|------|------|-----|----------|-----------|--------|----------|
| 4 | [Health] Contributing Guide | T2 | 2 | B (file) | LICENSE, README | fix/contributing-md | repos/.../ |
| 5 | [Health] CI Workflow Health | T2 | 2 | CI | .editorconfig | fix/ci-workflow-health | repos/.../ |

{If blocked items:}
### Blocked ({n} items — active blockers in state issue)
| # | Item | Blocker | Notes |
|---|------|---------|-------|
| 6 | [Health] Branch Protection | No admin access | Needs org admin |

Total items: {N} ({cat_a} API-only, {cat_b} file changes, {cat_ci} CI)
Waves: {n_waves}
Points recoverable: {total_points}
Blocked: {n_blocked} (skipped)

Proceed with all? (y/n/select)
```

For single-item mode, show a simpler plan (no waves needed):

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

Per `../shared/references/implementation-workflow.md` §5 — check for branch conflicts and existing PRs. Flag any conflicts in the plan table.

See `../shared/references/agent-spawning.md` (Pre-flight Checks section) for the exact commands.

## Phase 5 — Create Worktrees (Wave 1)

Create worktrees only for the current wave's Category B/CI items:

| Step | Command | Notes |
|------|---------|-------|
| 1. Create worktree dir | `mkdir -p repos/{owner}_{repo}--worktrees` | Sibling to main clone, never nested inside |
| 2. Add worktree | `git -C repos/{owner}_{repo} worktree add ../repos/{owner}_{repo}--worktrees/{prefix}--{slug} -b {prefix}/{slug}` | One worktree per Category B/CI item |
| 3. Verify creation | `ls repos/{owner}_{repo}--worktrees/{prefix}--{slug}/.git` | Confirm worktree is valid |

Category A items don't need worktrees — they use `gh` API commands directly.

## Phase 6 — Execute Wave

Spawn all agents for the current wave in a **single Task tool message** for parallel execution. Each agent gets a self-contained prompt and returns structured JSON per `../shared/references/implementation-workflow.md` §4.

Read the agent prompt templates and substitute placeholders:
- `agents/category-a-agent.md` — for Category A items (one agent handles all)
- `agents/category-b-agent.md` — for each Category B item (one agent per item)
- `agents/category-ci-agent.md` — for Category CI items

For issue items, use the Category B agent pattern but adapt the prompt:
- Read the full issue from GitHub: `gh issue view {number} --repo {owner}/{repo}`
- Include "Fixes #{number}" in the commit message and PR body

For items with synced issues (from `ghs-backlog-sync`):
- Category B agents: Include the `GitHub Issue: #{github_issue}` block from the agent template
- Category A agent: Include the `Synced Issue: #{number}` block

All agents use `subagent_type: general-purpose`.

### After Wave Completes

1. Parse JSON results per `../shared/references/agent-spawning.md` § Agent Result Contract
2. Apply circuit breaker for FAILED items (retry up to 3 total attempts)
3. Move successful project items from Todo → Done via the built-in Status field:
   ```bash
   # Get project/item/field IDs, then update Status to Done option
   gh project item-edit --project-id {project_node_id} --id {item_node_id} \
     --field-id {status_field_id} --single-select-option-id {done_option_id}
   ```
4. Set the `PR URL` custom field on each resolved item:
   ```bash
   gh project item-edit --project-id {project_node_id} --id {item_node_id} \
     --field-id {pr_url_field_id} --text "{pr_url}"
   ```
5. Recalculate health score via jq pipeline (see `../shared/references/projects-format.md` § Scoring via jq):
   ```bash
   ITEMS=$(gh project item-list $PROJECT_NUM --owner {owner} --format json --limit 500)
   EARNED=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and .status == "Done") | .points] | add // 0')
   POSSIBLE=$(echo "$ITEMS" | jq '[.items[] | select(.source == "Health Check" and (.status == "Todo" or .status == "Done")) | .points] | add // 0')
   SCORE=$(echo "scale=0; $EARNED * 100 / $POSSIBLE" | bc)
   ```
6. Report wave progress:

```
Wave 1 complete: {n_pass}/{n_total} passed
  Points recovered: {points} | Score: {old}% → {new}% (+{delta})
```

7. Clean up worktrees for PASS and FAILED items in this wave
8. Check Wave 2 dependencies — skip items whose dependencies failed (mark as BLOCKED)

## Phase 7 — Execute Remaining Waves

Repeat Phase 5-6 for each subsequent wave:

```
For wave_n in 2..N:
  1. Check dependencies — skip items whose deps failed
  2. Create worktrees for this wave's B/CI items
  3. Spawn agents in single Task message (parallel within wave)
  4. Collect results, apply circuit breaker
  5. Update project item statuses (Todo → Done) and PR URL fields
  6. Recalculate score via jq, report progress
  7. Clean up worktrees
```

Items with failed dependencies are marked BLOCKED (not FAILED) — they didn't fail on their own merits. The report distinguishes these from actual failures.

## Phase 8 — Write State & Final Report

### Write State Issue

Per `../shared/references/state-persistence.md` § Writing State:

Find or create the state issue, then append a session comment:

```bash
# Find or create state issue
STATE_ISSUE_NUM=$(gh issue list --repo {owner}/{repo} --label "ghs:state" --state open \
  --json number --limit 1 --jq '.[0].number // empty')

if [ -z "$STATE_ISSUE_NUM" ]; then
  gh label create "ghs:state" --color "1d76db" --description "GHS session state tracking" \
    --repo {owner}/{repo} 2>&1 || true
  STATE_ISSUE_NUM=$(gh issue create --repo {owner}/{repo} \
    --title "[GHS State] {owner}/{repo}" \
    --label "ghs:state" \
    --body "{initial_body}" \
    --json number --jq '.number')
fi

# Append session comment
gh issue comment $STATE_ISSUE_NUM --repo {owner}/{repo} --body "$(cat <<'EOF'
## {YYYY-MM-DD} — ghs-backlog-fix ({single|batch})

**Items attempted**: {N}
**Results**: {pass} PASS, {fail} FAILED, {human} NEEDS_HUMAN, {blocked} BLOCKED

| Item | Wave | Status | PR | Notes |
|------|------|--------|-----|-------|
| {slug} | {wave_n} | {status} | {pr_url or —} | {brief note} |

**Score change**: {before}% → {after}% ({delta})
EOF
)"
```

Record any new blockers (permissions, content filters) and decisions (skip patterns, merge preferences) by updating the issue body's JSON block.

### Update [GHS Score] Project Item

Update the `[GHS Score]` draft item's `Score` field and body with the new health score:

```bash
# Find [GHS Score] item node ID
SCORE_ITEM_ID=$(gh project item-list $PROJECT_NUM --owner {owner} --format json --limit 500 \
  | jq -r '.items[] | select(.title == "[GHS Score]") | .id')

# Update Score field
gh project item-edit --project-id {project_node_id} --id $SCORE_ITEM_ID \
  --field-id {score_field_id} --number {new_score}

# Update body with new JSON breakdown
gh project item-edit --project-id {project_node_id} --id $SCORE_ITEM_ID \
  --field-id {body_field_id} --text "{updated_score_json}"
```

### Final Report

```
## Results: {owner}/{repo}

| Item | Wave | Tier | Pts | Status | PR |
|------|------|------|-----|--------|----|
| [Health] LICENSE | 1 | T1 | 4 | [PASS] | #12 |
| [Health] Branch Protection | 1 | T1 | 4 | [PASS] | — (API) |
| [Health] .editorconfig | 1 | T2 | 2 | [PASS] | #13 |
| [Health] Contributing Guide | 2 | T2 | 2 | [PASS] | #14 |
| [Health] CI Workflow Health | 2 | T2 | 2 | [BLOCKED] | — |

---

Summary:
  Applied: {n_pass}/{n_total}
  PRs created: {n_prs}
  Points recovered: {points_recovered}/{points_possible}
  Waves executed: {n_waves}

  Score progression:
    Wave 1: {score_after_w1}% (+{delta_w1})
    Wave 2: {score_after_w2}% (+{delta_w2})
    Final:  {final_score}% (was {original_score}%)

{If any FAILED, BLOCKED, or NEEDS_HUMAN items:}
Remaining items:
  [FAILED] CI Workflow Health — {error}
  [BLOCKED] Contributing Guide — depends on README (FAILED in Wave 1)
  [NEEDS_HUMAN] ... — worktree at ...
```

### PR Template Fields

| Field | Value | Notes |
|-------|-------|-------|
| Title | `fix({slug}): {short description}` | Conventional commit style |
| Base | `{default_branch}` | Always target default branch |
| Head | `{prefix}/{slug}` | Branch created in worktree |
| Body | Description + acceptance criteria + `Fixes #{number}` | Include issue ref for auto-close |
| Labels | `ghs:auto-fix` | Identifies PRs created by this skill |

### Verification Checklist

Before creating a PR, every agent must verify:

| Check | How |
|-------|-----|
| Files match acceptance criteria | Diff review — only expected files changed |
| No unrelated modifications | `git diff --stat` shows only in-scope files |
| Commit message follows convention | Starts with `fix(`, `feat(`, or `docs(` |
| Tests pass (if applicable) | Run test command from tech stack detection |
| PR body includes issue reference | Contains `Fixes #{number}` when synced issue exists |

### Goal-Backward Verification

| Level | Check | Method |
|-------|-------|--------|
| Existence | Output artifact exists | File/PR/API response check |
| Substance | Contains correct content | Diff review, body inspection |
| Wiring | Properly connected | Correct branch target, auto-close refs |

</process>

## Single-Item Fast Path

When a single project item reference is provided:

1. Read state issue — check for blockers on this item's slug
2. Look up the item in `[GHS] {owner}/{repo}` project by title/slug, extract custom field values
3. Classify as Category A, B, or CI from the `Category` field
4. Clone/pull repo (Phase 3)
5. Show single-item plan, get `y/n` (Phase 4)
6. **Category A**: run the `gh` command directly in the orchestrator — no agent needed for a single API call
7. **Category B/CI**: create one worktree, spawn one agent
8. Move project item to Done, set PR URL field, write state issue comment, cleanup worktree, report

## Edge Cases

- **Already Done**: Skip the item. In batch mode, exclude from the plan table.
- **Already closed issues**: Update the linked project item Status to Done and skip.
- **Active blocker in state issue**: Skip the item with a note. Suggest resolving the blocker first.
- **Branch already exists remotely**: Flag in plan table. If user confirms, force-create the branch (`-B` flag on worktree add).
- **Agent failure**: One agent failing doesn't block others in the same wave. Mark the item FAILED in the report.
- **Dependency failure**: If a Wave 1 item fails and a Wave 2 item depends on it, mark the Wave 2 item as BLOCKED (not FAILED).
- **NEEDS_HUMAN**: Worktree left in place with instructions. Not cleaned up.
- **Re-running is safe**: Phase 1 skips already-Done items. Idempotent.
- **WARN items**: These indicate permission issues. Before applying, check if the user now has sufficient permissions. If not, record as blocker in state issue.
- **Complex issues**: If an issue seems too complex to auto-fix, present a plan and let the user guide the implementation.
- **Merge conflicts**: If a worktree branch has conflicts, report and let the user decide.
- **PR already exists for branch**: Check with `gh pr list --head fix/{slug}` before creating a new one.
- **Content filtering blocks agent output**: The orchestrator detects content filter failures and retries with a download-based approach. See `../shared/references/edge-cases.md` for the workaround pattern.
- **All items independent (no dependencies)**: Falls back to flat parallel execution — single wave, same as v8.0 behavior. No overhead from wave construction.
- **project scope missing**: Pre-flight check catches missing project scope. Instruct user: `gh auth refresh -s project`.

## Examples

**Example 1: Apply a single health item**
User says: "apply the LICENSE health item for phmatray/Formidable"
Result: Read state issue -> look up `[Health] LICENSE` in `[GHS] phmatray/Formidable` project -> parse item (Category B) -> clone/pull repo -> show plan -> create one worktree -> spawn one agent -> agent generates LICENSE file -> commits, pushes, creates PR -> orchestrator verifies -> moves project item to Done, sets PR URL field -> writes state issue comment -> cleans up worktree.

**Example 2: Apply all items with dependencies (wave execution)**
User says: "apply all for phmatray/Formidable"
Result: Read state issue -> query `[GHS] phmatray/Formidable` for Todo Health Check items -> find 8 items -> classify (2 Cat A, 5 Cat B, 1 Cat CI) -> build dependency graph (contributing-md depends on license, ci-workflow-health depends on editorconfig) -> assign waves:
- Wave 1 (6 items): license, readme, editorconfig, gitignore + 2 API items → parallel execution → score 45% → 72%
- Wave 2 (2 items): contributing-md, ci-workflow-health → parallel execution → score 72% → 85%
- Write state issue comment with full session log → Final report with score progression.

**Example 3: Blocked items from previous session**
User says: "apply all for phmatray/Formidable"
Result: Read state issue -> finds active blocker "No admin access" on branch-protection -> skips branch-protection in plan -> shows "1 blocked item" -> processes remaining items -> reports blocker in final output.

**Example 4: Apply an issue fix**
User says: "fix issue #42 for phmatray/Formidable"
Result: Read state issue -> look up issue item in project (Source = GitHub Issue) -> fetch full issue body from GitHub -> create worktree -> spawn agent -> agent implements fix with "Fixes #42" in commit -> creates PR -> moves project item to Done, sets PR URL field -> writes state issue comment.

## Troubleshooting

**Item status is already Done**
The fix has already been applied. The skill will skip it and tell you.

**"Permission denied" when pushing branch**
You need write access to the repository. Check `gh repo view --json viewerPermission`.

**Worktree creation fails**
If the branch already exists locally: `git -C repos/{owner}_{repo} branch -D fix/{slug}` then retry.
If it exists remotely: use `-B` flag to force-create, or ask user.

**Agent returns NEEDS_HUMAN**
The fix requires human judgment. The worktree is left in place — `cd` into it and make changes manually, then push and create a PR.

**PR creation fails**
Common causes: branch already exists remotely (skill checks for this in Phase 4), or default branch is protected. Check `gh pr list --head fix/{slug}` for existing PRs.

**Worktrees not cleaned up**
Run `git -C repos/{owner}_{repo} worktree list` to see active worktrees. Remove with `git worktree remove <path>`.

**Wave 2 items all BLOCKED**
This means Wave 1 dependencies failed. Fix the Wave 1 items first (check the error), then re-run. The state issue will show what failed and why.

**project scope missing**
Run `gh auth refresh -s project` to add the project scope to your token.
