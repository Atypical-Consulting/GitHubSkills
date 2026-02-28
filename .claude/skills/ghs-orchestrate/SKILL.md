---
name: ghs-orchestrate
description: >
  Run a full maintenance pipeline across repositories — update, scan, fix, review, merge, sync,
  and optionally release. Chains existing ghs-skills in sequence with human checkpoints before
  destructive stages, state issue-based resume, and dry-run mode.
  Use this skill whenever the user wants to orchestrate a pipeline, maintain repos end-to-end,
  or says things like "orchestrate", "run pipeline", "maintain my repos", "full pipeline",
  "scan and fix all repos", "process all repos", "pipeline for {repo}", "run all skills",
  "maintenance run", "end-to-end maintenance", or "run the full workflow".
  Do NOT use for single skill invocations — use the individual skill directly.
argument-hint: "[owner/repo...] [--stages pull,scan,fix,review,merge,sync,release] [--dry-run] [--resume]"
allowed-tools: "Bash(gh:*) Bash(git:*) Read Write Edit Glob Grep Skill"
compatibility: "Requires gh CLI (authenticated), git, all ghs-skills available, GSD framework (for fix stage)"
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

# Multi-Repo Pipeline Orchestrator

Chain existing ghs-skills into a full maintenance pipeline across one or many repositories. Manages the lifecycle: update repos, scan for issues, apply fixes, review PRs, merge, sync to GitHub, and optionally cut releases. Resumes from interruption via the state issue.

<context>
<execution_context>
References:
- ../shared/references/gh-cli-patterns.md
- ../shared/references/output-conventions.md
- ../shared/references/ui-brand.md
- ../shared/references/argument-parsing.md
- ../shared/references/state-persistence.md
- ../shared/references/checkpoint-patterns.md
- ../shared/references/agent-spawning.md
- ../shared/references/config.md
- ../shared/references/scoring-logic.md
</execution_context>

Purpose: Orchestrate existing ghs-skills into a sequential pipeline for end-to-end repository maintenance. This skill **only orchestrates** — it never directly modifies code, creates PRs, or calls the GitHub API for mutations. Every action is delegated to the appropriate skill via the Skill tool.

Roles:
1. **Orchestrator** (you) — parses input, validates pre-flight, tracks per-repo stage progress, invokes skills, enforces human checkpoints, writes state issue comments, produces the summary dashboard

### Pipeline Diagram

```
  pull ──> scan ──> fix ──> review ──> merge ──> sync ──> release
  (1)      (2)      (3)     (4)        (5)       (6)      (7)
                     ^                   ^                   ^
                 checkpoint          checkpoint          checkpoint
```

Stages 3, 5, and 7 are destructive and require human confirmation unless `--no-checkpoint` is set.

### Shared References

| Reference | Path | Use For |
|-----------|------|---------|
| gh CLI patterns | `../shared/references/gh-cli-patterns.md` | Authentication check, repo detection, error handling |
| Output conventions | `../shared/references/output-conventions.md` | Status indicators, table formats, routing suggestions |
| GSD integration | `../shared/references/gsd-integration.md` | GSD detection (fix stage depends on GSD for complex items) |
| State persistence | `../shared/references/state-persistence.md` | State issue lifecycle (GitHub Issues), resume from interruption |
| GitHub Projects format | `../shared/references/projects-format.md` | Project naming, discovery, score record, state record |
</context>

<anti-patterns>

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Run fix without scanning first | Always run scan before fix — stale backlog leads to wasted work | Backlog items may be outdated; scan refreshes the state |
| Merge without reviewing | Always run review before merge (unless user explicitly skips) | Unreviewed merges bypass quality gates |
| Skip human checkpoints on destructive stages | Pause for confirmation before fix, merge, and release | Destructive actions are hard to reverse — user must opt in |
| Process repos in parallel | Process repos **sequentially** — one repo completes its pipeline before the next starts | Parallel repo processing causes gh CLI rate limiting and confusing interleaved output |
| Continue pipeline if scan finds zero items | Skip fix/review/merge/sync stages — report "nothing to fix" and move to next repo | Running fix on an empty backlog wastes time and produces confusing output |
| Release without merging first | Complete merge stage before release — unmerged PRs mean the release tag misses changes | A release from a branch with open PRs produces an incomplete release |
| Re-scan a repo that was just scanned | Check state issue for recent scan — if < 1 hour old, skip pull+scan unless user forces | Re-scanning wastes API quota and time; use cached results |
| Ignore state issue resume data | Always read state issue at start — offer resume if a previous run was interrupted | Users expect to pick up where they left off, not restart from scratch |

</anti-patterns>

## Scope Boundary

This skill **only orchestrates** — it delegates all work to existing skills. It never:
- Directly modifies code files
- Creates PRs or branches
- Calls `gh` for mutations (issues, labels, PRs)
- Runs tests or linters

The sole writes this skill performs are:
1. Reading/writing state issue comments for orchestration progress
2. Terminal output (dashboards, progress updates)
3. Invoking other skills via the Skill tool

### Cognitive Bias Guards

| Bias | Antidote |
|------|----------|
| Sunk cost | If a repo is stuck mid-pipeline (3+ stages blocked), skip it rather than forcing through |
| Completion bias | Do not skip checkpoints to "finish faster" — each checkpoint exists for a reason |
| Automation bias | Do not trust scan results blindly — if scan reports 0 items on a known-problematic repo, flag it |
| Anchoring | Do not assume all repos need all stages — check actual state before proceeding |

<objective>
Orchestrate a complete maintenance pipeline across one or many repositories by chaining existing skills.

Outputs:
- Per-repo stage completion dashboard (terminal)
- State issue comment with orchestration session entry per repo
- Summary table showing all repos and their final status

Next routing:
- Suggest `ghs-backlog-board` to see the updated dashboard — "To view results: `/ghs-backlog-board`"
</objective>

<required_reading>
Read state issue for resume context and previous pipeline progress.
</required_reading>

<process>

## Input

### Invocation Modes

| Mode | Trigger | Example |
|------|---------|---------|
| Multi-repo (all) | "orchestrate", "run pipeline", "maintain my repos", "process all repos" | Processes all repos with `[GHS]` projects |
| Multi-repo (list) | "pipeline for repo1, repo2" | Processes specified repos only |
| Single-repo | "pipeline for {owner}/{repo}", "run pipeline on phmatray/Formidable" | Full pipeline for one repo |
| Partial pipeline | `--from {stage} --to {stage}` | Only run stages in the specified range |

### Flags

| Flag | Default | Effect |
|------|---------|--------|
| `--dry-run` | off | Show what would happen without executing any skills |
| `--release` | off | Include the release stage (opt-in) |
| `--no-checkpoint` | off | Skip human confirmation before destructive stages |
| `--from {stage}` | `pull` | Start pipeline at this stage |
| `--to {stage}` | `sync` (or `release` if `--release`) | Stop pipeline after this stage |

### Rule/Trigger/Example Triples

**Rule:** Multi-repo mode processes all repos with existing `[GHS]` projects.
**Trigger:** User says "maintain my repos" or "run pipeline".
**Example:** Discover `[GHS] phmatray/Formidable` and `[GHS] phmatray/OtherRepo` projects -> process each sequentially through the full pipeline.

**Rule:** Partial pipeline skips stages outside the specified range.
**Trigger:** User says "run pipeline --from scan --to merge".
**Example:** Skip pull stage, start at scan, run through fix, review, merge, stop before sync/release.

**Rule:** Dry-run shows the plan without executing.
**Trigger:** User says "orchestrate --dry-run".
**Example:** Display the pipeline plan for all repos, show which stages would run, then stop.

**Rule:** Resume from interruption uses the state issue.
**Trigger:** State issue shows a previous orchestration session with incomplete stages.
**Example:** "Previous run interrupted at fix stage for phmatray/Formidable. Resume from fix? (y/n/fresh)"

## Pipeline Stage Table

| Stage | Skill | Destructive? | Checkpoint? | Skippable? | Notes |
|-------|-------|-------------|-------------|------------|-------|
| pull | ghs-repos-pull | No | No | Yes (`--from scan`) | Updates all local clones |
| scan | ghs-repo-scan | No | No | No (required) | Produces/refreshes backlog |
| fix | ghs-backlog-fix | Yes (creates PRs) | Yes | Yes | Wave-based parallel agents |
| review | ghs-review-pr | No | No | Yes | Review created PRs |
| merge | ghs-merge-prs | Yes (merges PRs) | Yes | Yes | Merge approved PRs |
| sync | ghs-backlog-sync | No | No | Yes | Sync remaining findings to GitHub Issues |
| release | ghs-release | Yes (creates tag) | Yes | Yes (opt-in via `--release`) | Cut a release |

### Dry-Run Mode
When `--dry-run` is present in $ARGUMENTS:
- Run pull and scan stages normally (read-only)
- Show fix, merge, sync, release plans without executing
- Display the dry-run indicator box from ui-brand.md
- Useful for previewing what a full pipeline would do

## Phase 1 — Input Parsing

Parse the user's request to determine:

1. **Repo list**: All repos with `[GHS]` projects, a specified list, or a single repo
2. **Stage range**: `--from` and `--to` (default: `pull` through `sync`)
3. **Flags**: `--dry-run`, `--release`, `--no-checkpoint`

### Repo Discovery

```bash
# List all GHS-audited repos via their GitHub Projects
gh project list --owner {owner} --format json \
  --jq '.projects[] | select(.title | startswith("[GHS]"))'
```

Each project title follows the pattern `[GHS] {owner}/{repo}`. Extract `{owner}/{repo}` for skill invocations.

If no `[GHS]` projects exist, stop with a helpful message:

```
[WARN] No [GHS] projects found. Run a scan first:

  /ghs-repo-scan {owner}/{repo}
```

## Phase 2 — Pre-flight Checks

Verify all prerequisites before starting the pipeline:

| Check | Command | On Failure |
|-------|---------|------------|
| gh authenticated | `gh auth status` | Stop — "Run `gh auth login` first" |
| git available | `git --version` | Stop — "git is required" |
| Repo list valid | `gh project list --owner {owner}` to confirm project exists for each repo | Warn and skip repos with no `[GHS]` project |
| Skills available | Verify each required skill file exists | Warn about missing skills, skip their stages |

### Skill Availability Check

For each stage in the pipeline range, verify the skill file exists:

| Stage | Skill File |
|-------|-----------|
| pull | `.claude/skills/ghs-repos-pull/SKILL.md` |
| scan | `.claude/skills/ghs-repo-scan/SKILL.md` |
| fix | `.claude/skills/ghs-backlog-fix/SKILL.md` |
| review | `.claude/skills/ghs-review-pr/SKILL.md` |
| merge | `.claude/skills/ghs-merge-prs/SKILL.md` |
| sync | `.claude/skills/ghs-backlog-sync/SKILL.md` |
| release | `.claude/skills/ghs-release/SKILL.md` |

If a skill file is missing, skip that stage with a warning — do not fail the entire pipeline.

### Archived Repo Detection

```bash
gh repo view {owner}/{repo} --json isArchived -q '.isArchived'
```

If archived, skip fix, merge, and release stages (read-only stages still apply).

## Phase 3 — Load/Create Orchestration State

### Read State Issue

For each repo, read the state issue (per `../shared/references/state-persistence.md` § Reading State):

```bash
gh issue list --repo {owner}/{repo} --label "ghs:state" --state open \
  --json number,title,body --limit 1
```

1. Check for a previous orchestration session entry (in issue comments)
2. If found and incomplete (stages not all DONE), offer to resume:

```
Previous orchestration run detected for {owner}/{repo}:
  Started: {timestamp}
  Completed stages: pull, scan
  Next stage: fix

Resume from fix? (y/resume/fresh)
  y/resume — continue from where it left off
  fresh — start a new run from the beginning
```

3. Extract active blockers — repos with unresolvable blockers are flagged
4. Extract decisions — apply user preferences (merge method, skip patterns)

### Initialize Orchestration Tracking

Build an in-memory tracking table:

```
| Repo | pull | scan | fix | review | merge | sync | release | Status |
```

All stages start as `PENDING`. Stages outside the `--from`/`--to` range are marked `SKIPPED`.

## Phase 4 — Show Plan & Confirm

Display the pipeline plan before execution:

```
## Pipeline Plan: {mode}

Mode: {multi-repo | single-repo}
Stages: {from} -> {to}
Flags: {--dry-run, --release, --no-checkpoint, or "none"}
Repos: {count}

| # | Repo | Health | Open Items | Archived? | Resume From | Notes |
|---|------|--------|-----------|-----------|-------------|-------|
| 1 | owner/repo1 | 45% | 8 FAIL | No | — | — |
| 2 | owner/repo2 | 72% | 3 FAIL | No | fix | Resuming previous run |
| 3 | owner/repo3 | — | — | Yes | — | Archived — skip fix/merge/release |

Stages to execute: pull -> scan -> fix -> review -> merge -> sync
Checkpoints: fix (confirm), merge (confirm)
{If --release:} Release: enabled (checkpoint before release)

Proceed? (y/n)
```

If `--dry-run`, show the plan and stop — do not execute any stages.

Wait for user confirmation before continuing.

## Phase 5 — Execute Pipeline (Per Repo)

Process each repo sequentially through the pipeline stages. For each repo:

### Stage Execution Pattern

For each stage in the pipeline range:

```
1. Check if stage is applicable (e.g., skip fix if scan found 0 items)
2. If checkpoint stage and --no-checkpoint is NOT set:
   a. Show checkpoint prompt with context
   b. Wait for user confirmation (y/n/skip)
   c. If skip → mark stage SKIPPED, continue to next stage
3. Invoke the skill via Skill tool
4. Record result in tracking table
5. If stage failed → mark repo as BLOCKED, skip remaining stages for this repo
6. Update dashboard display
```

### Stage Invocations

Each stage invokes its corresponding skill. The orchestrator passes the repo identifier and any relevant flags:

| Stage | Skill Invocation | Context Passed |
|-------|-----------------|----------------|
| pull | `/ghs-repos-pull` | (no args — pulls all) |
| scan | `/ghs-repo-scan {owner}/{repo}` | Repo identifier |
| fix | `/ghs-backlog-fix {owner}/{repo}` | Repo identifier (batch mode) |
| review | `/ghs-review-pr {owner}/{repo}` | Repo identifier |
| merge | `/ghs-merge-prs {owner}/{repo}` | Repo identifier |
| sync | `/ghs-backlog-sync {owner}/{repo}` | Repo identifier |
| release | `/ghs-release {owner}/{repo}` | Repo identifier |

### Checkpoint Prompts

Before destructive stages, show context and ask for confirmation:

**Fix checkpoint:**
```
## Checkpoint: Fix Stage — {owner}/{repo}

Scan found {N} items to fix ({n_t1} Tier 1, {n_t2} Tier 2, {n_t3} Tier 3)
Points recoverable: {points}
This will create PRs on the repository.

Proceed with fix? (y/n/skip)
```

**Merge checkpoint:**
```
## Checkpoint: Merge Stage — {owner}/{repo}

{N} PRs ready to merge ({n_approved} approved, {n_pending} pending review)
This will merge PRs and delete branches.

Proceed with merge? (y/n/skip)
```

**Release checkpoint:**
```
## Checkpoint: Release Stage — {owner}/{repo}

All PRs merged. Ready to cut a release.
This will create a git tag and GitHub release.

Proceed with release? (y/n/skip)
```

### Stage Result Handling

| Result | Action |
|--------|--------|
| Stage succeeded | Mark DONE in tracking table, continue to next stage |
| Stage completed with warnings | Mark DONE with note, continue to next stage |
| Stage failed | Mark FAILED, record error, skip remaining stages for this repo |
| Stage skipped (0 items) | Mark SKIPPED with reason ("0 items to fix"), continue to next stage |
| User skipped at checkpoint | Mark SKIPPED with reason ("user skipped"), continue to next stage |

### Early Exit Conditions

| Condition | Action |
|-----------|--------|
| Scan finds 0 FAIL items | Skip fix, review, merge — report "nothing to fix" |
| Fix creates 0 PRs | Skip review, merge — report "no PRs created" |
| No PRs to merge | Skip merge — report "no PRs to merge" |
| Repo is archived | Skip fix, merge, release — read-only stages only |
| All remaining repos are BLOCKED | Stop pipeline — report blocked repos |

### Dashboard Update

After each stage completes, display the updated tracking table:

```
## Pipeline: Multi-Repo Maintenance

| Repo | pull | scan | fix | review | merge | sync | Status |
|------|------|------|-----|--------|-------|------|--------|
| owner/repo1 | [PASS] | [PASS] | [PASS] 3 PRs | [PASS] | Checkpoint... | — | In Progress |
| owner/repo2 | [PASS] | [PASS] | — (0 items) | — | — | — | Complete |
| owner/repo3 | [PASS] | [FAIL] | — | — | — | — | Blocked |
```

## Phase 6 — Write State & Summary

### Write State Issue Comment (Per Repo)

Per `../shared/references/state-persistence.md` § Writing State, append an orchestration session comment to each repo's state issue:

```bash
gh issue comment {state_number} --repo {owner}/{repo} --body "$(cat <<'EOF'
## {YYYY-MM-DD} — ghs-orchestrate ({single|multi}-repo)
EOF
)"
```

```markdown
### {YYYY-MM-DD} — ghs-orchestrate ({single|multi}-repo)

**Pipeline**: {from} -> {to}
**Flags**: {flags or "none"}

| Stage | Status | Notes |
|-------|--------|-------|
| pull | DONE | — |
| scan | DONE | 8 FAIL items found |
| fix | DONE | 5/8 items fixed, 3 PRs created |
| review | DONE | 3/3 PRs approved |
| merge | DONE | 3/3 PRs merged |
| sync | DONE | 3 remaining items synced |
| release | SKIPPED | Not requested |

**Score change**: 45% -> 82% (+37)
```

Record any new blockers (rate limits, permission errors) and decisions discovered during the run.

### Final Summary Dashboard

```
## Pipeline Complete

| # | Repo | pull | scan | fix | review | merge | sync | release | Score |
|---|------|------|------|-----|--------|-------|------|---------|-------|
| 1 | owner/repo1 | [PASS] | [PASS] | [PASS] 3 PRs | [PASS] | [PASS] | [PASS] | — | 45% -> 82% |
| 2 | owner/repo2 | [PASS] | [PASS] | — (0 items) | — | — | [PASS] | — | 91% (no change) |
| 3 | owner/repo3 | [PASS] | [FAIL] | — | — | — | — | — | — (scan failed) |

---

Summary:
  Repos processed: {n_total}
  Fully completed: {n_complete}
  Partially completed: {n_partial}
  Blocked: {n_blocked}

  Stages executed: {total_stages}
  PRs created: {n_prs}
  PRs merged: {n_merged}

  {If any blocked repos:}
  Blocked repos:
    owner/repo3 — scan failed: {error}

  To view updated dashboard: /ghs-backlog-board
```

</process>

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No `[GHS]` projects found | Stop with message suggesting `ghs-repo-scan` first |
| Repo is archived | Skip fix/merge/release stages; run scan and sync only |
| Rate limiting mid-pipeline | Pause, report to user, record in state issue, suggest resuming later |
| Skill not available (file missing) | Skip that stage with `[WARN]`, continue pipeline |
| State issue exists from previous run | Offer resume or fresh start before proceeding |
| Pipeline interrupted (Ctrl+C, context limit) | State issue enables resume — next run detects incomplete stages |
| All items already fixed (scan finds 0 FAIL) | Skip fix/review/merge, report "nothing to fix", continue to sync |
| Scan fails for a repo | Mark repo as BLOCKED, continue to next repo |
| Fix stage creates 0 PRs (all API-only fixes) | Skip review/merge, continue to sync |
| User declines checkpoint | Mark stage as SKIPPED, continue to next stage |
| `--no-checkpoint` on destructive stages | Execute without pausing — user accepted the risk via the flag |
| Mixed archived and active repos | Process each according to its archive status |
| Single stage pipeline (`--from merge --to merge`) | Only run merge for each repo, skip everything else |
| Repo not yet scanned (no `[GHS]` project) | Run scan first regardless of `--from` flag — scan is always required |

## Good and Bad Examples

### Good Pipeline Output

```
## Pipeline: Multi-Repo Maintenance

Mode: multi-repo (2 repos)
Stages: pull -> scan -> fix -> merge -> sync

| Repo | pull | scan | fix | review | merge | sync | Status |
|------|------|------|-----|--------|-------|------|--------|
| phmatray/Formidable | [PASS] | [PASS] 8 items | [PASS] 5 fixed, 3 PRs | [PASS] | [PASS] 3 merged | [PASS] | Complete |
| phmatray/OtherRepo | [PASS] | [PASS] 0 items | — (nothing to fix) | — | — | [PASS] | Complete |

Summary:
  Repos processed: 2
  Fully completed: 2
  PRs created: 3
  PRs merged: 3

  Score changes:
    phmatray/Formidable: 45% -> 82% (+37)
    phmatray/OtherRepo: 91% (no change)
```

### Bad Pipeline Output

```
Running pipeline...
Done with repo1.
Done with repo2.
All done!
```

The bad example lacks per-stage visibility, score tracking, item counts, and structured formatting. Users cannot tell what happened at each stage or what changed.

## Examples

**Example 1: Full pipeline on all repos**
User: "maintain my repos"
Flow: Discover `[GHS]` projects -> pre-flight checks -> show plan -> pull all -> for each repo: scan, checkpoint+fix, review, checkpoint+merge, sync -> write state issue comment per repo -> final dashboard.

**Example 2: Single repo with release**
User: "pipeline for phmatray/Formidable --release"
Flow: Pre-flight -> show plan (1 repo, 7 stages) -> pull -> scan -> checkpoint+fix -> review -> checkpoint+merge -> sync -> checkpoint+release -> state issue comment -> summary.

**Example 3: Partial pipeline (scan and fix only)**
User: "run pipeline --from scan --to fix"
Flow: Skip pull -> scan each repo -> checkpoint+fix -> stop after fix -> state issue comment -> summary.

**Example 4: Dry run**
User: "orchestrate --dry-run"
Flow: Discover repos via `[GHS]` projects -> pre-flight -> show plan with all stages and expected actions -> stop without executing.

**Example 5: Resume interrupted pipeline**
User: "run pipeline" (state issue shows previous run stopped at fix stage)
Flow: Read state issue -> "Previous run interrupted at fix for phmatray/Formidable. Resume? (y/fresh)" -> user says y -> skip pull and scan -> start at fix -> continue through remaining stages.

**Example 6: All items already fixed**
User: "maintain my repos"
Flow: Pull -> scan phmatray/Formidable (0 FAIL items) -> skip fix/review/merge -> sync -> report "nothing to fix, repo is healthy at 95%".
