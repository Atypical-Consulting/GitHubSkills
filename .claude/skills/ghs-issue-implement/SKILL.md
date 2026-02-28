---
name: ghs-issue-implement
description: >
  Implement a GitHub issue using worktree-based agents, then create a PR. Clones the repo, creates
  a worktree, spawns an agent to implement the fix/feature, verifies the result, and opens a PR
  with auto-close references. For complex issues (High/Very High complexity from ghs-issue-analyze),
  automatically uses GSD framework for multi-phase planning and execution with wave-based
  parallelization, fresh context per task, and automated verification.
  Use this skill whenever the user wants to implement an issue, fix
  a bug from an issue, build a feature from an issue, or says things like "implement issue #42",
  "fix issue #42", "implement #42", "build feature from issue #15", "implement all triaged issues",
  "implement all bugs", "work on issue #42", or "code issue #42".
  Do NOT use for triaging/labeling issues (use ghs-issue-triage), analyzing issues
  (use ghs-issue-analyze), applying backlog health items (use ghs-backlog-fix), or scanning
  repos (use ghs-repo-scan).
allowed-tools: "Bash(gh:*) Bash(git:*) Read Write Edit Glob Grep Task Skill"
compatibility: "Requires gh CLI (authenticated), git, GSD framework (for complex issues), network access"
license: MIT
metadata:
  author: phmatray
  version: 5.0.0
routes-to:
  - ghs-merge-prs
routes-from:
  - ghs-issue-triage
  - ghs-issue-analyze
  - ghs-backlog-board
---

# Issue Implementation

Implement GitHub issues using parallel worktree-based agents. For simple issues, spawns a single agent per issue. For complex issues, invokes GSD's full planning and execution pipeline — discuss, plan, execute, verify — with wave-based parallelization and fresh context per task.

<context>
Purpose: Implement GitHub issues and create PRs. Routes through either the **fast path** (single-shot agent) or the **GSD path** (multi-phase pipeline) based on issue complexity.

### Shared References

| Reference | Path | Use For |
|-----------|------|---------|
| Agent spawning | `../shared/references/agent-spawning.md` | Worktree creation, agent spawning, context budgeting, result contract, bounded retries, cleanup, wave-based execution |
| GSD integration | `../shared/references/gsd-integration.md` | GSD detection, complexity routing, command patterns, skill-to-GSD contract, error handling |
| State persistence | `../shared/references/state-persistence.md` | State issue lifecycle, reading/writing session state via GitHub Issues |
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
| Force GSD on simple issues | Use complexity routing — Low/Medium go fast path, High/Very High go GSD | GSD overhead isn't justified for a typo fix or single-file change |
| Skip state issue check at start | Read state issue for active blockers and previous attempts | Re-trying known-blocked items wastes time and confuses users |

</anti-patterns>

## Scope Boundary

Only implement what the issue describes. If the agent discovers adjacent problems (outdated deps, missing tests for unrelated code, style inconsistencies), it must **not** fix them inline. Instead, note them in the PR body under a "Discovered Issues" section so they can be filed separately.

## Complexity Routing

Every issue goes through a routing decision before execution. See `../shared/references/gsd-integration.md` § Complexity Routing for the full decision matrix.

### Decision Flow

```
1. Check state issue for active blockers on this issue
2. Fetch issue details + analysis comment (if any)
3. Determine complexity:
   a. Analysis comment exists → use its Complexity field
   b. No analysis → estimate from issue body signals
4. Route:
   - Low/Medium → Fast Path (Phase 5a)
   - High/Very High → GSD Path (Phase 5b)
   - User override → respect explicit request
```

### Complexity Signals (when no analysis exists)

| Signal | Points Toward |
|--------|--------------|
| Single file mentioned | Fast path |
| "typo", "fix", "update" in title | Fast path |
| 1-2 acceptance criteria | Fast path |
| 4+ files mentioned | GSD path |
| "refactor", "migration", "redesign" | GSD path |
| Sub-task checklist in body | GSD path |
| Multiple modules/subsystems affected | GSD path |
| Architectural decision required | GSD path |

When ambiguous, default to fast path. The user can always re-run with `/gsd:quick` or ask for the GSD path explicitly.

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
| State issue active blockers (for this issue only) | Full state issue contents |

<objective>
Implement GitHub issues and create PRs with auto-close references.

Outputs:
- PRs created on GitHub for each implemented issue
- Labels updated on implemented issues (`status:in-progress`)
- Terminal report with implementation results
- State issue updated with session comment
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
**Example:** Fetch #42 (type:bug) -> assess complexity -> route to fast or GSD path -> implement -> PR.

**Rule:** "all" + a label keyword resolves to batch mode.
**Trigger:** User says "implement all triaged issues" or "implement all bugs".
**Example:** Fetch all matching issues, assess each issue's complexity, group by path (fast vs GSD), execute in parallel within each group.

**Rule:** User can force a specific path.
**Trigger:** User says "use GSD for #42" or "just quick-fix #42".
**Example:** Override complexity routing and use the requested path regardless of signals.

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

### Phase 1 — Read State & Fetch Issues

**Read state issue** (per `../shared/references/state-persistence.md` § Reading State):

```bash
gh issue list --repo {owner}/{repo} --label "ghs:state" --state open
# Then read the most recent state issue:
gh issue view {state_issue_number} --repo {owner}/{repo} --json body,comments
```

```
1. Fetch open state issue via gh issue list (label: ghs:state)
2. Extract active blockers from issue comments → flag blocked issues in plan
3. Extract decisions → apply user preferences
4. Show "Last activity: {date} — {summary}" if recent
```

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

### Phase 2 — Assess Complexity & Route

For each issue, determine the execution path:

```
1. Check for analysis comment → extract Complexity field
2. If no analysis, estimate from issue body signals (see Complexity Signals table)
3. Check for user override ("use GSD", "quick fix")
4. Assign path: FAST or GSD
```

**Display routing decision in plan:**

| # | Issue | Type | Priority | Complexity | Path | Branch |
|---|-------|------|----------|------------|------|--------|
| 1 | #42 Login crashes | bug | high | Low | FAST | fix/42-login-crash |
| 2 | #15 Add auth system | feature | medium | High | GSD | feat/15-add-auth |
| 3 | #18 Update README | docs | low | Low | FAST | docs/18-update-readme |

### Phase 3 — Prepare Repository

Per `../shared/references/agent-spawning.md` § Repository Cloning:

1. Clone or pull the repo to `repos/{owner}_{repo}/`
2. Detect default branch
3. Detect tech stack (language, framework, test runner, linter)

### Phase 4 — Show Plan & Confirm

**Batch plan:**

```
## Implementation Plan: {owner}/{repo}

| # | Issue | Type | Priority | Path | Branch | Has Analysis? |
|---|-------|------|----------|------|--------|---------------|
| 1 | #42 Login crashes | bug | high | FAST | fix/42-login-crash | Yes |
| 2 | #15 Add auth system | feature | medium | GSD | feat/15-add-auth | Yes (High) |
| 3 | #18 Update README | docs | low | FAST | docs/18-update-readme | No |

Total: {N} issues ({n_fast} fast path, {n_gsd} GSD path)
{If blockers:} Blocked: {n_blocked} issues (active blockers in state issue)

Proceed with all? (y/n/select)
```

**Single issue plan:**

```
## Plan: #{number} — {title}

Repository: {owner}/{repo}
Type:       {type_label}
Priority:   {priority_label}
Complexity: {Low|Medium|High|Very High}
Path:       {FAST — single agent | GSD — multi-phase pipeline}
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

### Phase 5a — Fast Path Execution (Low/Medium Complexity)

Create worktrees and spawn agents as before — this is the existing v4.0 behavior.

Per `../shared/references/agent-spawning.md` § Worktree Creation:

```bash
mkdir -p repos/{owner}_{repo}--worktrees

git -C repos/{owner}_{repo} worktree add \
  ../repos/{owner}_{repo}--worktrees/{prefix}--{number}-{slug} \
  -b {prefix}/{number}-{slug}
```

Spawn all fast-path agents in a **single Task tool message** using `subagent_type: general-purpose`. See `../shared/references/agent-spawning.md` § Parallel Execution Pattern.

Read `agents/implementation-agent.md` for the prompt template. Substitute: `{owner}`, `{repo}`, `{default_branch}`, `{detected_stack}`, `{prefix}`, `{number}`, `{slug}`, `{title}`, `{body}`, and optionally `{analysis_comment_content}`.

### Phase 5b — GSD Path Execution (High/Very High Complexity)

For each GSD-routed issue, follow `../shared/references/gsd-integration.md` § Implementation Flow:

**Step 1: GSD Pre-flight**

Check GSD is installed per `../shared/references/gsd-integration.md` § GSD Detection. If not found, fail fast with install instructions.

**Step 2: Prepare GSD Context**

Create a worktree for the issue (same as fast path), then set up GSD's `.planning/` directory inside it:

```bash
mkdir -p repos/{owner}_{repo}--worktrees/{prefix}--{number}-{slug}/.planning
```

Write `.planning/PROJECT.md` with the issue context:

```markdown
# {repo} — Issue #{number}: {title}

## Project Context
- **Repository**: {owner}/{repo}
- **Tech Stack**: {detected_stack}
- **Default Branch**: {default_branch}

## Issue Details
{Full issue body}

## Analysis (from ghs-issue-analyze)
{Analysis comment content, if available}

## Acceptance Criteria
{Extracted from issue body as checklist}
```

Write `.planning/REQUIREMENTS.md` with extracted acceptance criteria.

**Step 3: Execute GSD Pipeline**

Run GSD commands in sequence from within the worktree directory. The orchestrator invokes these via the Skill tool:

1. `/gsd:discuss-phase 1` — captures implementation preferences. If running in batch mode, skip discussion (use analysis comment as context instead)
2. `/gsd:plan-phase 1` — creates atomic task plans with verification commands
3. `/gsd:execute-phase 1` — wave-based execution with fresh context per task, atomic commits
4. `/gsd:verify-work 1` — walks through acceptance criteria, spawns debug agents for failures

**Step 4: Post-GSD Handoff**

After GSD completes:

1. Read `.planning/1-VERIFICATION.md` for pass/fail results
2. If verification passed → push branch and create PR (orchestrator responsibility)
3. If verification failed → check if GSD generated fix plans. If yes, re-execute. If no, mark NEEDS_HUMAN
4. Map GSD results to the standard agent result contract:

```json
{
  "source": "issue",
  "slug": "{number}-{short-slug}",
  "status": "PASS|FAILED|NEEDS_HUMAN",
  "pr_url": null,
  "verification": ["extracted from VERIFICATION.md"],
  "error": "extracted from state issue blockers or null"
}
```

**Batch GSD execution:** When multiple issues are routed to GSD, execute them sequentially (not in parallel) — each GSD pipeline is already internally parallelized and uses significant context. Running multiple GSD pipelines simultaneously would exhaust resources.

### Phase 6 — Collect Results & Update Labels

After all agents (fast path) and GSD pipelines complete, parse results per `../shared/references/agent-spawning.md` § Agent Result Contract.

**On success (PASS):**

```bash
gh issue edit {number} --repo {owner}/{repo} \
  --remove-label "status:triaged,status:analyzing" \
  --add-label "status:in-progress"
```

**On failure:** Apply the circuit breaker (up to 3 attempts for fast path). GSD handles retries internally.

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
- For GSD path: `.planning/` artifacts are inside the worktree and get cleaned automatically

### Phase 8 — Write State & Final Report

**Write state issue** (per `../shared/references/state-persistence.md` § Writing State):

Post a session comment to the open state issue via `gh issue comment`:

```bash
gh issue comment {state_issue_number} --repo {owner}/{repo} --body "$(cat <<'EOF'
### {YYYY-MM-DD} — ghs-issue-implement ({single|batch})

**Items attempted**: {N}
**Results**: {pass} PASS, {fail} FAILED, {human} NEEDS_HUMAN

| Item | Complexity | Path | Status | PR | Notes |
|------|-----------|------|--------|-----|-------|
| #{number} {title} | {level} | {FAST|GSD} | {status} | {pr_url or —} | {brief note} |
EOF
)"
```

If no state issue exists yet, create one first:

```bash
gh issue create --repo {owner}/{repo} --label "ghs:state" \
  --title "ghs state: {owner}/{repo}" \
  --body "Session state tracking issue for ghs skills."
```

Record any new blockers or decisions discovered during execution as additional comment content.

**Final Report:**

```
## Results: {owner}/{repo}

| # | Issue | Type | Path | Status | PR |
|---|-------|------|------|--------|----|
| #42 | Login crashes | bug | FAST | [PASS] | #101 |
| #15 | Add auth system | feature | GSD | [PASS] | #102 |
| #18 | Update README | docs | FAST | [NEEDS_HUMAN] | — |

---

Summary:
  Implemented: {n_pass}/{n_total}
  PRs created: {n_prs}
  By path: {n_fast} fast, {n_gsd} GSD
  By type: {n_bug} bugs, {n_feature} features, {n_docs} docs

{If any NEEDS_HUMAN:}
Remaining:
  [NEEDS_HUMAN] #18 Update README — worktree at repos/{o}_{r}--worktrees/docs--18-update-readme/
    Reason: Unclear what sections to update — needs user guidance
```

**Routing suggestion:** `To merge created PRs: /ghs-merge-prs {owner}/{repo}`

### Verification Checklist

Before marking any issue as PASS, the agent (or GSD) must confirm:

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

## Implementation Path
{FAST — single agent | GSD — multi-phase (N tasks, N commits)}

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
| Issue too complex for fast path | Agent sets `NEEDS_HUMAN`; suggest re-running with GSD |
| GSD not installed | Fail fast with install instructions for GSD-routed issues |
| GSD plan fails validation 3 times | Mark NEEDS_HUMAN; preserve worktree with `.planning/` artifacts |
| GSD verification finds failures | GSD generates fix plans; orchestrator re-executes or escalates |
| Agent failure (fast path) | One failure doesn't block others; mark `FAILED` in report |
| Content filter blocks output | Retry with download-based approach (see `../shared/references/edge-cases.md`) |
| Issue has no analysis | Agent investigates on its own (fast path) or GSD researches (GSD path) |
| Re-running on existing items | Issues with `status:in-progress` + open PR are skipped in batch |
| Active blocker in state issue | Skip the issue; report blocker in plan |
| Mixed batch (fast + GSD) | Execute fast-path issues in parallel first, then GSD issues sequentially |

## Examples

**Example 1: Single bug fix (fast path)**
User: "implement issue #42"
Flow: Read state issue -> fetch #42 (type:bug, complexity:Low) -> route to FAST -> show plan -> create worktree `fix--42-login-crash` -> agent fixes bug with tests -> commit with `Fixes #42` -> create PR -> update label -> write state issue comment -> cleanup -> report with `[PASS]`.

**Example 2: Complex feature (GSD path)**
User: "implement #15" (analysis says complexity:High)
Flow: Read state issue -> fetch #15 (type:feature, complexity:High) -> route to GSD -> show plan -> create worktree -> prepare `.planning/PROJECT.md` -> `/gsd:discuss-phase 1` -> `/gsd:plan-phase 1` -> `/gsd:execute-phase 1` (3 tasks, 3 atomic commits) -> `/gsd:verify-work 1` (4/4 criteria pass) -> push branch -> create PR -> update label -> write state issue comment -> cleanup -> report.

**Example 3: Batch with mixed complexity**
User: "implement all triaged issues"
Flow: Read state issue -> fetch 5 triaged issues -> assess complexity (3 Low, 1 Medium, 1 High) -> show plan with paths -> user confirms -> fast-path: 4 issues in parallel (worktrees + agents) -> GSD path: 1 issue sequentially -> collect all results -> update labels -> write state issue comment -> cleanup -> report.

**Example 4: User forces GSD on a simple issue**
User: "use GSD for issue #42"
Flow: Same as Example 2 but skipping complexity assessment — user override wins.
