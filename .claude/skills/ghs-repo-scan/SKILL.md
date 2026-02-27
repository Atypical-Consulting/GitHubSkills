---
name: ghs-repo-scan
description: >
  Scans a GitHub repository for quality essentials and open issues, produces a scored report, and
  saves all findings as structured markdown backlog items. Use this skill whenever the user wants to
  check repository quality, audit a repo's setup, see open issues organized as backlog, verify best
  practices are followed, or asks about missing files like README, LICENSE, CODEOWNERS, CI/CD, branch
  protection, templates, security policies, .editorconfig, or failing CI workflows. Also trigger when users say things like "scan my repo",
  "is my repo set up properly", "what's missing from my project", "repo audit", "repo scan",
  "repository checklist", "health check", "what issues are open", "organize my issues",
  "save health report", "export audit results", or "create backlog from audit".
  Do NOT use for managing GitHub Actions workflows, reviewing pull requests, creating repositories, or modifying code.
allowed-tools: "Bash(gh:*) Bash(git:*) Bash(python3:*) Read Write Glob Task"
compatibility: "Requires gh CLI (authenticated), git, python3, network access"
license: MIT
metadata:
  author: phmatray
  version: 6.0.0
routes-to:
  - ghs-backlog-fix
  - ghs-backlog-sync
  - ghs-backlog-board
  - ghs-issue-triage
routes-from:
  - ghs-backlog-board
---

# Repo Scan

Scan a GitHub repository for quality best practices and open issues, display a terminal report, and save all findings as structured markdown backlog items.

## Scope Boundary

This skill ONLY scans and reports. It never modifies the repository, creates PRs, or fixes findings.
Route users to `ghs-backlog-fix` for applying fixes.

## Roles

| Role | Responsibility |
|------|---------------|
| **Orchestrator** (you) | Detect repo, detect stack (modules), spawn agents, collect results, compute scores, write SUMMARY.md, display terminal report |
| **Core Health Check Agents** (3x, spawned via Task) | One per tier — run all core checks in the tier, write backlog items to `health/` |
| **Language Module Agents** (3x per module, spawned via Task) | One per tier per active module — run module checks, write backlog items to `{module}/` |
| **Issues Agent** (1x, spawned via Task) | Fetch open issues, write issue backlog items |

<context>
Purpose: Scan a GitHub repository for quality best practices and open issues, produce a scored report, and save all findings as structured markdown backlog items.

### Shared References

| Reference | Path | Use For |
|-----------|------|---------|
| Scoring logic | `../shared/references/scoring-logic.md` | Score calculation, tier weights, priority algorithm |
| Backlog format | `../shared/references/backlog-format.md` | File naming, metadata, status values |
| Output conventions | `../shared/references/output-conventions.md` | Terminal formatting, progress bars, tables |
| gh CLI patterns | `../shared/references/gh-cli-patterns.md` | Authentication, repo detection, error handling |
| Agent spawning | `../shared/references/agent-spawning.md` | Task tool patterns, result contract, retries |
| Module registry | `../shared/checks/index.md` | Module discovery, stack detection, scoring weights |
| Core checks | `../shared/checks/core/index.md` | Core check registry with tier assignments and slugs |
| .NET checks | `../shared/checks/dotnet/index.md` | .NET check registry (conditional on .sln detection) |

The user must have **read access** to the target repository.
</context>

<anti-patterns>

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Fail hard on API errors (404/403) | Degrade gracefully: 404 = FAIL finding, 403 = WARN with "Unable to check (requires admin access)" | API errors are expected for some checks — crashing loses all progress |
| Re-scan checks that already passed | Load SUMMARY.md first; if user chooses to overwrite, scan all checks fresh | Wastes time and API calls on known-good checks |
| Create duplicate backlog items for the same finding | Overwrite existing `tier-1--license.md` rather than creating `tier-1--license-2.md` | Duplicates confuse the backlog board and scoring |
| Auto-fix findings during scan | Report `[FAIL] LICENSE -- Not found` and route to `ghs-backlog-fix` | Scan is read-only — fixing is a separate skill's job |
| Skip network-dependent checks if offline | Mark as WARN: `[WARN] CI Workflow Health -- Unable to check (network unavailable)` | Skipping silently hides potential failures |

</anti-patterns>

<objective>
Scan a GitHub repository, produce a scored terminal report, and save all findings as structured markdown backlog items.

Outputs:
- Terminal report with health score, failing checks, and open issues
- Backlog items saved to `backlog/{owner}_{repo}/health/` and `backlog/{owner}_{repo}/issues/`
- `SUMMARY.md` with score breakdown and action items

Next routing:
- Suggest `ghs-backlog-sync` to publish findings as GitHub Issues
- Suggest `ghs-backlog-fix` to fix the highest-impact item
- Suggest `ghs-backlog-board` to view the full dashboard
- Suggest `ghs-issue-triage` for unlabeled issues
</objective>

<process>

## Prerequisites

**Rule:** Verify `gh` authentication before any API calls.
**Trigger:** Start of every scan.
**Example:** Run `gh auth status`; if it fails, tell the user to run `gh auth login`.

See `../shared/references/gh-cli-patterns.md` for authentication and repo detection patterns.

## Input

**Rule:** Accept `owner/repo` explicitly, or detect from git remote.
**Trigger:** User invokes scan without specifying a repo.
**Example:** `gh repo view --json nameWithOwner -q '.nameWithOwner'` — if neither works, ask the user.

## Phase 1 — Setup and Stack Detection

1. Detect the repository (`owner/repo`) and default branch
2. Detect repo visibility (public/private), fork status, and commit count
3. **Detect tech stack** to determine active modules:
   ```bash
   # Check for .NET
   gh api repos/{owner}/{repo}/contents/ --jq '.[].name' 2>/dev/null | grep -q '\.sln$' && DOTNET_DETECTED=true
   ```
   See `../shared/checks/index.md` for the full module registry and detection markers.
4. Create output directories: `backlog/{owner}_{repo}/health/` and `backlog/{owner}_{repo}/issues/`
   - If .NET detected: also create `backlog/{owner}_{repo}/dotnet/`
5. If `backlog/{owner}_{repo}/` already exists, load `SUMMARY.md` first (progressive disclosure) — only read individual backlog items if needed for comparison

**Rule:** Ask before overwriting existing health items.
**Trigger:** `backlog/{owner}_{repo}/health/` directory already exists.
**Example:** "Health backlog exists from 2026-02-20. Overwrite or create timestamped version?"

## Phase 2 — Spawn Agents in Parallel

Launch agents simultaneously using the Task tool. Each agent works independently and writes files directly.

### Core Module Agents (always)

| Agent | Template | Substitutions |
|-------|----------|--------------|
| Core Tier 1 Agent | `agents/health-check-agent.md` | `{owner}`, `{repo}`, `{default_branch}`, `{N}=1`, `{module}=core`, `{skills_path}` |
| Core Tier 2 Agent | `agents/health-check-agent.md` | `{owner}`, `{repo}`, `{default_branch}`, `{N}=2`, `{module}=core`, `{skills_path}` |
| Core Tier 3 Agent | `agents/health-check-agent.md` | `{owner}`, `{repo}`, `{default_branch}`, `{N}=3`, `{module}=core`, `{skills_path}` |
| Issues Agent | `agents/issues-agent.md` | `{owner}`, `{repo}`, `{skills_path}` |

### .NET Module Agents (if .sln detected)

| Agent | Template | Substitutions |
|-------|----------|--------------|
| .NET Tier 1 Agent | `agents/health-check-agent.md` | `{owner}`, `{repo}`, `{default_branch}`, `{N}=1`, `{module}=dotnet`, `{skills_path}` |
| .NET Tier 2 Agent | `agents/health-check-agent.md` | `{owner}`, `{repo}`, `{default_branch}`, `{N}=2`, `{module}=dotnet`, `{skills_path}` |
| .NET Tier 3 Agent | `agents/health-check-agent.md` | `{owner}`, `{repo}`, `{default_branch}`, `{N}=3`, `{module}=dotnet`, `{skills_path}` |

All agents use `subagent_type: general-purpose`. Spawn all agents in a **single message** for parallel execution (4 agents for core-only repos, 7 agents for .NET repos).

Each agent reads its module's index file:
- Core agents: `checks/core/index.md`
- .NET agents: `checks/dotnet/index.md`

Backlog items are written to the module's directory:
- Core agents write to: `backlog/{owner}_{repo}/health/`
- .NET agents write to: `backlog/{owner}_{repo}/dotnet/`

See `../shared/references/agent-spawning.md` for spawning patterns and the agent result contract.

### Context Budget

| Pass to Agent | Omit |
|---------------|------|
| Module index (from checks/{module}/index.md) | Other module indexes |
| Check definitions for the agent's tier | Other check definitions |
| Repo owner/name, default branch | Full SUMMARY.md |
| Tech stack detection result | Previous scan results |
| Scoring logic for the check's tier | Full scoring-logic.md |

## Phase 3 — Collect Results and Compute Score

After all agents complete:

1. Parse JSON results from each health check agent
2. Group check results by module (core, dotnet)
3. Calculate per-module scores:
   - Core: `core_pct = round(core_earned / core_possible * 100)`
   - .NET (if active): `dotnet_pct = round(dotnet_earned / dotnet_possible * 100)`
4. Calculate combined score per `../shared/references/scoring-logic.md`:
   - Core only: `score = core_pct`
   - Core + .NET: `score = round(core_pct * 0.6 + dotnet_pct * 0.4)`
5. Parse the issues summary from the issues agent

**Rule:** Retry failed agents once before marking as WARN.
**Trigger:** Agent returns malformed JSON or errors out.
**Example:** Re-run with error appended to prompt. If it fails again, mark all checks in that tier as WARN with detail "Agent failed after retry."

## Phase 4 — Write SUMMARY.md

Write `backlog/{owner}_{repo}/SUMMARY.md` using the template from `references/templates.md`. Include:
- Per-module health score breakdown by tier with progress bars
- Combined score (if language module active)
- Action items table linking to each backlog file (health/ and module-specific dirs)
- Passing checks list (grouped by module)
- Open issues table linking to each issue backlog file

Verify score: `python .claude/skills/shared/scripts/calculate_score.py backlog/{owner}_{repo}`

## Phase 5 — Display Terminal Report

Present combined results as a clean, scannable terminal report. See `../shared/references/output-conventions.md` for full format specification.

Report structure (core-only repo):

```
## Repository Scan: {owner}/{repo}

### Core Health Checks

#### Tier 1 — Required
  [PASS] README.md — Found (2.3 KB)
  [FAIL] LICENSE — Not found
  [WARN] Branch protection — Unable to check (requires admin access)

#### Tier 2 — Recommended
  [PASS] .gitignore — Found
  [FAIL] .editorconfig — Not found

#### Tier 3 — Nice to Have
  [FAIL] SECURITY.md — Not found
  [INFO] FUNDING.yml — Not found (optional)

---

### Health Score: 14/51 (27%)

  Tier 1:  8/16  ████░░░░ (50%)
  Tier 2:  6/26  ██░░░░░░ (23%)
  Tier 3:  0/9   ░░░░░░░░ (0%)

---

### Open Issues — 18 total

| # | Title | Labels | Age | Assignee |
|---|-------|--------|-----|----------|
| 42 | Login page crashes on mobile | bug | 12d | @user |
| 108 | Add dark mode support | enhancement | 45d | — |

Labels: bug: 5 | enhancement: 8 | docs: 2 | unlabeled: 3

---

### Backlog saved to: backlog/{owner}_{repo}/
  health/   — 8 items (8 FAIL, 0 WARN)
  issues/   — 18 items
```

Report structure (repo with .NET module):

```
## Repository Scan: {owner}/{repo}

### Core Health Checks

#### Tier 1 — Required
  [PASS] README.md — Found (2.3 KB)
  [FAIL] LICENSE — Not found

#### Tier 2 — Recommended
  [PASS] .gitignore — Found
  [FAIL] .editorconfig — Not found

#### Tier 3 — Nice to Have
  [FAIL] SECURITY.md — Not found

Core Score: 30/74 (41%)

---

### .NET Health Checks

#### Tier 1 — Required
  [PASS] Directory.Build.props — Found
  [PASS] Test Project Exists — 3 test projects found

#### Tier 2 — Recommended
  [PASS] Nullable Reference Types — Enabled in Directory.Build.props
  [FAIL] Central Package Management — Directory.Packages.props not found
  [FAIL] Code Coverage — No coverlet package detected

#### Tier 3 — Nice to Have
  [FAIL] SourceLink — Microsoft.SourceLink.* not referenced
  [INFO] Target Framework — net9.0 (current)
  [INFO] Package Count — 12 packages across 5 projects

.NET Score: 18/34 (53%)

---

### Combined Health Score: 46% (core 41% × 60% + .NET 53% × 40%)

  Core:   30/74  ███░░░░░ (41%)
  .NET:   18/34  ████░░░░ (53%)

---

### Open Issues — 5 total

| # | Title | Labels | Age | Assignee |
|---|-------|--------|-----|----------|
| 12 | Add CI pipeline | enhancement | 30d | — |

---

### Backlog saved to: backlog/{owner}_{repo}/
  health/   — 6 items (5 FAIL, 1 WARN)
  dotnet/   — 3 items (3 FAIL)
  issues/   — 5 items
```

If there are more than 20 issues, show the 20 most recent and note: "(+N more -- see backlog/issues/ for full list)".

### Goal-Backward Verification

| Level | Check | Method |
|-------|-------|--------|
| Existence | Output artifact exists | File/PR/API response check |
| Substance | Contains correct content | Diff review, body inspection |
| Wiring | Properly connected | Correct branch target, auto-close refs |

</process>

## Next Routing

| Condition | Suggestion |
|-----------|-----------|
| FAIL items exist | "To publish findings as GitHub Issues: `/ghs-backlog-sync {owner}/{repo}`" |
| FAIL items exist | "To fix the highest-impact item: `/ghs-backlog-fix backlog/{owner}_{repo}/health/{top_item}`" |
| Any results | "To view the full dashboard: `/ghs-backlog-board`" |
| All checks pass, unlabeled issues | "To triage unlabeled issues: `/ghs-issue-triage {owner}/{repo}`" |

## Edge Cases

| Scenario | Handling |
|----------|---------|
| Private repo | All checks work if user has access. Note in report header. |
| Org-level settings | Branch protection/security alerts may be org-managed. If 403, mention this. |
| Fork | Note in report — forks often inherit upstream settings. |
| Empty/new repo (0 commits) | Add note: "This appears to be a new repository -- focus on Tier 1 items first." |
| No failures and no issues | Display congratulatory message. Create only SUMMARY.md. |
| Many issues (>20) | Cap terminal display at 20, save all to backlog. |
| Very long issue bodies | Truncate to 500 characters with link to full issue. |

## Re-running

| Content | Behavior |
|---------|---------|
| `health/` | Ask user: overwrite or create timestamped version |
| `issues/` | Always refresh: remove closed, add new, update changed |

## Finding Description Quality

| Quality | Example |
|---------|---------|
| Good | "Missing LICENSE file -- no open-source license detected in repository root" |
| Bad | "LICENSE check failed" |
| Good | "Branch protection not enabled on `main` -- direct pushes allowed" |
| Bad | "branch protection FAIL" |

Descriptions must state **what** is wrong and **why** it matters.

## Examples

**Scan a specific repo:** User says "scan phmatray/NewSLN" -- terminal report with health score, failing checks, open issues. Backlog saved to `backlog/phmatray_NewSLN/`.

**Scan current repo:** User says "is my repo set up properly?" -- detect from git remote, spawn agents, display report, save backlog.

**Re-scan after fixes:** User says "re-scan phmatray/NewSLN" -- refresh health checks (asks about overwrite), sync issues, update SUMMARY.md.

## Troubleshooting

| Problem | Solution |
|---------|---------|
| `gh auth status` fails | `gh` CLI not authenticated. Run `gh auth login`. |
| 403 on branch protection | Requires admin access. Check agent reports as WARN -- expected. |
| Rate limiting during scan | See `../shared/references/gh-cli-patterns.md`. Do not retry in a loop. |
| Scan seems slow | 4 agents run in parallel. Large repos with many issues (500+) take longer. |
