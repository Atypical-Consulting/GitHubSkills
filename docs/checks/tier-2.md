# Core — Tier 2 — Recommended

Tier 2 core checks verify professional standards that well-maintained repositories should have. Each check is worth **2 points**. There are 22 checks in this tier for a maximum of 44 points. These checks run for all repositories regardless of tech stack.

## .gitignore

| Slug | Category | What it checks |
|------|----------|----------------|
| `gitignore` | Dev Config | A `.gitignore` file exists and is non-empty |

Prevents build artifacts, dependencies, and OS files from being committed. Every project should have one tailored to its tech stack.

---

## CI/CD Workflows

| Slug | Category | What it checks |
|------|----------|----------------|
| `ci-cd-workflows` | CI/CD | At least one GitHub Actions workflow exists in `.github/workflows/` |

Automated testing and deployment are table-stakes for modern development. Even a simple "run tests on push" workflow catches regressions early.

---

## CI Workflow Health

| Slug | Category | What it checks |
|------|----------|----------------|
| `ci-workflow-health` | CI/CD | The most recent CI workflow run completed successfully |

Having CI is good. Having CI that actually passes is better. This check verifies your workflows aren't permanently broken.

---

## Action Version Pinning

| Slug | Category | What it checks |
|------|----------|----------------|
| `action-version-pinning` | CI/CD | Third-party actions use SHA pins or version tags, not `@main`/`@master`/`@latest` |

Unpinned actions are a supply-chain security risk. If a third-party action's `main` branch is compromised, your workflow automatically pulls the malicious code. Pin to SHAs or version tags for reproducible, secure builds.

---

## Workflow Permissions

| Slug | Category | What it checks |
|------|----------|----------------|
| `workflow-permissions` | CI/CD | Every workflow declares an explicit `permissions:` block |

Without explicit permissions, workflows inherit the repository's default token permissions — often overly broad. Declaring `permissions:` limits the blast radius if a workflow is compromised.

---

## .editorconfig

| Slug | Category | What it checks |
|------|----------|----------------|
| `editorconfig` | Dev Config | An `.editorconfig` file exists |

Ensures consistent formatting (indentation, line endings, charset) across different editors and IDEs without requiring project-specific editor plugins.

---

## CODEOWNERS

| Slug | Category | What it checks |
|------|----------|----------------|
| `codeowners` | Dev Config | A `CODEOWNERS` file exists (in root, `.github/`, or `docs/`) |

Automatically assigns reviewers to PRs based on which files are changed. Essential for teams, useful even for solo projects to enforce review habits.

---

## Issue Templates

| Slug | Category | What it checks |
|------|----------|----------------|
| `issue-templates` | Community | At least one issue template exists in `.github/ISSUE_TEMPLATE/` |

Structured issue templates ensure reporters provide the information needed to diagnose and fix problems. Reduces back-and-forth on every new issue.

---

## PR Template

| Slug | Category | What it checks |
|------|----------|----------------|
| `pr-template` | Community | A pull request template exists (`.github/PULL_REQUEST_TEMPLATE.md`) |

Guides contributors to include context, test plans, and checklists with every PR. Makes code review faster and more consistent.

---

## Topics

| Slug | Category | What it checks |
|------|----------|----------------|
| `topics` | Repo Settings | The repository has at least one topic/tag set |

Topics improve discoverability in GitHub search and help users find your project. Think of them as SEO for your repo.

**Fix:** `gh repo edit --add-topic "your-topic"`

---

## Changelog

| Slug | Category | What it checks |
|------|----------|----------------|
| `changelog` | Documentation | A `CHANGELOG.md` file exists |

A changelog communicates what changed between versions. Users and contributors rely on it to understand upgrade paths and new features.

---

## Delete Branch on Merge

| Slug | Category | What it checks |
|------|----------|----------------|
| `delete-branch-on-merge` | Repo Settings | The "Automatically delete head branches" setting is enabled |

Prevents stale branches from accumulating after PRs are merged. Keeps the branch list clean and avoids confusion.

**Fix:** `gh repo edit --delete-branch-on-merge`

---

## GitHub Releases

| Slug | Category | What it checks |
|------|----------|----------------|
| `github-releases` | Maintenance | At least one GitHub Release exists |

Releases provide versioned snapshots of your project with release notes. They're how many users discover and download specific versions.

---

## Stale Issues

| Slug | Category | What it checks |
|------|----------|----------------|
| `stale-issues` | Maintenance | No issues have been inactive for over 90 days without a response |

Stale issues signal an unmaintained project. Regular triage keeps the issue tracker useful and shows contributors their reports are valued.

---

## Stale PRs

| Slug | Category | What it checks |
|------|----------|----------------|
| `stale-prs` | Maintenance | No PRs have been inactive for over 30 days |

Abandoned PRs waste contributor effort and create confusion. Review, merge, or close them promptly.

---

## Stale Branches

| Slug | Category | What it checks |
|------|----------|----------------|
| `stale-branches` | Maintenance | No branches are older than 90 days without activity |

Stale branches clutter the repository and may contain outdated or conflicting code. Clean them up or delete them.

---

## Merge Strategy

| Slug | Category | What it checks |
|------|----------|----------------|
| `merge-strategy` | Repo Settings | A deliberate merge strategy is configured (not all three enabled) |

Having all three merge options enabled (merge, squash, rebase) leads to inconsistent git history. Pick a strategy and stick with it.

---

## README Description

| Slug | Category | What it checks |
|------|----------|----------------|
| `readme-description` | Documentation | The README contains a meaningful project description (not just the title) |

A title alone doesn't tell visitors what the project does. The first paragraph should clearly explain the project's purpose.

---

## README Badges

| Slug | Category | What it checks |
|------|----------|----------------|
| `readme-badges` | Documentation | The README contains at least one badge (build status, version, license, etc.) |

Badges provide at-a-glance project health information. Common badges: CI status, latest version, license type, code coverage.

---

## README Installation

| Slug | Category | What it checks |
|------|----------|----------------|
| `readme-installation` | Documentation | The README includes installation instructions |

Users need to know how to install or set up the project. An "Installation" or "Getting Started" section is expected.

---

## README Usage Examples

| Slug | Category | What it checks |
|------|----------|----------------|
| `readme-usage` | Documentation | The README includes usage examples or code snippets |

Show, don't just tell. Concrete examples help users understand how to actually use the project.

---

## README Features

| Slug | Category | What it checks |
|------|----------|----------------|
| `readme-features` | Documentation | The README lists key features or capabilities |

A features section helps users quickly evaluate if the project meets their needs.
