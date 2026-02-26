---
name: repo-health-check
description: >
  Audits a GitHub repository for quality essentials, produces a scored health report, and saves each
  actionable finding as a structured markdown backlog item. Use this skill whenever the user wants to
  check repository quality, audit a repo's setup, verify best practices are followed, or asks about
  missing files like README, LICENSE, CODEOWNERS, CI/CD, branch protection, templates, or security
  policies. Also trigger when users say things like "is my repo set up properly", "what's missing from
  my project", "repo audit", "repository checklist", "health check", "save health report", "export
  audit results", or "create backlog from audit".
---

# Repo Health Check

Audit a GitHub repository against quality best practices, display a terminal report, and save actionable findings as structured markdown backlog items.

## Prerequisites

- The `gh` CLI must be authenticated (`gh auth status`)
- The user must have read access to the target repository

## Input

The user may provide a repo in `owner/repo` format. If not provided, detect the repo from the current git remote:

```bash
gh repo view --json nameWithOwner -q '.nameWithOwner'
```

If neither works, ask the user which repository to audit.

## Phase 1 — Audit

Run all checks using `gh api` and `gh repo view`. Organize them into three severity tiers that affect scoring.

### Tier 1 — Required (4 points each)

These are non-negotiable for any public or team-shared repository.

| Check | How to verify | Pass condition |
|-------|--------------|----------------|
| **README** | `gh api repos/{owner}/{repo}/readme` | Exists AND response size > 500 bytes (not just a title) |
| **LICENSE** | `gh api repos/{owner}/{repo}/license` | Exists (any recognized license) |
| **Description** | `gh repo view --json description -q '.description'` | Non-empty string |
| **Default branch protection** | `gh api repos/{owner}/{repo}/branches/{default_branch}/protection` | Returns 200 (not 404). Note: may require admin access — if 403/404, report as "unable to check" rather than fail |

### Tier 2 — Recommended (2 points each)

Important for maintainability and collaboration.

| Check | How to verify | Pass condition |
|-------|--------------|----------------|
| **.gitignore** | `gh api repos/{owner}/{repo}/contents/.gitignore` | Exists |
| **CI/CD workflows** | `gh api repos/{owner}/{repo}/contents/.github/workflows` | Directory exists and contains at least one `.yml` or `.yaml` file |
| **CODEOWNERS** | Check `gh api repos/{owner}/{repo}/contents/CODEOWNERS`, also `.github/CODEOWNERS` and `docs/CODEOWNERS` | Exists in any standard location |
| **Issue templates** | `gh api repos/{owner}/{repo}/contents/.github/ISSUE_TEMPLATE` | Directory exists with at least one file |
| **PR template** | Check `gh api repos/{owner}/{repo}/contents/.github/pull_request_template.md`, also `.github/PULL_REQUEST_TEMPLATE.md` (case variations) and `.github/PULL_REQUEST_TEMPLATE/` directory | Exists in any standard location |
| **Topics** | `gh repo view --json repositoryTopics -q '.repositoryTopics[].name'` | At least one topic set |

### Tier 3 — Nice to Have (1 point each)

Polish items that signal a mature, well-maintained project.

| Check | How to verify | Pass condition |
|-------|--------------|----------------|
| **SECURITY.md** | `gh api repos/{owner}/{repo}/contents/SECURITY.md` | Exists |
| **CONTRIBUTING.md** | `gh api repos/{owner}/{repo}/contents/CONTRIBUTING.md` | Exists |
| **Dependabot / security alerts** | `gh api repos/{owner}/{repo}/vulnerability-alerts` (check if enabled), `gh api repos/{owner}/{repo}/dependabot/alerts?state=open&per_page=1` | No open critical/high alerts. If alerts API returns 403, report as "not enabled" with a suggestion to enable |
| **Funding** | `gh api repos/{owner}/{repo}/contents/.github/FUNDING.yml` | Exists (purely informational, no penalty) |

### Execution Strategy

Run API calls in parallel where possible. Group independent checks and execute them concurrently using background subshells.

Handle errors gracefully:
- **404**: The file/feature doesn't exist — that's a legitimate "fail" result
- **403**: Insufficient permissions — report as "unable to check (insufficient permissions)" with a note, don't count as fail
- **Rate limiting**: If hit, wait and retry once

### Terminal Report

Present results as a clean, scannable terminal report using this structure:

```
## Repository Health Report: {owner}/{repo}

### Tier 1 — Required
  [PASS] README.md — Found (2.3 KB)
  [FAIL] LICENSE — Not found
  [PASS] Description — "A tool for automating GitHub workflows"
  [WARN] Branch protection — Unable to check (requires admin access)

### Tier 2 — Recommended
  [PASS] .gitignore — Found
  [PASS] CI/CD workflows — 3 workflow files found
  [FAIL] CODEOWNERS — Not found
  [FAIL] Issue templates — Not found
  [PASS] PR template — Found at .github/pull_request_template.md
  [FAIL] Topics — No topics set

### Tier 3 — Nice to Have
  [FAIL] SECURITY.md — Not found
  [FAIL] CONTRIBUTING.md — Not found
  [PASS] Security alerts — No open alerts
  [INFO] FUNDING.yml — Not found (optional)

---

### Health Score: 14/28 (50%)

  Tier 1:  8/16  ████░░░░ (50%)
  Tier 2:  6/12  █████░░░ (50%)
  Tier 3:  0/3   ░░░░░░░░ (0%)
```

### Scoring Rules

- Each check contributes points based on its tier (Tier 1 = 4, Tier 2 = 2, Tier 3 = 1)
- WARN items (permission issues) are excluded from the total — don't penalize for things we can't verify
- INFO items (like FUNDING.yml) are purely informational and don't affect the score
- The percentage is `earned_points / possible_points * 100`, rounded to the nearest integer

## Phase 2 — Save Backlog Items

After displaying the terminal report, save each actionable finding as a structured markdown file.

### Output Directory

Save files to `backlog/{owner}/{repo}/health-report/` in the current working directory. Replace `/` in the repo name with `_`.

Structure:
```
backlog/{owner}_{repo}/health-report/
├── SUMMARY.md                          # Overall report snapshot
├── tier-1--readme.md                   # One file per failed/warn item
├── tier-1--description.md
├── tier-2--gitignore.md
└── ...
```

File naming: `tier-{N}--{check-name-kebab}.md`. Only create files for `[FAIL]` or `[WARN]` items — not `[PASS]` or `[INFO]`.

### Templates

Read `references/templates.md` for the exact SUMMARY.md and action item file templates. The key principle: each file should be self-contained and actionable — someone reading it should understand what's missing, why it matters, and exactly how to fix it, with real commands using the actual `owner/repo`.

### Execution

1. Create the output directory
2. Generate one action item file per `[FAIL]`/`[WARN]` item using the template
3. Generate `SUMMARY.md` linking to all items and listing passing checks
4. Report to the user: show files created and suggest starting with the highest-tier items

### Re-running

If `backlog/{owner}_{repo}/health-report/` already exists, ask the user whether to overwrite or create a timestamped version (e.g., `health-report-2026-02-26/`).

## Edge Cases

- **Private repos**: All checks should still work if the user has access. Note in the report header whether the repo is public or private.
- **Org-level settings**: Branch protection and security alerts may be managed at the org level. If checks fail with 403, mention this possibility.
- **Forks**: Note if the repo is a fork, since forks often inherit settings from upstream and may not need all checks.
- **Empty/new repos**: If the repo has zero commits, several checks will naturally fail. Add a note: "This appears to be a new repository — focus on Tier 1 items first."
- **No failures**: If all checks pass, create only SUMMARY.md with a congratulatory note. No action item files needed.
