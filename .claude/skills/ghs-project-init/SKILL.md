---
name: ghs-project-init
description: >
  Scaffold a new GitHub repository with all quality essentials to achieve a 100% health score from
  ghs-repo-scan. Creates the repo via `gh repo create`, generates all Tier 1/2/3 files tailored to
  the detected tech stack, configures repo settings via API, and verifies the result. For complex
  scaffolding (custom CI pipelines, monorepo setups), uses GSD framework for multi-phase execution.
  Use this skill whenever the user wants to create a new repo, scaffold a project, initialize a
  repository, bootstrap a project, or says things like "init project", "create repo", "scaffold
  repository", "new project", "project init", "initialize repo", "set up new repo", "bootstrap
  project", "create a 100% repo", "start a new project", or "create a perfect repo".
  Do NOT use for scanning existing repos (use ghs-repo-scan), fixing existing repos
  (use ghs-backlog-fix), or implementing issues (use ghs-issue-implement).
allowed-tools: "Bash(gh:*) Bash(git:*) Bash(python3:*) Read Write Edit Glob Grep Skill"
compatibility: "Requires gh CLI (authenticated), git, GSD framework, network access"
license: MIT
metadata:
  author: phmatray
  version: 1.0.0
routes-to:
  - ghs-repo-scan
  - ghs-backlog-board
routes-from: []
---

# Project Init

Scaffold a new GitHub repository with all quality essentials — Tier 1 (Required), Tier 2 (Recommended), and Tier 3 (Nice to Have) — tailored to the detected tech stack, targeting a 100% health score from `ghs-repo-scan`. Uses GSD framework for orchestrating the scaffolding pipeline.

<context>
Purpose: Create a new GitHub repository (or scaffold an existing empty one) with every file and setting that `ghs-repo-scan` checks, producing a repo that scores 100% on its first scan.

### Roles

| Role | Responsibility |
|------|---------------|
| **Orchestrator** (you) | Gather preferences, create repo, invoke GSD for file scaffolding, apply API-only settings, run verification |
| **GSD Pipeline** | Generates all files in phases via `/gsd:new-project`, handles wave-based execution |

### Shared References

| Reference | Path | Use For |
|-----------|------|---------|
| GSD integration | `../shared/references/gsd-integration.md` | GSD detection, command patterns, skill-to-GSD contract |
| gh CLI patterns | `../shared/references/gh-cli-patterns.md` | Repo creation, labels, branch protection, error handling |
| Scoring logic | `../shared/references/scoring-logic.md` | Tier definitions, what ghs-repo-scan checks for 100% |
| Output conventions | `../shared/references/output-conventions.md` | Status indicators, table formats, summary blocks |
| Backlog format | `../shared/references/backlog-format.md` | Health check items — what the scan expects to find |
| Core checks | `../shared/checks/core/index.md` | Full list of 40 core checks with tier assignments |

### GSD Dependency

GSD is a **hard dependency** for this skill. The scaffolding pipeline is inherently multi-phase (file generation, API settings, verification) and benefits from GSD's structured execution, atomic commits, and verification guarantees. If GSD is not installed, fail fast with install instructions.
</context>

<anti-patterns>

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Scaffold without asking tech stack | Detect or ask for tech stack before generating any files | .gitignore, CI workflow, README badges, and dependency config all depend on the stack |
| Hardcode file contents | Use templates tailored to the detected stack | A Python .gitignore in a Rust project wastes the user's time and looks sloppy |
| Skip branch protection setup | Always configure branch protection after first push | Branch protection is a Tier 1 check — skipping it guarantees a non-100% score |
| Create repo without confirming visibility | Always ask or confirm public/private before `gh repo create` | Accidentally public repos leak private code; accidentally private repos miss community features |
| Assume MIT license | Always ask or check user preference for license type | Wrong license has legal consequences — never default silently |
| Skip GSD detection pre-flight | Check for GSD before starting scaffolding | Failing mid-scaffold leaves a half-initialized repo |
| Create repo if name already taken | Check availability first with `gh repo view` | `gh repo create` on an existing name either fails or clones — both confuse the user |
| Generate files without explaining what each does | Show the scaffold plan with all files listed before proceeding | Users need to understand and approve what's being created in their repo |
| Skip the initial commit and push before setting branch protection | Commit and push first, then set branch protection | Branch protection requires at least one commit on the default branch |

</anti-patterns>

## Scope Boundary

This skill **creates new repositories and their initial files**. It does NOT:
- Modify existing repositories with code (use `ghs-backlog-fix` instead)
- Re-scan repositories (use `ghs-repo-scan` instead)
- Implement features or fix bugs (use `ghs-issue-implement` instead)

The sole write actions are:
1. Creating a new GitHub repo (or scaffolding an existing empty one)
2. Generating and committing files to the repo
3. Configuring repo settings via the GitHub API (description, topics, branch protection, delete-branch-on-merge, merge strategy)

## Context Budget

What to pass to GSD:

| Pass | Do NOT Pass |
|------|-------------|
| Repo name, owner, visibility | Other repos' backlog data |
| Tech stack (language, framework, test runner) | Scan results from other repos |
| License type | User's full GitHub profile |
| Description and topics | Unrelated project context |
| Code owners list | Previous session history |
| User preferences (collected in Phase 3) | Health check implementation details |

## Circuit Breaker

| Attempt | Action |
|---------|--------|
| 1st failure | Re-run GSD phase with error context |
| 2nd failure | Re-run with explicit file list and constraints |
| 3rd failure | Mark as NEEDS_HUMAN, report what was created and what remains |

<objective>
Scaffold a new GitHub repository that achieves 100% on ghs-repo-scan.

Outputs:
- New GitHub repository (or scaffolded existing empty repo)
- All Tier 1/2/3 files committed and pushed
- API settings configured (description, topics, branch protection, merge strategy, delete-branch-on-merge)
- Terminal report with health score verification and repo URL

Next routing:
- Suggest `ghs-repo-scan` to verify — "To verify: `/ghs-repo-scan {owner}/{repo}`"
- Suggest `ghs-backlog-board` to see it on the dashboard — "To view: `/ghs-backlog-board`"
</objective>

## Input

### Invocation Modes

| Trigger | Mode | Behavior |
|---------|------|----------|
| `init project {name}` | New repo | Create repo + scaffold all files |
| `scaffold repo {owner}/{repo}` | Existing empty repo | Scaffold files into existing repo |
| `create a 100% repo` | Interactive | Ask for name, then proceed |
| `bootstrap project {name} --stack dotnet` | With stack hint | Skip stack detection, use provided stack |

### Rule/Trigger/Example Triples

**Rule:** A repo name without owner defaults to the authenticated user's account.
**Trigger:** User says "init project my-app".
**Example:** Resolve owner via `gh api user --jq '.login'` -> `phmatray/my-app`.

**Rule:** If the user specifies a tech stack, skip detection.
**Trigger:** User says "create repo my-api --stack python".
**Example:** Use Python templates for .gitignore, CI, README badges.

**Rule:** If the repo already exists and has commits, refuse and suggest ghs-backlog-fix.
**Trigger:** User says "scaffold repo phmatray/existing-project" and it has commits.
**Example:** Warn: "This repo has existing commits. Use `/ghs-backlog-fix` to improve it instead."

**Rule:** Visibility must be explicitly confirmed before repo creation.
**Trigger:** User says "create repo my-tool" without specifying visibility.
**Example:** Ask: "Public or private? (default: public)"

<process>

### Phase 1 — Parse Input & Pre-flight Checks

**Step 1: Parse invocation**

Extract from user input:
- Repo name (required)
- Owner (optional — default to authenticated user)
- Tech stack hint (optional)
- Visibility hint (optional)
- License hint (optional)

**Step 2: Pre-flight checks**

| Check | Command | On Failure |
|-------|---------|------------|
| gh authenticated | `gh auth status` | Stop: "Run `gh auth login` first" |
| GSD installed | `ls ~/.claude/commands/gsd:* 2>/dev/null \|\| ls ~/.claude/plugins/*/skills/gsd-*/SKILL.md 2>/dev/null` | Stop: "[ERROR] GSD framework required. Install: https://github.com/gsd-build/get-shit-done" |
| git available | `git --version` | Stop: "git is required" |
| Repo name available | `gh repo view {owner}/{repo} 2>&1` | If exists + has commits: "Repo exists with commits — use `/ghs-backlog-fix`". If exists + empty: proceed in scaffold mode |

**Step 3: Resolve owner**

```bash
# If no owner specified, use authenticated user
gh api user --jq '.login'
```

### Phase 2 — Gather Preferences

Collect all preferences before any creation. Ask the user (with sensible defaults):

| Preference | Default | Options |
|-----------|---------|---------|
| **Tech stack** | Auto-detect or ask | .NET, Node.js, Python, Rust, Go, Generic |
| **License** | MIT | MIT, Apache-2.0, GPL-3.0, BSD-2-Clause, BSD-3-Clause, LGPL-3.0, MPL-2.0, Unlicense |
| **Visibility** | public | public, private |
| **Description** | Ask (required) | Free text |
| **Topics** | Suggest based on stack | Comma-separated |
| **Code owners** | `@{owner}` | Space-separated GitHub usernames |
| **CI provider** | GitHub Actions | GitHub Actions (only supported provider) |

**Display collected preferences:**

```
## Scaffold Plan: {owner}/{repo}

Visibility:  {public|private}
License:     {license}
Tech Stack:  {stack}
Description: {description}
Topics:      {topics}
Code Owners: {owners}

### Files to Create

#### Tier 1 — Required (4 pts each)
  [ ] README.md — Project readme with description, badges, installation, usage, features, TOC, license mention
  [ ] LICENSE — {license_type} license file

#### Tier 2 — Recommended (2 pts each)
  [ ] .gitignore — Tailored to {stack}
  [ ] .github/workflows/ci.yml — CI pipeline for {stack}
  [ ] .editorconfig — Standard editor configuration
  [ ] CODEOWNERS — Code ownership: {owners}
  [ ] .github/ISSUE_TEMPLATE/bug_report.yml — Bug report template
  [ ] .github/ISSUE_TEMPLATE/feature_request.yml — Feature request template
  [ ] .github/PULL_REQUEST_TEMPLATE.md — PR template
  [ ] CHANGELOG.md — Keep a Changelog format

#### Tier 3 — Nice to Have (1 pt each)
  [ ] SECURITY.md — Security policy
  [ ] CONTRIBUTING.md — Contribution guidelines
  [ ] CODE_OF_CONDUCT.md — Contributor Covenant
  [ ] .github/renovate.json — Dependency update config
  [ ] .gitattributes — Git attributes for line endings

#### API Settings (no file — configured via gh CLI)
  [ ] Repository description
  [ ] Repository topics
  [ ] Branch protection (after first push)
  [ ] Delete branch on merge
  [ ] Merge strategy (squash preferred)

Proceed? (y/n)
```

Wait for user confirmation before continuing.

### Phase 3 — Create GitHub Repository

**New repo mode:**

```bash
gh repo create {owner}/{repo} \
  --{visibility} \
  --description "{description}" \
  --clone
```

This creates the repo and clones it locally.

**Existing empty repo mode:**

```bash
# Clone the existing empty repo
git clone https://github.com/{owner}/{repo}.git repos/{owner}_{repo}
```

Change into the repo directory for all subsequent operations.

### Phase 4 — GSD Scaffolding Pipeline

**Step 1: Prepare GSD context**

Create `.planning/` directory in the repo:

```bash
mkdir -p .planning
```

Write `.planning/PROJECT.md`:

```markdown
# {repo} — Project Initialization

## Project Context
- **Repository**: {owner}/{repo}
- **Tech Stack**: {stack}
- **License**: {license}
- **Visibility**: {visibility}

## Scaffold Requirements
Generate all files needed for a 100% ghs-repo-scan health score.

### Files to Generate
{list all files from the scaffold plan}

### Tech Stack Templates
Use {stack}-specific templates for:
- .gitignore patterns
- CI/CD workflow (build, test, lint steps)
- README badges
- Dependency management config

### Quality Requirements
- README must include: description, badges, installation, usage, features, table of contents, license section
- CI workflow must: build, test, have proper permissions, use pinned action versions, include timeout and concurrency
- All templates must be production-quality, not placeholder stubs
```

**Step 2: Execute GSD pipeline**

Invoke GSD for the scaffolding:

```
/gsd:new-project
```

GSD handles:
1. File generation in dependency order
2. Atomic commits per logical group
3. Quality verification of generated content

**Step 3: Post-GSD review**

After GSD completes, verify all expected files were created:

```bash
# Check all expected files exist
ls -la README.md LICENSE .gitignore .editorconfig CODEOWNERS \
  CONTRIBUTING.md SECURITY.md CODE_OF_CONDUCT.md CHANGELOG.md \
  .gitattributes .github/workflows/ci.yml \
  .github/ISSUE_TEMPLATE/bug_report.yml \
  .github/ISSUE_TEMPLATE/feature_request.yml \
  .github/PULL_REQUEST_TEMPLATE.md \
  .github/renovate.json 2>&1
```

If any files are missing, generate them directly (GSD fallback).

### Phase 5 — Push & Configure API Settings

**Step 1: Push all commits**

```bash
git push -u origin main
```

**Step 2: Configure repo settings via API**

These are settings that cannot be set via files — they require the GitHub API:

```bash
# Set description and topics (if not already set by gh repo create)
gh repo edit {owner}/{repo} --description "{description}"
gh repo edit {owner}/{repo} --add-topic "{topic1}" --add-topic "{topic2}"

# Enable delete branch on merge
gh repo edit {owner}/{repo} --delete-branch-on-merge

# Set merge strategy (enable squash, disable merge commit and rebase)
gh api repos/{owner}/{repo} -X PATCH \
  -f allow_squash_merge=true \
  -f allow_merge_commit=true \
  -f allow_rebase_merge=false \
  -f squash_merge_commit_title="PR_TITLE" \
  -f squash_merge_commit_message="PR_BODY"

# Branch protection (requires at least one commit on main)
gh api repos/{owner}/{repo}/branches/main/protection -X PUT \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["ci"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": null,
  "restrictions": null
}
EOF
```

**Solo vs Team repo adjustment:** If the repo is personal (not org) and has a single owner, skip `required_pull_request_reviews` (solo devs can't review their own PRs). See `../shared/references/gh-cli-patterns.md` § Solo vs Team Repo.

**Step 3: Create standard labels**

```bash
# Type labels
gh label create "type:bug" --color "d73a4a" --description "Something isn't working" --repo {owner}/{repo} 2>&1 || true
gh label create "type:feature" --color "a2eeef" --description "New feature or request" --repo {owner}/{repo} 2>&1 || true
gh label create "type:docs" --color "0075ca" --description "Documentation improvements" --repo {owner}/{repo} 2>&1 || true
gh label create "type:chore" --color "e4e669" --description "Maintenance and housekeeping" --repo {owner}/{repo} 2>&1 || true

# Priority labels
gh label create "priority:critical" --color "b60205" --description "Must be fixed immediately" --repo {owner}/{repo} 2>&1 || true
gh label create "priority:high" --color "d93f0b" --description "Should be fixed soon" --repo {owner}/{repo} 2>&1 || true
gh label create "priority:medium" --color "fbca04" --description "Normal priority" --repo {owner}/{repo} 2>&1 || true
gh label create "priority:low" --color "0e8a16" --description "Nice to have" --repo {owner}/{repo} 2>&1 || true

# Status labels
gh label create "status:triaged" --color "c5def5" --description "Issue has been triaged" --repo {owner}/{repo} 2>&1 || true
gh label create "status:in-progress" --color "006b75" --description "Work in progress" --repo {owner}/{repo} 2>&1 || true
```

### Phase 6 — Verification

Run the health check logic to confirm the score. Check each item that `ghs-repo-scan` would check:

#### Tier 1 — Required (4 pts each, 16 pts total)

| Check | Slug | Verification | What This Skill Creates |
|-------|------|-------------|------------------------|
| README | `readme` | File exists, has content | Full README with description, badges, installation, usage, features, TOC, license |
| LICENSE | `license` | File exists, recognized license | User-selected license (MIT, Apache-2.0, etc.) |
| Description | `description` | Repo has description set | Set via `gh repo edit --description` |
| Branch Protection | `branch-protection` | API returns protection rules | Configured via `gh api` after first push |

#### Tier 2 — Recommended (2 pts each, 44 pts total)

| Check | Slug | Verification | What This Skill Creates |
|-------|------|-------------|------------------------|
| .gitignore | `gitignore` | File exists | Stack-tailored .gitignore |
| CI/CD Workflows | `ci-cd-workflows` | `.github/workflows/*.yml` exists | `ci.yml` for detected stack |
| CI Workflow Health | `ci-workflow-health` | Latest CI run passes | Fresh workflow — first run should pass |
| Action Version Pinning | `action-version-pinning` | Actions use `@vN` or SHA | Pinned versions in generated workflow |
| Workflow Permissions | `workflow-permissions` | `permissions:` key present | `permissions: read-all` in workflow |
| .editorconfig | `editorconfig` | File exists | Standard .editorconfig |
| CODEOWNERS | `codeowners` | File exists | CODEOWNERS with specified owners |
| Issue Templates | `issue-templates` | `.github/ISSUE_TEMPLATE/` exists with files | Bug report + feature request YAML templates |
| PR Template | `pr-template` | `.github/PULL_REQUEST_TEMPLATE.md` exists | Standard PR template |
| Topics | `topics` | Repo has at least 1 topic | Set via `gh repo edit --add-topic` |
| Changelog | `changelog` | CHANGELOG.md exists | Keep a Changelog format |
| Delete Branch on Merge | `delete-branch-on-merge` | Setting enabled | Set via `gh repo edit --delete-branch-on-merge` |
| GitHub Releases | `github-releases` | At least 1 release exists | **Not created** — WARN (new repo, no release yet) |
| Stale Issues | `stale-issues` | No issues older than 90 days | PASS (new repo, no issues) |
| Stale PRs | `stale-prs` | No PRs older than 30 days | PASS (new repo, no PRs) |
| Stale Branches | `stale-branches` | No branches older than 90 days | PASS (new repo, fresh branches) |
| Merge Strategy | `merge-strategy` | Squash merge configured | Set via API |
| README Description | `readme-description` | README has description section | Included in generated README |
| README Badges | `readme-badges` | README has badge images | Stack-specific badges in README |
| README Installation | `readme-installation` | README has installation section | Included in generated README |
| README Usage | `readme-usage` | README has usage/examples section | Included in generated README |
| README Features | `readme-features` | README has features section | Included in generated README |

#### Tier 3 — Nice to Have (1 pt each, 14 pts total)

| Check | Slug | Verification | What This Skill Creates |
|-------|------|-------------|------------------------|
| Workflow Naming | `workflow-naming` | Workflow has human-readable `name:` | `name: CI` in workflow |
| Workflow Timeouts | `workflow-timeouts` | `timeout-minutes:` present | Timeout in generated workflow |
| Workflow Concurrency | `workflow-concurrency` | `concurrency:` key present | Concurrency group in workflow |
| SECURITY.md | `security-md` | File exists | Security policy file |
| CONTRIBUTING.md | `contributing-md` | File exists | Contribution guidelines |
| Security Alerts | `security-alerts` | Renovate/Dependabot configured | renovate.json generated |
| .editorconfig Drift | `editorconfig-drift` | Files match .editorconfig rules | Fresh files — no drift possible |
| Code of Conduct | `code-of-conduct` | File exists | Contributor Covenant |
| Homepage URL | `homepage-url` | Repo has homepage set | **Not set** — user should set manually if needed |
| .gitattributes | `gitattributes` | File exists | Git attributes for line endings |
| Version Pinning | `version-pinning` | Lock files present (if applicable) | Generated by stack setup if applicable |
| Dependency Update Config | `dependency-update-config` | renovate.json or dependabot.yml exists | renovate.json |
| README TOC | `readme-toc` | README has table of contents | TOC section in generated README |
| README License Mention | `readme-license-mention` | README mentions the license | License section in generated README |

#### INFO-only Checks (no points)

| Check | Slug | Notes |
|-------|------|-------|
| Funding | `funding` | Not created — optional, user-specific |
| Discussions Enabled | `discussions-enabled` | Not enabled — user preference |
| Commit Signoff | `commit-signoff` | Not enabled — user preference |

**Expected score:** 74/74 (100%) for core checks, excluding GitHub Releases (WARN for new repo — no release yet) and Homepage URL (user-specific). Actual achievable score: ~70/72 (97%+) on first scan.

### Phase 7 — Terminal Output

```
## Project Init: {owner}/{repo}

Repository: https://github.com/{owner}/{repo}
Visibility: {public|private}
License:    {license}
Stack:      {stack}

### Files Created

#### Tier 1 — Required
  [PASS] README.md
  [PASS] LICENSE ({license_type})

#### Tier 2 — Recommended
  [PASS] .gitignore ({stack})
  [PASS] .github/workflows/ci.yml
  [PASS] .editorconfig
  [PASS] CODEOWNERS
  [PASS] .github/ISSUE_TEMPLATE/bug_report.yml
  [PASS] .github/ISSUE_TEMPLATE/feature_request.yml
  [PASS] .github/PULL_REQUEST_TEMPLATE.md
  [PASS] CHANGELOG.md

#### Tier 3 — Nice to Have
  [PASS] SECURITY.md
  [PASS] CONTRIBUTING.md
  [PASS] CODE_OF_CONDUCT.md
  [PASS] .github/renovate.json
  [PASS] .gitattributes

### API Settings
  [PASS] Description set
  [PASS] Topics set: {topics}
  [PASS] Branch protection enabled
  [PASS] Delete branch on merge enabled
  [PASS] Merge strategy configured (squash)
  [PASS] Labels created (type, priority, status)

---

### Health Score: {earned}/{possible} ({percentage}%)

  Tier 1:  {t1_earned}/{t1_possible}  {bar} ({t1_pct}%)
  Tier 2:  {t2_earned}/{t2_possible}  {bar} ({t2_pct}%)
  Tier 3:  {t3_earned}/{t3_possible}  {bar} ({t3_pct}%)

Summary:
  Files created:    {count}
  API settings:     {count}
  Labels created:   {count}
  Health score:     {earned}/{possible} ({percentage}%)
  Repository URL:   https://github.com/{owner}/{repo}

To verify: /ghs-repo-scan {owner}/{repo}
To view dashboard: /ghs-backlog-board
```

</process>

## Tech Stack Templates

| Stack | .gitignore | CI Workflow | README Badges | Dependency Config |
|-------|-----------|-------------|---------------|-------------------|
| .NET | VisualStudio.gitignore | `dotnet build`, `dotnet test` | NuGet, .NET version, Build Status | renovate.json with .NET preset |
| Node.js | Node.gitignore | `npm ci`, `npm test` | npm, Node version, Build Status | renovate.json with Node preset |
| Python | Python.gitignore | `pip install`, `pytest` | PyPI, Python version, Build Status | renovate.json with Python preset |
| Rust | Rust.gitignore | `cargo build`, `cargo test` | crates.io, Rust version, Build Status | renovate.json with Rust preset |
| Go | Go.gitignore | `go build`, `go test ./...` | Go Reference, Build Status | renovate.json with Go preset |
| Generic | Minimal (OS files, IDE) | Basic lint/check | License, Build Status | renovate.json (base config) |

### CI Workflow Requirements

Every generated CI workflow must include these elements to pass all CI-related health checks:

| Element | Check It Satisfies | Example |
|---------|-------------------|---------|
| `name: CI` | `workflow-naming` | Human-readable name |
| `permissions: read-all` | `workflow-permissions` | Least-privilege permissions |
| `timeout-minutes: 15` | `workflow-timeouts` | Prevents stuck jobs |
| `concurrency:` group | `workflow-concurrency` | Prevents redundant runs |
| Actions pinned to `@vN` | `action-version-pinning` | `actions/checkout@v4` |
| Build + test steps | `ci-cd-workflows` | Stack-specific commands |

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| Repo name already taken | Check with `gh repo view` first; if taken, report error and suggest a different name |
| User has no org permissions | Fall back to personal account; inform the user |
| GSD not installed | Fail fast: `[ERROR] GSD framework required. Install: https://github.com/gsd-build/get-shit-done` |
| Existing repo not empty | Warn: "Repo has existing commits — use `/ghs-backlog-fix` to improve it instead" |
| User wants monorepo | Note limitation: "This skill scaffolds single-project repos. For monorepos, scaffold the root and add sub-projects manually" |
| User cancels mid-scaffold | GSD handles via `/gsd:pause-work`; partial state is preserved in `.planning/` |
| Branch protection fails (not admin) | Report as `[WARN]` — "Branch protection requires admin access. Ask a repo admin to configure it" |
| Private repo — skip community files? | No — still create all files. They're useful if the repo is ever made public |
| Rate limiting during API setup | Pause and report; user can re-run to complete API settings |
| gh repo create fails | Check error: name conflict, quota, permissions. Report clearly |

## Examples

**Example 1: Create a .NET project**

User: "init project my-api --stack dotnet"

Flow: Pre-flight (gh auth, GSD, name available) -> gather preferences (license: MIT, visibility: public, description, topics) -> show plan -> create repo -> GSD scaffolds all files with .NET templates -> push -> API settings (description, topics, branch protection, merge strategy) -> verify -> report with 97%+ score.

**Example 2: Create a generic project interactively**

User: "create a 100% repo"

Flow: Ask for repo name -> pre-flight -> ask for stack (user picks "Generic") -> ask for license (user picks Apache-2.0) -> ask for visibility -> ask for description and topics -> show full plan -> confirm -> create repo -> GSD scaffolds -> push -> API settings -> verify -> report.

**Example 3: Scaffold an existing empty repo**

User: "scaffold repo phmatray/empty-project"

Flow: Pre-flight (repo exists, no commits) -> detect stack from user input -> gather preferences -> show plan -> clone repo -> GSD scaffolds -> push -> API settings -> verify -> report.

**Good output example:**

```
## Project Init: phmatray/my-api

Repository: https://github.com/phmatray/my-api
Visibility: public
License:    MIT
Stack:      .NET

### Files Created

#### Tier 1 — Required
  [PASS] README.md
  [PASS] LICENSE (MIT)

#### Tier 2 — Recommended
  [PASS] .gitignore (.NET)
  [PASS] .github/workflows/ci.yml
  [PASS] .editorconfig
  [PASS] CODEOWNERS
  [PASS] .github/ISSUE_TEMPLATE/bug_report.yml
  [PASS] .github/ISSUE_TEMPLATE/feature_request.yml
  [PASS] .github/PULL_REQUEST_TEMPLATE.md
  [PASS] CHANGELOG.md

#### Tier 3 — Nice to Have
  [PASS] SECURITY.md
  [PASS] CONTRIBUTING.md
  [PASS] CODE_OF_CONDUCT.md
  [PASS] .github/renovate.json
  [PASS] .gitattributes

### API Settings
  [PASS] Description set
  [PASS] Topics set: dotnet, api, csharp
  [PASS] Branch protection enabled
  [PASS] Delete branch on merge enabled
  [PASS] Merge strategy configured (squash)
  [PASS] Labels created (10)

---

### Health Score: 70/72 (97%)

  Tier 1:  16/16  ████████ (100%)
  Tier 2:  40/42  ████████ (95%)
  Tier 3:  14/14  ████████ (100%)

Summary:
  Files created:    15
  API settings:     5
  Labels created:   10
  Health score:     70/72 (97%)
  Repository URL:   https://github.com/phmatray/my-api

To verify: /ghs-repo-scan phmatray/my-api
To view dashboard: /ghs-backlog-board
```

**Bad output example:**

```
Created repo. Added some files. Done.
```

This is bad because: no file list, no score verification, no URL, no next steps, no indication of what was configured.
