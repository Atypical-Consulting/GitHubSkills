---
name: repo-scan
description: >
  Scans a GitHub repository for quality essentials and open issues, produces a scored report, and
  saves all findings as structured markdown backlog items. Use this skill whenever the user wants to
  check repository quality, audit a repo's setup, see open issues organized as backlog, verify best
  practices are followed, or asks about missing files like README, LICENSE, CODEOWNERS, CI/CD, branch
  protection, templates, or security policies. Also trigger when users say things like "scan my repo",
  "is my repo set up properly", "what's missing from my project", "repo audit", "repo scan",
  "repository checklist", "health check", "what issues are open", "organize my issues",
  "save health report", "export audit results", or "create backlog from audit".
---

# Repo Scan

Scan a GitHub repository for quality best practices and open issues, display a terminal report, and save all findings as structured markdown backlog items.

## Prerequisites

- The `gh` CLI must be authenticated (`gh auth status`)
- The user must have read access to the target repository

## Input

The user may provide a repo in `owner/repo` format. If not provided, detect the repo from the current git remote:

```bash
gh repo view --json nameWithOwner -q '.nameWithOwner'
```

If neither works, ask the user which repository to scan.

## Phase 1 — Health Audit

Run all checks using `gh api` and `gh repo view`. Organize them into three severity tiers that affect scoring.

### Tier 1 — Required (4 points each)

These are non-negotiable for any public or team-shared repository.

| Check | How to verify | Pass condition |
|-------|--------------|----------------|
| **README** | `gh api repos/{owner}/{repo}/readme` | Exists AND response size > 500 bytes (not just a title) |
| **LICENSE** | `gh api repos/{owner}/{repo}/license` | Exists (any recognized license) |
| **Description** | `gh repo view --json description -q '.description'` | Non-empty string |
| **Default branch protection** | `gh api repos/{owner}/{repo}/branches/{default_branch}/protection` | Returns 200 (not 404). Note: may require admin access — if 403/404, report as "unable to check" rather than fail. **Solo maintainer awareness**: detect if the repo has a single owner/contributor (check collaborators count or org membership). For solo repos, branch protection is still recommended but the backlog item should suggest a lightweight config (no required reviews, just force-push protection and enforce admins) since requiring PR approvals blocks the sole maintainer from merging. |

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

## Phase 2 — Issue Collection

Fetch all open issues from the repository using `gh issue list`.

### How to fetch

```bash
gh issue list --repo {owner}/{repo} --state open --json number,title,labels,assignees,createdAt,updatedAt,body --limit 500
```

### Filtering

Exclude issues that match any of these conditions:
- Title contains "Dependency Dashboard" (Renovate bot dashboard issues)
- Title contains "renovate" AND has a bot label

Keep everything else — bugs, features, questions, unlabeled issues.

### Terminal Report

After the health audit section, display the issue summary:

```
### Open Issues — {count} total

| # | Title | Labels | Age | Assignee |
|---|-------|--------|-----|----------|
| 42 | Login page crashes on mobile | bug | 12d | @user |
| 108 | Add dark mode support | enhancement | 45d | — |
| 115 | Update docs for v2 API | docs | 3d | — |
...

Labels breakdown:
  bug: 5 | enhancement: 8 | docs: 2 | unlabeled: 3
```

If there are more than 20 issues, show the 20 most recent in the table and note the rest: "(+N more — see backlog/issues/ for full list)".

## Phase 3 — Save Backlog Items

After displaying the terminal report, save all findings as structured markdown files.

### Output Directory

Save files to `backlog/{owner}_{repo}/` in the current working directory.

Structure:
```
backlog/{owner}_{repo}/
├── SUMMARY.md                          # Unified repo summary
├── health/                             # Health check findings
│   ├── tier-1--readme.md
│   ├── tier-2--gitignore.md
│   └── ...
└── issues/                             # Open GitHub issues
    ├── issue-42--login-page-crashes.md
    ├── issue-108--add-dark-mode.md
    └── ...
```

### File naming

- Health items: `tier-{N}--{check-name-kebab}.md` — only create files for `[FAIL]` or `[WARN]` items
- Issue items: `issue-{number}--{title-kebab}.md` — kebab-case title, truncated to 50 chars max

### Templates

Read `references/templates.md` for the exact SUMMARY.md, health item, and issue item file templates. Each file should be self-contained — someone reading it should understand the context and what action to take.

### Execution

1. Create the output directories (`health/`, `issues/`)
2. Generate health item files per `[FAIL]`/`[WARN]` item
3. Generate issue item files per open issue
4. Generate unified `SUMMARY.md` covering both sources
5. Report to the user: show files created, suggest starting with the highest-priority items

### Re-running

If `backlog/{owner}_{repo}/` already exists:
- **health/** — Ask the user whether to overwrite or create a timestamped version
- **issues/** — Always refresh: remove issue files for issues that are now closed, add new ones for newly opened issues, update existing ones if title/labels/assignees changed. This keeps the issues directory in sync with GitHub.

## Terminal Report — Full Structure

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
  [FAIL] CODEOWNERS — Not found
  [FAIL] Issue templates — Not found
  [PASS] PR template — Found at .github/pull_request_template.md
  [FAIL] Topics — No topics set

#### Tier 3 — Nice to Have
  [FAIL] SECURITY.md — Not found
  [FAIL] CONTRIBUTING.md — Not found
  [PASS] Security alerts — No open alerts
  [INFO] FUNDING.yml — Not found (optional)

---

### Health Score: 14/28 (50%)

  Tier 1:  8/16  ████░░░░ (50%)
  Tier 2:  6/12  █████░░░ (50%)
  Tier 3:  0/3   ░░░░░░░░ (0%)

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

### Scoring Rules

- Each health check contributes points based on its tier (Tier 1 = 4, Tier 2 = 2, Tier 3 = 1)
- WARN items (permission issues) are excluded from the total — don't penalize for things we can't verify
- INFO items (like FUNDING.yml) are purely informational and don't affect the score
- The percentage is `earned_points / possible_points * 100`, rounded to the nearest integer
- Issues don't have a point score — they're tracked by count and labels

## Edge Cases

- **Private repos**: All checks should still work if the user has access. Note in the report header whether the repo is public or private.
- **Org-level settings**: Branch protection and security alerts may be managed at the org level. If checks fail with 403, mention this possibility.
- **Forks**: Note if the repo is a fork, since forks often inherit settings from upstream and may not need all checks.
- **Empty/new repos**: If the repo has zero commits, several checks will naturally fail. Add a note: "This appears to be a new repository — focus on Tier 1 items first."
- **No failures and no issues**: Display a congratulatory message. Create only SUMMARY.md.
- **Repos with many issues**: Cap the terminal display at 20 issues, but save all of them to the backlog.
- **Issues with very long bodies**: Truncate the body to 500 characters in the backlog item file, with a link to the full issue.
