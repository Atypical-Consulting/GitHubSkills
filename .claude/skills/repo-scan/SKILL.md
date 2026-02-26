---
name: repo-scan
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
metadata:
  author: phmatray
  version: 3.0.0
---

# Repo Scan

Scan a GitHub repository for quality best practices and open issues, display a terminal report, and save all findings as structured markdown backlog items.

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

## Architecture

This skill uses **parallel agents** to speed up scanning. Instead of running all checks sequentially, it spawns specialized agents that work simultaneously.

### Roles

1. **Orchestrator** (you): detects the repo, spawns agents, collects results, computes scores, writes SUMMARY.md, displays the terminal report
2. **Health Check Agents** (spawned via Task tool): one per tier, each runs all checks in its tier and writes backlog items for failures
3. **Issues Agent** (spawned via Task tool): fetches open issues and writes issue backlog items

### Check Definitions

Each health check is defined in its own self-contained file under `../shared/checks/`. Read `../shared/checks/index.md` for the full registry with tier assignments, slugs, and links to individual check files.

## Execution

### Step 1 — Setup

1. Detect the repository (`owner/repo`) and default branch
2. Detect repo visibility (public/private), whether it's a fork, and commit count
3. Create output directories: `backlog/{owner}_{repo}/health/` and `backlog/{owner}_{repo}/issues/`
4. If `backlog/{owner}_{repo}/` already exists, ask the user whether to overwrite health items or create a timestamped version. Issues are always synced.

### Step 2 — Spawn Agents in Parallel

Launch **4 agents simultaneously** using the Task tool. Each agent works independently and writes files directly.

#### Agent Prompt Template

Each health check agent receives a prompt like this (adapt for the specific tier):

```
You are a health check agent for the repo-scan skill.

Repository: {owner}/{repo}
Default branch: {default_branch}
Tier: {N}
Output directory: backlog/{owner}_{repo}/health/
Date: {YYYY-MM-DD}
Skills path: {path to .claude/skills}

Your job:
1. Read the check index at `{skills_path}/shared/checks/index.md` to find which checks belong to Tier {N}
2. For each check in your tier:
   a. Read the check file: `{skills_path}/shared/checks/{slug}.md`
   b. Run the verification command from the "Verification" section (substitute {owner}/{repo} and {default_branch})
   c. Determine PASS/FAIL/WARN based on the "Status Rules" section
   d. If FAIL or WARN: write a backlog item file to `backlog/{owner}_{repo}/health/tier-{N}--{slug}.md`
      using the health item template from `{skills_path}/repo-scan/references/templates.md`
      and the "Backlog Content" section from the check file for What's Missing, Why It Matters, How to Fix, and Acceptance Criteria
   e. Record the result

3. Return your results as a fenced JSON array, one object per check:
[
  {"check": "README", "slug": "readme", "tier": 1, "points": 4, "status": "PASS", "detail": "Found (2.3 KB)"},
  {"check": "LICENSE", "slug": "license", "tier": 1, "points": 4, "status": "FAIL", "detail": "Not found"}
]

Important:
- Use `2>&1 || true` on all gh commands so 404s don't cause errors
- For checks with scoring: "info", use status "INFO" instead of "FAIL" when missing
- Write backlog items only for FAIL and WARN statuses
```

#### Issues Agent Prompt

```
You are an issues collection agent for the repo-scan skill.

Repository: {owner}/{repo}
Output directory: backlog/{owner}_{repo}/issues/
Date: {YYYY-MM-DD}
Skills path: {path to .claude/skills}

Your job:
1. Fetch all open issues:
   gh issue list --repo {owner}/{repo} --state open --json number,title,labels,assignees,createdAt,updatedAt,body --limit 500

2. Filter out:
   - Issues with title containing "Dependency Dashboard" (Renovate bot)
   - Issues with title containing "renovate" AND a bot label

3. For each remaining issue, write a backlog item file to `backlog/{owner}_{repo}/issues/issue-{number}--{title-kebab}.md`
   using the issue item template from `{skills_path}/repo-scan/references/templates.md`
   - Title kebab-case, truncated to 50 chars max (cut at last complete word)
   - Truncate issue body to 500 characters in the file

4. If `backlog/{owner}_{repo}/issues/` already has files, sync:
   - Remove files for issues that are now closed
   - Add files for newly opened issues
   - Update files if title/labels/assignees changed

5. Return a JSON summary:
{
  "total": 18,
  "labels": {"bug": 5, "enhancement": 8, "docs": 2, "unlabeled": 3},
  "issues": [
    {"number": 42, "title": "Login page crashes", "labels": ["bug"], "age_days": 12, "assignee": "user"},
    ...
  ]
}
```

#### Launching All 4 Agents

Use the Task tool to spawn all 4 agents in a **single message** (parallel execution):

- **Tier 1 Agent**: subagent_type `general-purpose`, prompt with tier=1
- **Tier 2 Agent**: subagent_type `general-purpose`, prompt with tier=2
- **Tier 3 Agent**: subagent_type `general-purpose`, prompt with tier=3
- **Issues Agent**: subagent_type `general-purpose`, prompt for issue collection

### Step 3 — Collect Results and Compute Score

After all agents complete:

1. Parse the JSON results from each health check agent
2. Combine all check results into a unified list
3. Calculate the health score using these rules:
   - Each check contributes points based on its tier (Tier 1 = 4, Tier 2 = 2, Tier 3 = 1)
   - WARN items are **excluded** from both earned and possible totals
   - INFO items (Funding) don't affect the score at all
   - Percentage = `earned_points / possible_points * 100`, rounded to nearest integer
4. Parse the issues summary from the issues agent

### Step 4 — Write SUMMARY.md

Write `backlog/{owner}_{repo}/SUMMARY.md` using the template from `references/templates.md`. Include:
- Health score breakdown by tier with progress bars
- Action items table linking to each health backlog file
- Passing checks list
- Open issues table linking to each issue backlog file

You can verify the score with: `python ../shared/scripts/calculate_score.py backlog/{owner}_{repo}`

### Step 5 — Display Terminal Report

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
  [FAIL] CODEOWNERS — Not found
  [FAIL] Issue templates — Not found
  [PASS] PR template — Found at .github/pull_request_template.md
  [FAIL] Topics — No topics set

#### Tier 3 — Nice to Have
  [FAIL] SECURITY.md — Not found
  [FAIL] CONTRIBUTING.md — Not found
  [PASS] Security alerts — No open alerts
  [PASS] .editorconfig Drift — N/A (no .editorconfig to compare)
  [INFO] FUNDING.yml — Not found (optional)

---

### Health Score: 14/36 (39%)

  Tier 1:  8/16  ████░░░░ (50%)
  Tier 2:  4/16  ██░░░░░░ (25%)
  Tier 3:  2/4   ████░░░░ (50%)

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

Progress bars: `█` for filled, `░` for empty, 8 characters wide. Filled = `round(percentage / 100 * 8)`.

If there are more than 20 issues, show the 20 most recent and note: "(+N more — see backlog/issues/ for full list)".

## Edge Cases

- **Private repos**: All checks should still work if the user has access. Note in the report header.
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
