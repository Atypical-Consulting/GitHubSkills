---
name: ghs-dev-loop
description: >
  Act as an autonomous developer for a repository — monitor for new/triaged issues, process them
  through the full development lifecycle (triage, analyze, implement, review, merge), handle health
  maintenance, dependency updates, and optional releases. Operates in cycles with human checkpoints
  for safety. Use this skill whenever the user wants a full developer loop, says things like
  "dev loop", "be my developer", "autonomous developer", "work on my repo", "process all issues",
  "developer mode", "full dev loop", "maintain this repo", "handle everything", "automate development",
  "dev cycle", "work through issues", "run a dev cycle", "be my dev", or "take over this repo".
  Do NOT use for single-skill operations — use the individual skill directly.
  Do NOT use for multi-repo pipelines — use ghs-orchestrate instead.
allowed-tools: "Bash(gh:*) Bash(git:*) Read Write Edit Glob Grep Skill"
compatibility: "Requires gh CLI (authenticated), git, all ghs-skills, GSD framework"
license: MIT
metadata:
  author: phmatray
  version: 2.0.0
routes-to:
  - ghs-backlog-board
routes-from:
  - ghs-backlog-board
  - ghs-backlog-next
---

# Full Developer Loop

Act as an autonomous developer for a single repository. Process work in priority-driven cycles: health maintenance, issue triage/analysis/implementation, code review, PR merging, dependency updates, and optional releases. Each cycle enforces human checkpoints for irreversible operations.

<context>
Purpose: Replace a human developer for a single repository by orchestrating the full suite of ghs-skills in priority order, operating in budget-constrained cycles with safety checkpoints.

### Roles

1. **Developer** (you) — orchestrates existing skills, manages the priority queue, enforces checkpoints, tracks progress via state issue
2. **Human** (the user) — approves checkpoints, overrides priorities, provides context when needed

This skill **only orchestrates** via the Skill tool — it never directly modifies code, creates branches, or pushes commits. All mutations flow through the chained skills.

### Shared References

| Reference | Path | Use For |
|-----------|------|---------|
| gh CLI patterns | `../shared/references/gh-cli-patterns.md` | Authentication, repo detection, error handling |
| Output conventions | `../shared/references/output-conventions.md` | Status indicators, table formats, summary blocks |
| GSD integration | `../shared/references/gsd-integration.md` | GSD detection, complexity routing, command patterns |
| State persistence | `../shared/references/state-persistence.md` | State issue lifecycle (GitHub Issues), reading/writing session state |
| GitHub Projects format | `../shared/references/projects-format.md` | Project naming, discovery, score record, state record |
| Agent spawning | `../shared/references/agent-spawning.md` | Worktree patterns, context budgets, circuit breakers |

### Skill Dependency Map

```
ghs-dev-loop
  |
  +-- Health Maintenance
  |     +-- /ghs-repo-scan        (scan health)
  |     +-- /ghs-backlog-fix      (apply fixes)
  |     +-- /ghs-merge-prs        (merge fix PRs)
  |
  +-- Issue Processing
  |     +-- /ghs-issue-triage     (label new issues)
  |     +-- /ghs-issue-analyze    (deep analysis)
  |     +-- /ghs-issue-implement  (code + PR)
  |     +-- /ghs-review-pr        (review PRs)
  |     +-- /ghs-merge-prs        (merge approved PRs)
  |
  +-- Dependency Management
  |     +-- /ghs-merge-prs --renovate  (bot PRs)
  |
  +-- Release (optional)
        +-- /ghs-release          (draft/publish)
```

### Cycle Diagram

```
  Start
    |
    v
  [Load State Issue]
    |
    v
  [Check Health Score] ---> Score < threshold? ---> [Health Maintenance]
    |                                                     |
    | (score OK)                                          v
    v                                             [Merge fix PRs]
  [Triage unlabeled issues]                               |
    |                                                     |
    v                                                     |
  [Process issues by priority] <--------------------------+
    |
    | For each issue (up to budget):
    |   [Analyze] -> [Implement] -> [Review PR] -> [Merge]
    |
    v
  [Merge Renovate/bot PRs]
    |
    v
  [Release decision] ---> threshold met? ---> [Draft release + checkpoint]
    |
    v
  [Cycle summary report]
    |
    v
  [Update State Issue]
    |
    v
  [Next cycle decision]
```
</context>

<anti-patterns>

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Process unlimited issues in one cycle | Enforce issue budget (default: 5 per cycle) | Unbounded processing drains API quota, creates PR avalanches, and overwhelms reviewers |
| Skip health maintenance when score is below threshold | Always run health fixes before issue processing | A degraded repo (missing CI, no tests) produces broken implementations |
| Implement without analyzing first | Run `/ghs-issue-analyze` before `/ghs-issue-implement` for every issue | Skipping analysis leads to incomplete implementations, wrong scope, and missed edge cases |
| Merge without reviewing | Run `/ghs-review-pr` before `/ghs-merge-prs` for implementation PRs | Unreviewed code erodes quality and may introduce regressions |
| Release without merging all pending PRs | Merge or defer all open PRs before creating a release | A release with unmerged PRs creates version confusion and partial features |
| Re-process issues that already have open PRs or branches | Check for existing PRs/branches before processing; skip if found | Re-implementing wastes time and creates conflicting PRs |
| Start continuous mode without explicit user consent | Require the user to explicitly say "continuous" or "keep going" | Autonomous loops without consent can drain API quota and create unwanted changes |
| Ignore state issue from a previous session | Read state issue first; offer resume or fresh start | Ignoring previous state re-processes items, re-encounters known blockers, and loses decisions |
| Process issues assigned to other users | Skip issues with assignees (unless assigned to the authenticated user) | Implementing someone else's assigned work causes ownership conflicts |
| Bypass checkpoints even in continuous mode | Always pause at non-disableable checkpoints (High+ implementation, release) | Irreversible operations need human sign-off regardless of automation mode |
| Modify code directly | Delegate all code changes to chained skills via the Skill tool | This skill is an orchestrator — direct code changes bypass verification and review |
| Process all issue types equally | Respect priority queue: critical bugs before features before docs | Equal treatment means a typo fix blocks a production crash |

</anti-patterns>

## Scope Boundary

This skill **orchestrates only** — it never directly modifies code, creates branches, or pushes commits. All mutations flow through existing skills:

| Action | Delegated To |
|--------|-------------|
| Scanning health | `/ghs-repo-scan` |
| Fixing health items | `/ghs-backlog-fix` |
| Triaging issues | `/ghs-issue-triage` |
| Analyzing issues | `/ghs-issue-analyze` |
| Implementing issues | `/ghs-issue-implement` |
| Reviewing PRs | `/ghs-review-pr` |
| Merging PRs | `/ghs-merge-prs` |
| Creating releases | `/ghs-release` |

The sole write actions of ghs-dev-loop itself are:
1. Reading and writing state issue (session tracking)
2. Terminal output (cycle reports)

## Context Budget

What state to carry between cycle stages:

| Carry Forward | Do NOT Carry |
|---------------|-------------|
| Health score (before/after) | Full scan output (re-scan if needed) |
| Issue list with priorities and statuses | Issue body details (re-fetch per skill) |
| PR numbers created this cycle | Subagent prompts and intermediate results |
| Blocker list from state issue | Previous session history (only current blockers matter) |
| Cycle budget counters (issues processed, failures) | Worktree paths (managed by downstream skills) |
| Checkpoint decisions (user approvals) | GSD internal state (managed by GSD) |

## Circuit Breaker

| Condition | Action |
|-----------|--------|
| 3 failed implementations in one cycle | Stop issue processing; report failures; suggest manual review |
| Health scan fails | Skip health maintenance; proceed to issues with a warning |
| Rate limit detected | Pause cycle; report remaining budget; offer resume |
| Skill invocation fails 3 times consecutively | Stop cycle; preserve state issue; report error |

<objective>
Operate as an autonomous developer for one repository, processing work in priority-driven cycles.

Outputs per cycle:
- Cycle report with health delta, issues processed, PRs created/merged
- State issue updated with session entry, decisions, blockers
- Terminal summary with next-cycle recommendation

Next routing:
- After single cycle: "To view dashboard: `/ghs-backlog-board`"
- After continuous run: "All cycles complete. Dashboard: `/ghs-backlog-board`"
</objective>

## Priority Queue

| Priority | Category | Trigger | Action |
|----------|----------|---------|--------|
| P0 | Health critical | Health score < 50% | `/ghs-repo-scan` + `/ghs-backlog-fix` (all tiers) immediately |
| P1 | Critical bugs | `priority:critical` label | `/ghs-issue-analyze` + `/ghs-issue-implement` |
| P2 | Health maintenance | Health score < 80% | `/ghs-backlog-fix` (Tier 1 + Tier 2 items) |
| P3 | High-priority issues | `priority:high` label | `/ghs-issue-analyze` + `/ghs-issue-implement` |
| P4 | Normal issues | `priority:medium`, `priority:low`, or unlabeled | `/ghs-issue-triage` + `/ghs-issue-analyze` + `/ghs-issue-implement` |
| P5 | Dependencies | Renovate/bot PRs pending | `/ghs-review-pr` + `/ghs-merge-prs --renovate` |
| P6 | Release | Configured threshold met and `--auto-release` flag | `/ghs-release --draft` + checkpoint |

## Cycle Modes

| Mode | Behavior | Budget | Use When |
|------|----------|--------|----------|
| `single` | Run one cycle, then stop | 5 issues (default) | Manual invocation, testing |
| `continuous` | Repeat cycles until no work remains | 5 issues per cycle | Batch processing backlog |
| `watch` | Poll for new issues at interval, run cycle when found | 5 issues per poll | Long-running maintenance |

### Rule/Trigger/Example Triples

**Rule:** Default to `single` mode unless the user explicitly requests otherwise.
**Trigger:** User says "dev loop on my repo" without specifying a mode.
**Example:** Run one cycle with default budget of 5 issues, report results, stop.

**Rule:** `continuous` mode requires explicit user consent.
**Trigger:** User says "keep going", "continuous mode", or "process everything".
**Example:** Run cycles until the priority queue is empty or budget is exhausted per cycle, pausing at checkpoints.

**Rule:** `watch` mode requires a polling interval.
**Trigger:** User says "watch my repo" or "monitor for new issues".
**Example:** Check for new issues every 5 minutes (configurable), run a cycle when new issues are found.

**Rule:** Budget applies per cycle, not across cycles.
**Trigger:** In continuous mode, each cycle processes up to 5 issues independently.
**Example:** Cycle 1 processes 5 issues, cycle 2 processes 3 remaining issues, cycle 3 finds 0 issues and stops.

## Checkpoint Configuration

| Gate | Default | Can Disable? | Why Default On |
|------|---------|-------------|----------------|
| Before health fix | ON | Yes (`--no-checkpoint`) | Fixes create PRs — user should review the plan |
| Before implement (High+) | ON | No | Complex changes need human sign-off |
| Before merge | ON | Yes (`--auto-merge`) | Merging is irreversible |
| Before release | ON | No | Releases are public and versioned |

### Checkpoint Behavior

When a checkpoint is reached:

1. Display a summary of what will happen
2. Ask the user to approve, reject, or modify
3. If rejected: skip the action, record the decision in state issue, continue to next priority
4. If modified: apply the user's adjustments (e.g., "skip issue #15, do the rest")

In `continuous` and `watch` modes, checkpoints still pause execution — they are never auto-approved.

<process>

## Input

### Invocation Patterns

| Trigger | Mode | Budget | Flags |
|---------|------|--------|-------|
| "dev loop on owner/repo" | single | 5 | — |
| "be my developer for owner/repo" | single | 5 | — |
| "dev loop --continuous owner/repo" | continuous | 5/cycle | — |
| "process all issues on owner/repo" | continuous | 5/cycle | — |
| "maintain this repo --auto-merge" | single | 5 | auto-merge |
| "dev cycle --budget 10 owner/repo" | single | 10 | — |
| "watch my repo every 10m" | watch | 5/poll | interval=10m |
| "dev loop --auto-release owner/repo" | single | 5 | auto-release |

### Flag Reference

| Flag | Default | Effect |
|------|---------|--------|
| `--budget N` | 5 | Max issues to process per cycle |
| `--continuous` | off | Repeat cycles until no work remains |
| `--watch INTERVAL` | off | Poll for new issues at interval |
| `--auto-merge` | off | Skip merge checkpoint (non-High+ PRs only) |
| `--auto-release` | off | Enable release step (still checkpointed) |
| `--no-checkpoint` | off | Disable optional checkpoints (health fix, merge) |
| `--health-threshold N` | 80 | Health score % below which maintenance triggers |
| `--skip-health` | off | Skip health maintenance entirely |
| `--skip-dependencies` | off | Skip Renovate/bot PR merging |

## Phase 1 — Pre-flight

Verify all prerequisites before starting the cycle.

| Check | Command | On Failure |
|-------|---------|------------|
| gh authentication | `gh auth status` | Stop — tell user to run `gh auth login` |
| Repository access | `gh repo view {owner}/{repo} --json name` | Stop — repo not found or no access |
| Write permission | `gh repo view {owner}/{repo} --json viewerPermission` | Stop if read-only — report archived/fork status |
| GSD availability | Check per `../shared/references/gsd-integration.md` § GSD Detection | Warn — High/Very High issues will fail; offer to continue with fast-path only |
| Skill availability | Verify key skills respond | Stop if critical skills are missing |

Detect repository context (per `../shared/references/gh-cli-patterns.md` § Repo Context Detection):
- Default branch name
- Tech stack
- Visibility (public/private)
- Fork status
- Dependency manager (Renovate/Dependabot)

## Phase 2 — Load/Create State Issue

Per `../shared/references/state-persistence.md` § Reading State:

```
1. Query gh issue list --label ghs:state (if exists)
2. Extract active blockers → flag blocked items
3. Extract decisions → apply user preferences
4. Extract last session → offer resume or fresh start
5. If no state issue → create fresh (first cycle for this repo)
```

If state issue shows a previous incomplete cycle:
- Display: "Previous cycle on {date} processed {N} items. {M} issues remain. Resume or start fresh?"
- Wait for user decision

## Phase 3 — Priority Assessment

Gather the full picture of available work:

### 3a. Health Score

```bash
# Check if GitHub Project exists and has a score record
# If no project: run /ghs-repo-scan first
# If project exists: query [GHS Score] item from project
```

| Score | Action |
|-------|--------|
| < 50% | P0 — Critical health. Fix all tiers before any issue work |
| 50%–79% | P2 — Fix Tier 1 + Tier 2 items before normal issues |
| >= 80% | Skip health maintenance this cycle |

### 3b. Issue Inventory

```bash
# Fetch all open issues
gh issue list --repo {owner}/{repo} --state open \
  --json number,title,labels,assignees,createdAt --limit 100
```

Classify each issue:

| Condition | Classification | Priority |
|-----------|---------------|----------|
| Has `priority:critical` | Critical bug | P1 |
| Has `priority:high` | High-priority | P3 |
| Has `priority:medium` or `priority:low` | Normal | P4 |
| No priority label | Needs triage | P4 (triage first) |
| Has assignee (not self) | Assigned elsewhere | SKIP |
| Has open PR linked | Already in progress | SKIP |
| Has `status:in-progress` | Work in progress | SKIP |

### 3c. Dependency PRs

```bash
# Check for Renovate/bot PRs
gh pr list --repo {owner}/{repo} --state open \
  --json number,title,author,headRefName,statusCheckRollup,mergeable \
  --jq '[.[] | select(.author.login == "renovate[bot]" or .author.login == "dependabot[bot]")]'
```

### 3d. Display Priority Queue

```
## Dev Loop: Priority Queue — {owner}/{repo}

  Health Score: {score}% ({status})
  Open Issues: {total} ({critical} critical, {high} high, {normal} normal, {skip} skipped)
  Bot PRs: {n_bot} pending
  Mode: {single|continuous|watch} (budget: {N} issues/cycle)

### Queue

| Priority | Category | Count | Action |
|----------|----------|-------|--------|
| P0 | Health critical | — | Score < 50% — full health fix |
| P1 | Critical bugs | {n} | Analyze + implement |
| P2 | Health maintenance | {n} items | Tier 1 + 2 fixes |
| P3 | High-priority issues | {n} | Analyze + implement |
| P4 | Normal issues | {n} | Triage + analyze + implement |
| P5 | Dependencies | {n} | Review + merge bot PRs |
| P6 | Release | — | {enabled/disabled} |

Proceed with cycle? (y/n/adjust)
```

Wait for user confirmation.

## Phase 4 — Health Maintenance (if needed)

Triggered when health score < threshold (default 80%).

### Step 4a: Scan (if no recent scan)

```
/ghs-repo-scan {owner}/{repo}
```

Only if no backlog exists or the last scan is older than 7 days.

### Step 4b: Fix health items

**Checkpoint** (if enabled): Show fix plan, wait for approval.

```
/ghs-backlog-fix {owner}/{repo}
```

For P0 (< 50%): fix all tiers.
For P2 (50%–79%): fix Tier 1 + Tier 2 items only.

### Step 4c: Merge health fix PRs

```
/ghs-merge-prs {owner}/{repo} --own
```

**Checkpoint** (if merge checkpoint enabled): Confirm before merging.

Record health delta: `{before}% -> {after}%`.

## Phase 5 — Issue Processing

Process issues in priority order, up to the cycle budget.

### For each issue (by priority P1 > P3 > P4):

**Step 5a: Triage (if needed)**

If the issue lacks type/priority labels:

```
/ghs-issue-triage {owner}/{repo} #{number}
```

**Step 5b: Analyze**

```
/ghs-issue-analyze #{number}
```

Extract complexity from the analysis result.

**Step 5c: Implement**

**Checkpoint** (non-disableable for High/Very High complexity): Show analysis summary, wait for approval.

```
/ghs-issue-implement #{number}
```

Track the resulting PR number.

**Step 5d: Review**

```
/ghs-review-pr #{pr_number}
```

**Step 5e: Merge (if review passes)**

**Checkpoint** (if merge checkpoint enabled): Confirm before merging.

```
/ghs-merge-prs {owner}/{repo} --pr #{pr_number}
```

### Budget Tracking

```
Issues processed: {n}/{budget}
Implementations failed: {n}/3 (circuit breaker at 3)
```

If circuit breaker triggers (3 failed implementations):
- Stop issue processing
- Report failures with details
- Proceed to Phase 6 (dependencies)

### Smart Skip Rules

| Condition | Action | Reason |
|-----------|--------|--------|
| Issue has open PR | Skip | Already being worked on |
| Issue has `status:in-progress` label | Skip | Work in progress |
| Issue assigned to another user | Skip | Respect ownership |
| Issue is a pull request | Skip | PRs are reviewed, not implemented |
| Issue is closed | Skip | No work needed |
| Issue blocked in state issue | Skip | Known blocker — report it |
| Issue failed in previous cycle | Skip (unless user retries) | Avoid repeating same failure |

## Phase 6 — Dependency Management

```
/ghs-merge-prs {owner}/{repo} --renovate
```

This handles Renovate and Dependabot PRs. Review is implicit (CI status check).

If `--skip-dependencies` flag is set, skip this phase.

## Phase 7 — Release Decision

Only if `--auto-release` flag is set.

### Release Criteria

| Criterion | Check |
|-----------|-------|
| Changes since last release | `gh release list --limit 1` + compare with HEAD |
| All PRs merged or deferred | No open implementation PRs from this cycle |
| Health score acceptable | Score >= 80% |
| No critical bugs open | No `priority:critical` issues |

If criteria met:

```
/ghs-release {owner}/{repo} --draft
```

**Checkpoint** (non-disableable): Show draft release details, wait for approval before publishing.

If not met, report why and skip.

## Phase 8 — Cycle Summary Report

```
## Dev Loop: Cycle #{n} — {owner}/{repo}

### Health
  Score: {before}% -> {after}% ({delta})
  Fixed: {n} items ({breakdown by tier})
  PRs: {list} ({merged|pending})

### Issues Processed ({n}/{budget})

| # | Issue | Action | Result | PR |
|---|-------|--------|--------|----|
| #12 | Login crash | Implement | [PASS] | #49 (merged) |
| #15 | Dark mode | Implement | [PASS] | #50 (pending review) |
| #18 | Refactor auth | Analyze | Deferred (VeryHigh — checkpoint declined) |

### Dependencies
  Merged: {n} Renovate PRs ({list})
  Skipped: {n} (CI failing)

### Release
  {Released v1.2.0 | Skipped — criteria not met | Not configured}

---

Summary:
  Issues: {processed} processed, {merged} merged, {deferred} deferred, {failed} failed
  Health: {delta} improvement
  PRs created: {n}, PRs merged: {n}
  Next: {remaining} issues remaining, score at {score}%
  Circuit breaker: {n}/3 failures

{If continuous mode:}
  Cycle {n} complete. Starting cycle {n+1}...
{If single mode:}
  Cycle complete. To continue: /ghs-dev-loop --continuous {owner}/{repo}
```

## Phase 9 — State Issue Update

Per `../shared/references/state-persistence.md` § Writing State:

```bash
gh issue comment {state_issue_number} --repo {owner}/{repo} --body "$(cat <<'EOF'
### {YYYY-MM-DD} — ghs-dev-loop (cycle #{n}, {mode})

**Issues processed**: {N}/{budget}
**Health delta**: {before}% -> {after}% ({delta})
**Results**: {pass} PASS, {fail} FAILED, {human} NEEDS_HUMAN, {deferred} DEFERRED

| Item | Type | Action | Status | PR | Notes |
|------|------|--------|--------|----|-------|
| #{number} {title} | issue | implement | PASS | #{pr} | merged |
| {slug} | health | fix | PASS | #{pr} | Tier 1 |

**Dependencies merged**: {n} ({list})
**Release**: {version or skipped}
**Circuit breaker**: {n}/3
EOF
)"
```

Record any new blockers or decisions discovered during the cycle.

## Phase 10 — Next Cycle Decision

| Mode | Decision |
|------|----------|
| `single` | Stop. Report summary. Suggest `/ghs-dev-loop --continuous` if work remains |
| `continuous` | If priority queue is empty -> stop. If work remains -> start Phase 3 again |
| `watch` | Sleep for polling interval. On wake: fetch new issues. If found -> start Phase 3. If not -> sleep again |

</process>

## Cognitive Bias Guards

| Bias | Risk | Antidote |
|------|------|----------|
| Automation bias | "All PRs passed review, so they must be correct" | Review is a signal, not a guarantee. Checkpoints exist for human verification |
| Sunk cost | "We already analyzed 4 issues, let's push through #5 even though it's failing" | Respect the circuit breaker. 3 failures means stop |
| Optimism bias | "This High-complexity issue will probably work on fast path" | Trust the complexity routing. High/VeryHigh = GSD path |
| Anchoring | "The health score is 78%, close enough to 80%" | The threshold is the threshold. < 80% means run health maintenance |
| Completion bias | "Just one more issue before stopping" | Budget is the budget. 5 means 5 |
| Availability bias | "The last issue was easy, so the next one will be too" | Each issue is independent. Re-assess complexity every time |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No issues to process | Report "inbox zero", skip to dependencies/release phase |
| All issues are High/Very High complexity | Respect budget, checkpoint each, defer overflow to next cycle |
| Repository is archived | Read-only mode — scan and report only, no fixes/PRs/merges |
| Issue assigned to someone else | Skip, respect ownership, report in summary |
| Implementation fails 3 times on same issue | Mark NEEDS_HUMAN, activate circuit breaker, continue with dependencies |
| Rate limiting detected | Pause cycle, report remaining budget, offer resume |
| State issue exists from previous cycle | Offer resume or fresh start before proceeding |
| Watch mode — no new issues found | Sleep and re-poll at configured interval |
| User cancels mid-cycle | State issue captures progress for resume in next session |
| Conflicting PRs from different issues | Warn, do not merge both — suggest resolving conflicts first |
| Health scan already recent (< 7 days) | Skip re-scan, use existing project data |
| No GitHub Project exists | Run `/ghs-repo-scan` first to create initial project |
| GSD not available but High-complexity issue found | Warn, offer fast-path fallback or skip |
| User declines a checkpoint | Record decision in state issue, skip that action, continue cycle |
| All checkpoints declined | Cycle completes with no mutations — report "dry run" |
| Continuous mode with recurring failures | Circuit breaker stops issue processing per cycle; failures reset between cycles |

## Examples

### Example 1: Single cycle with health maintenance

User says: "dev loop on phmatray/Formidable"

Flow:
1. Pre-flight: auth OK, repo accessible, GSD available
2. State issue: previous cycle fixed 3 items, score at 65%
3. Priority: score 65% < 80% -> P2 health maintenance, 4 open issues (1 critical, 3 normal)
4. Health: `/ghs-backlog-fix` fixes 3 Tier 1+2 items -> score 82%
5. Merge fix PRs: `/ghs-merge-prs --own` merges 3 PRs
6. Issues: process critical #12 (analyze -> implement -> review -> merge), then 3 normal issues (budget 4/5)
7. Dependencies: merge 2 Renovate PRs
8. Release: not configured -> skip
9. Report: health +17%, 4 issues processed, 6 PRs merged
10. State issue updated, cycle complete

### Example 2: Continuous mode clearing a backlog

User says: "process all issues on phmatray/Formidable --continuous"

Flow:
- Cycle 1: health at 88% (skip), process 5 issues (3 merged, 1 deferred High, 1 failed), merge 1 Renovate PR
- Cycle 2: process 4 remaining issues (2 merged, 1 deferred VeryHigh, 1 NEEDS_HUMAN), no bot PRs
- Cycle 3: 1 deferred VeryHigh issue -> checkpoint -> user approves -> GSD path -> merged
- Cycle 4: 0 issues remaining -> "inbox zero" -> stop
- Report: 4 cycles, 12 issues processed, 9 merged, 2 deferred, 1 NEEDS_HUMAN

### Example 3: Watch mode

User says: "watch my repo every 10m"

Flow:
- Initial cycle: process existing issues (budget 5)
- Sleep 10 minutes
- Wake: check for new issues -> 2 new issues found
- Cycle 2: triage + analyze + implement 2 issues
- Sleep 10 minutes
- Wake: no new issues -> sleep again
- User sends cancel -> state issue updated, stop

### Example 4: Checkpoint declined

User says: "dev loop on my-org/backend"

Flow:
- Health OK (92%), skip maintenance
- Issue #42 (critical bug): analyze -> implement (Low complexity, no checkpoint) -> review -> merge
- Issue #55 (High complexity): analyze -> checkpoint: "Implement #55? Complexity: High, Effort: L" -> user says "skip for now"
- Record decision in state issue: "#55 deferred by user"
- Continue with remaining budget
- Report includes: "#55 — Deferred (user decision at checkpoint)"

### Good Cycle Report

```
## Dev Loop: Cycle #1 — phmatray/Formidable

### Health
  Score: 65% -> 82% (+17%)
  Fixed: 3 items (2 Tier 1, 1 Tier 2)
  PRs: #45, #46, #47 (merged)

### Issues Processed (4/5 budget)

| # | Issue | Action | Result | PR |
|---|-------|--------|--------|----|
| #12 | Login crash | Implement | [PASS] | #49 (merged) |
| #15 | Dark mode toggle | Implement | [PASS] | #50 (merged) |
| #18 | Refactor auth | Analyze | Deferred (VeryHigh — next cycle) |
| #22 | Fix pagination | Implement | [PASS] | #51 (merged) |

### Dependencies
  Merged: 2 Renovate PRs (#41, #43)

---

Summary:
  Issues: 4 processed, 3 merged, 1 deferred
  Health: +17% improvement
  PRs created: 3, PRs merged: 8
  Next: 8 issues remaining, score at 82%
```

### Bad Cycle Report

```
Dev loop done. Fixed some stuff. 3 PRs merged I think. Health went up.
```

(Vague, no numbers, no structure, no actionable next steps.)
