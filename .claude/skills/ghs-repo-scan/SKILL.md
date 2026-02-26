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
  version: 4.0.0
---

# Repo Scan

Scan a GitHub repository for quality best practices and open issues, display a terminal report, and save all findings as structured markdown backlog items.

<context>
Purpose: Audit a GitHub repository's quality setup and open issues, producing a scored health report and structured backlog.

Roles:
1. **Orchestrator** (you) — detects the repo, spawns agents, collects results, computes scores, writes SUMMARY.md, displays the terminal report
2. **Health Check Agents** (spawned via Task tool) — one per tier, each runs all checks in its tier and writes backlog items for failures
3. **Issues Agent** (spawned via Task tool) — fetches open issues and writes issue backlog items

Shared docs:
- `../shared/gh-prerequisites.md` — authentication, repo detection, error handling
- `../shared/checks/index.md` — full check registry with tier assignments, slugs, and links
- `../shared/config.md` — scoring constants and display settings
- `../shared/backlog-format.md` — file naming, metadata formats, scoring rules

Check definitions: Each health check lives in its own file under `../shared/checks/`. Read the index for the full registry.
</context>

<objective>
Produce a scored health report and save findings as backlog items under `backlog/{owner}_{repo}/`.

Outputs:
- `backlog/{owner}_{repo}/SUMMARY.md` — unified repo summary
- `backlog/{owner}_{repo}/health/tier-N--slug.md` — one file per FAIL/WARN check
- `backlog/{owner}_{repo}/issues/issue-N--title.md` — one file per open issue
- Terminal report with health score, check results, and issue table

Next routing:
- Suggest `ghs-backlog-fix` for FAIL items — "To fix the highest-impact item: `/ghs-backlog-fix backlog/{owner}_{repo}/health/{top_item}`"
- Suggest `ghs-backlog-board` for full dashboard view
- If all checks pass, suggest `ghs-issue-triage` if there are unlabeled issues
</objective>

<process>

## Prerequisites

- The `gh` CLI must be authenticated (`gh auth status`)
- The user must have read access to the target repository

For prerequisites, error handling, and repo detection, read `../shared/gh-prerequisites.md`.

## Input

The user may provide a repo in `owner/repo` format. If not provided, detect the repo from the current git remote:

```bash
gh repo view --json nameWithOwner -q '.nameWithOwner'
```

If neither works, ask the user which repository to scan.

## Phase 1 — Setup

1. Detect the repository (`owner/repo`) and default branch
2. Detect repo visibility (public/private), whether it's a fork, and commit count
3. Create output directories: `backlog/{owner}_{repo}/health/` and `backlog/{owner}_{repo}/issues/`
4. If `backlog/{owner}_{repo}/` already exists, ask the user whether to overwrite health items or create a timestamped version. Issues are always synced.

## Phase 2 — Spawn Agents in Parallel

Launch **4 agents simultaneously** using the Task tool. Each agent works independently and writes files directly.

Read `agents/health-check-agent.md` for the health check agent prompt template. Substitute `{owner}`, `{repo}`, `{default_branch}`, `{N}` (tier number), and `{skills_path}` placeholders.

Read `agents/issues-agent.md` for the issues agent prompt template. Substitute `{owner}`, `{repo}`, and `{skills_path}` placeholders.

Use the Task tool to spawn all 4 agents in a **single message** (parallel execution):

- **Tier 1 Agent**: subagent_type `general-purpose`, prompt from health-check-agent.md with tier=1
- **Tier 2 Agent**: subagent_type `general-purpose`, prompt from health-check-agent.md with tier=2
- **Tier 3 Agent**: subagent_type `general-purpose`, prompt from health-check-agent.md with tier=3
- **Issues Agent**: subagent_type `general-purpose`, prompt from issues-agent.md

## Phase 3 — Collect Results and Compute Score

After all agents complete:

1. Parse the JSON results from each health check agent
2. Combine all check results into a unified list
3. Calculate the health score (see `../shared/config.md` for tier point values):
   - WARN items are **excluded** from both earned and possible totals — they indicate permission issues, not real failures
   - INFO items don't affect the score at all — they're purely informational
   - Percentage = `earned_points / possible_points * 100`, rounded to nearest integer
4. Parse the issues summary from the issues agent

## Phase 4 — Write SUMMARY.md

Write `backlog/{owner}_{repo}/SUMMARY.md` using the template from `references/templates.md`. Include:
- Health score breakdown by tier with progress bars
- Action items table linking to each health backlog file
- Passing checks list
- Open issues table linking to each issue backlog file

You can verify the score with: `python ../shared/scripts/calculate_score.py backlog/{owner}_{repo}`

## Phase 5 — Display Terminal Report

Present the combined results as a clean, scannable terminal report:

```
## Repository Scan: {owner}/{repo}

### Health Checks

#### Tier 1 — Required
  [PASS] README.md — Found (2.3 KB)
  [FAIL] LICENSE — Not found
  [PASS] Description — "A tool for automating GitHub workflows"
  [WARN] Branch protection — Unable to check (requires admin access)

#### Tier 2 — Recommended
  [PASS] .gitignore — Found
  [PASS] CI/CD workflows — 3 workflow files found
  [FAIL] CI Workflow Health — 1 workflow failing (build.yml)
  [FAIL] .editorconfig — Not found
  ...

#### Tier 3 — Nice to Have
  [FAIL] SECURITY.md — Not found
  [FAIL] CONTRIBUTING.md — Not found
  [INFO] FUNDING.yml — Not found (optional)
  ...

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
...

Labels: bug: 5 | enhancement: 8 | docs: 2 | unlabeled: 3

---

### Backlog saved to: backlog/{owner}_{repo}/
  health/   — 8 items (8 FAIL, 0 WARN)
  issues/   — 18 items
```

Progress bars use `█` filled and `░` empty, 8 chars wide (see `../shared/config.md`).

If there are more than 20 issues, show the 20 most recent and note: "(+N more — see backlog/issues/ for full list)".

</process>

## Edge Cases

- **Private repos**: All checks still work if the user has access. Note in the report header.
- **Org-level settings**: Branch protection and security alerts may be managed at the org level. If 403, mention this possibility.
- **Forks**: Note if the repo is a fork — forks often inherit settings from upstream.
- **Empty/new repos**: If zero commits, add a note: "This appears to be a new repository — focus on Tier 1 items first."
- **No failures and no issues**: Display a congratulatory message. Create only SUMMARY.md.
- **Repos with many issues**: Cap terminal display at 20 issues, but save all to the backlog.
- **Issues with very long bodies**: Truncate to 500 characters with a link to the full issue.

## Re-running

If `backlog/{owner}_{repo}/` already exists:
- **health/** — Ask the user whether to overwrite or create a timestamped version
- **issues/** — Always refresh: remove closed, add new, update changed

## Examples

**Example 1: Scan a specific repo**
User says: "scan phmatray/NewSLN"
Result: Terminal report showing health score, failing checks, open issues. Backlog files saved to `backlog/phmatray_NewSLN/`.

**Example 2: Scan the current repo**
User says: "is my repo set up properly?"
Result: Detects repo from git remote, spawns agents, displays report, saves backlog items.

**Example 3: Re-scan after fixes**
User says: "re-scan phmatray/NewSLN"
Result: Refreshes health checks (asks about overwrite), syncs issues, updates SUMMARY.md.

## Troubleshooting

**`gh auth status` fails**
The `gh` CLI is not authenticated. Run `gh auth login` first.

**403 on branch protection check**
Branch protection requires admin access. The check agent will report as WARN — this is expected.

**Rate limiting during scan**
If you hit GitHub's API rate limit, the agents will encounter errors. Wait and retry.

**Scan seems slow**
The skill runs 4 agents in parallel. Most scans complete quickly. Large repos with many issues (500+) will take longer.
