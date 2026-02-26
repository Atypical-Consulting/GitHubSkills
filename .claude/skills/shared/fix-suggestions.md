# Fix Suggestions per Health Check

Per-check fix strategies including quick fixes, full solutions, acceptance criteria, and special notes. Consumed by: repo-scan (when generating "How to Fix" sections), apply-backlog-item (when planning and executing fixes).

## Table of Contents

1. [README](#readme-tier-1--4-points)
2. [LICENSE](#license-tier-1--4-points)
3. [Description](#description-tier-1--4-points)
4. [Branch Protection](#branch-protection-tier-1--4-points)
5. [.gitignore](#gitignore-tier-2--2-points)
6. [CI/CD Workflows](#cicd-workflows-tier-2--2-points)
7. [CI Workflow Health](#ci-workflow-health-tier-2--2-points)
8. [.editorconfig](#editorconfig-tier-2--2-points)
9. [CODEOWNERS](#codeowners-tier-2--2-points)
10. [Issue Templates](#issue-templates-tier-2--2-points)
11. [PR Template](#pr-template-tier-2--2-points)
12. [Topics](#topics-tier-2--2-points)
13. [SECURITY.md](#securitymd-tier-3--1-point)
14. [CONTRIBUTING.md](#contributingmd-tier-3--1-point)
15. [Security Alerts](#security-alerts-tier-3--1-point)
16. [.editorconfig Drift](#editorconfig-drift-tier-3--1-point)
17. [Funding](#funding-tier-3--info-only)

---

## README (Tier 1 -- 4 points)

### Quick Fix

```bash
echo "# {repo}\n\nDescription of the project." > README.md
```

### Full Solution

Generate a substantive README tailored to the repository. Use the detected tech stack, project structure, and license to produce real content -- not a generic stub. A good README includes:

- **Project title and description**: What the project does and why it exists.
- **Getting Started**: Prerequisites, installation, and first-run instructions matching the tech stack.
- **Usage**: Key commands, API examples, or screenshots.
- **Contributing**: Link to CONTRIBUTING.md if it exists, or a brief note.
- **License**: State the license type and link to the LICENSE file.

For .NET projects, include `dotnet build` / `dotnet run` instructions. For Node.js, include `npm install` / `npm start`. Match the tech stack.

### Acceptance Criteria

- [ ] `README.md` exists in the repository root
- [ ] File size is greater than 500 bytes

### Notes

- The quick fix is only for unblocking -- always prefer the full solution for real projects.
- Inspect existing files (source code, configs, other docs) to infer the project's purpose. Do not use placeholder text.

---

## LICENSE (Tier 1 -- 4 points)

### Quick Fix

```bash
curl -o LICENSE https://choosealicense.com/licenses/mit/
```

Adjust the URL for the appropriate license type. Common options:
- MIT: `https://choosealicense.com/licenses/mit/`
- Apache 2.0: `https://choosealicense.com/licenses/apache-2.0/`
- GPL 3.0: `https://choosealicense.com/licenses/gpl-3.0/`

### Full Solution

1. Determine the appropriate license. If the repo already has license hints (e.g., a `<PackageLicenseExpression>` in a .csproj, a `license` field in package.json), use that.
2. Download the license text from choosealicense.com or GitHub's license API.
3. Replace placeholder fields (year, author name) with actual values from the repo owner's profile.

### Acceptance Criteria

- [ ] `LICENSE` file exists in the repository root
- [ ] File contains a recognized open-source license

### Notes

- If unsure which license to use, suggest MIT as a safe default and let the user choose.
- Some licenses require the copyright holder name and year -- fill these in rather than leaving placeholders.

---

## Description (Tier 1 -- 4 points)

### Quick Fix

```bash
gh repo edit {owner}/{repo} --description "Your project description here"
```

### Full Solution

Craft a meaningful one-line description by inspecting the repository:
- Read the README (if it exists) for a summary.
- Check package.json `description`, .csproj `<Description>`, Cargo.toml `description`, or pyproject.toml `description`.
- Look at the repo name and directory structure for clues.

The description should be concise (under 350 characters), informative, and avoid generic phrases like "A project" or "My repo".

### Acceptance Criteria

- [ ] Repository description is a non-empty string
- [ ] Description is meaningful and accurately reflects the project

### Notes

- This is an **API-only fix** -- no file changes or PR needed.
- The `gh repo edit` command updates the description immediately.

---

## Branch Protection (Tier 1 -- 4 points)

### Quick Fix

```bash
gh api repos/{owner}/{repo}/branches/{default_branch}/protection \
  -X PUT \
  --input - <<'EOF'
{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

### Full Solution

The configuration depends on whether the repo is solo-maintained or team-based.

#### Solo maintainer repos

Detect: single collaborator, or `owner.type` is `User` with no additional collaborators.

Use a **lightweight configuration**:

```json
{
  "required_status_checks": null,
  "enforce_admins": true,
  "required_pull_request_reviews": null,
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

Key point: `required_pull_request_reviews` is set to `null`. Requiring PR approvals would lock the sole maintainer out of merging their own PRs, since there is no one else to approve.

#### Team repos

Detect: 2+ collaborators, or org-owned repository.

Use a **full configuration**:

```json
{
  "required_status_checks": {
    "strict": true,
    "contexts": []
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1,
    "dismiss_stale_reviews": true
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
```

If CI/CD workflows exist, populate `contexts` with detected status check names.

### Acceptance Criteria

- [ ] Branch protection API returns 200 for the default branch
- [ ] Force pushes are blocked
- [ ] Admins are included in enforcement

### Notes

- This is an **API-only fix** -- no file changes or PR needed.
- Requires admin access to the repository. If the user is not an admin, the API will return 403.
- If the default branch name is unusual (e.g., `develop`), consider noting that renaming to `main` is a common best practice.

---

## .gitignore (Tier 2 -- 2 points)

### Quick Fix

```bash
curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/{Template}.gitignore
```

### Full Solution

Select the template based on the detected tech stack:

| Tech Stack | Template |
|-----------|----------|
| .NET | `VisualStudio.gitignore` |
| Node.js | `Node.gitignore` |
| Python | `Python.gitignore` |
| Rust | `Rust.gitignore` |
| Go | `Go.gitignore` |
| Java (Maven) | `Maven.gitignore` |
| Java (Gradle) | `Gradle.gitignore` |
| Ruby | `Ruby.gitignore` |
| PHP | `Composer.gitignore` |

For multi-stack repos, concatenate the relevant templates with clear section headers.

If no tech stack is detected, use a minimal `.gitignore` covering common OS and editor files:

```gitignore
# OS files
.DS_Store
Thumbs.db

# Editor files
.vscode/
.idea/
*.swp
*.swo
```

### Acceptance Criteria

- [ ] `.gitignore` file exists in the repository root

### Notes

- Always inspect the repo for build artifacts or generated files that should be ignored beyond the standard template.

---

## CI/CD Workflows (Tier 2 -- 2 points)

### Quick Fix

Create `.github/workflows/ci.yml` with a starter workflow matching the tech stack.

### Full Solution

#### .NET

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'
      - run: dotnet restore
      - run: dotnet build --no-restore
      - run: dotnet test --no-build --verbosity normal
```

#### Node.js

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test
```

#### Python

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e ".[dev]"
      - run: pytest
```

#### Rust

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo build --verbose
      - run: cargo test --verbose
```

#### Go

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - run: go build ./...
      - run: go test ./...
```

Adjust the default branch name in `branches:` to match the actual default branch. Adjust language versions to match what the project actually uses (check config files for version hints).

### Acceptance Criteria

- [ ] At least one `.yml` or `.yaml` file exists in `.github/workflows/`
- [ ] The workflow includes build and test steps appropriate to the tech stack

### Notes

- If CI already exists but is broken, fixing it is out of scope for this check -- the check only verifies existence.
- For multi-stack repos, consider a single workflow with multiple jobs or a matrix strategy.

---

## CI Workflow Health (Tier 2 -- 2 points)

### Quick Fix

Investigate the failing workflow run and fix the root cause. Start by viewing the failure logs:

```bash
gh run list --repo {owner}/{repo} --status failure --limit 5
gh run view {run-id} --repo {owner}/{repo} --log-failed
```

### Full Solution

1. Identify which workflows are failing by checking the most recent run per workflow:
   ```bash
   gh run list --repo {owner}/{repo} --limit 20 --json conclusion,workflowName,status,databaseId
   ```
2. For each failing workflow, view the failed logs to diagnose the issue:
   ```bash
   gh run view {run-id} --repo {owner}/{repo} --log-failed
   ```
3. Common causes of CI failures:
   - **Outdated dependencies**: lock file out of sync, removed packages
   - **Broken tests**: flaky tests, missing test fixtures, environment differences
   - **Deprecated actions**: using `actions/checkout@v2` when `v4` is available
   - **Expired secrets/tokens**: API keys or tokens that need rotation
   - **Platform changes**: runtime version no longer available (e.g., Node 16 EOL)
4. Fix the root cause in the workflow file or the codebase, and push to trigger a re-run.

### Acceptance Criteria

- [ ] All workflows have their most recent completed run with a `success` or `skipped` conclusion
- [ ] No workflow has its latest completed run in `failure` state

### Notes

- This check looks at the most recent completed run per workflow, not all historical runs.
- If a workflow is intentionally broken or unused, consider deleting or disabling it rather than leaving it in a failed state.
- Workflow failures are often a sign of neglected maintenance — fixing them frequently uncovers other issues.

---

## .editorconfig (Tier 2 -- 2 points)

### Quick Fix

Copy the matching shared `.editorconfig` for the detected tech stack:

```bash
# For .NET projects:
cp {skills-path}/shared/editorconfigs/dotnet.editorconfig .editorconfig

# For JS/TS projects:
cp {skills-path}/shared/editorconfigs/javascript.editorconfig .editorconfig

# For Python projects:
cp {skills-path}/shared/editorconfigs/python.editorconfig .editorconfig
```

### Full Solution

Select the shared `.editorconfig` template based on the detected tech stack:

| Tech Stack | Shared Reference |
|-----------|-----------------|
| .NET (`.csproj`, `.sln`) | `shared/editorconfigs/dotnet.editorconfig` |
| JavaScript/TypeScript (`package.json`, `tsconfig.json`) | `shared/editorconfigs/javascript.editorconfig` |
| Python (`pyproject.toml`, `setup.py`) | `shared/editorconfigs/python.editorconfig` |
| Rust (`Cargo.toml`) | `shared/editorconfigs/rust.editorconfig` |
| Go (`go.mod`) | `shared/editorconfigs/go.editorconfig` |

For multi-stack repos, start with the primary language's template and merge relevant sections from others.

If no matching shared reference exists, create a minimal `.editorconfig`:

```ini
root = true

[*]
indent_style = space
indent_size = 4
end_of_line = lf
charset = utf-8
trim_trailing_whitespace = true
insert_final_newline = true

[*.md]
trim_trailing_whitespace = false
```

### Acceptance Criteria

- [ ] `.editorconfig` file exists in the repository root
- [ ] The file contains `root = true`

### Notes

- EditorConfig standardizes formatting across editors (VS Code, Rider, vim, etc.), reducing noise in diffs.
- Most editors have built-in or plugin support for `.editorconfig`.
- The shared references are stored in `.claude/skills/shared/editorconfigs/` and should be treated as the canonical style for each tech stack.

---

## CODEOWNERS (Tier 2 -- 2 points)

### Quick Fix

```bash
mkdir -p .github && echo "* @{owner}" > .github/CODEOWNERS
```

### Full Solution

A more granular CODEOWNERS file maps specific paths to owners:

```
# Default owner for everything
* @{owner}

# Examples for common patterns (adapt to repo structure):
# /docs/    @{owner}
# /src/     @{owner}
# *.md      @{owner}
```

For solo repos, `* @{owner}` is sufficient. For team repos, map directories to specific team members or teams if known.

### Acceptance Criteria

- [ ] `CODEOWNERS` file exists in one of the standard locations: root, `.github/`, or `docs/`

### Notes

- GitHub checks CODEOWNERS in this order: root, `docs/`, `.github/`. The `.github/` location is conventional.
- Invalid CODEOWNERS syntax (e.g., referencing non-existent teams) will cause GitHub to ignore the file silently.

---

## Issue Templates (Tier 2 -- 2 points)

### Quick Fix

```bash
mkdir -p .github/ISSUE_TEMPLATE
```

Then create the template files below.

### Full Solution

Create two starter templates:

#### `.github/ISSUE_TEMPLATE/bug_report.md`

```markdown
---
name: Bug Report
about: Report a bug to help us improve
title: '[Bug] '
labels: bug
assignees: ''
---

## Description

A clear description of the bug.

## Steps to Reproduce

1. Step one
2. Step two
3. Step three

## Expected Behavior

What you expected to happen.

## Actual Behavior

What actually happened.

## Environment

- OS: [e.g., Windows 11, macOS 14]
- Version: [e.g., 1.0.0]

## Additional Context

Any other context, screenshots, or logs.
```

#### `.github/ISSUE_TEMPLATE/feature_request.md`

```markdown
---
name: Feature Request
about: Suggest an idea for this project
title: '[Feature] '
labels: enhancement
assignees: ''
---

## Problem

A clear description of the problem this feature would solve.

## Proposed Solution

Your idea for how to solve it.

## Alternatives Considered

Any alternative solutions or features you've considered.

## Additional Context

Any other context, mockups, or examples.
```

### Acceptance Criteria

- [ ] `.github/ISSUE_TEMPLATE/` directory exists
- [ ] Directory contains at least one template file

### Notes

- You can also add a `config.yml` to the ISSUE_TEMPLATE directory to add blank issue options or external links.
- Template names and labels should match the project's existing conventions if any.

---

## PR Template (Tier 2 -- 2 points)

### Quick Fix

```bash
mkdir -p .github
```

Then create the template file below.

### Full Solution

Create `.github/pull_request_template.md`:

```markdown
## Summary

Brief description of what this PR does.

## Related Issue

Fixes #(issue number)

## Changes

- Change one
- Change two

## Checklist

- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have added tests that prove my fix or feature works
- [ ] New and existing tests pass locally
- [ ] I have updated the documentation accordingly
```

### Acceptance Criteria

- [ ] PR template exists in one of the standard locations: `.github/pull_request_template.md`, `.github/PULL_REQUEST_TEMPLATE.md`, or `.github/PULL_REQUEST_TEMPLATE/` directory

### Notes

- GitHub is case-insensitive for `pull_request_template.md` but `.github/pull_request_template.md` (lowercase) is the most common convention.
- The checklist items should be adapted to the project's actual requirements (e.g., add linting, type checking steps if relevant).

---

## Topics (Tier 2 -- 2 points)

### Quick Fix

```bash
gh repo edit {owner}/{repo} --add-topic {topic1} --add-topic {topic2}
```

### Full Solution

Suggest topics based on the detected tech stack and repository characteristics:

| Tech Stack | Suggested Topics |
|-----------|-----------------|
| .NET | `dotnet`, `csharp`, `netcore` |
| Node.js | `nodejs`, `javascript`, `typescript` (if tsconfig exists) |
| Python | `python`, `python3` |
| Rust | `rust`, `cargo` |
| Go | `golang`, `go` |

Also consider:
- The project type: `cli`, `library`, `api`, `web-app`, `tool`, `framework`
- The domain: `devtools`, `data`, `security`, `automation`
- The license: `open-source`, `mit-license`

Aim for 3-5 relevant topics. Avoid overly generic topics like `code` or `project`.

### Acceptance Criteria

- [ ] At least one topic is set on the repository

### Notes

- This is an **API-only fix** -- no file changes or PR needed.
- Topics improve discoverability on GitHub. They appear on the repo page and in GitHub search.

---

## SECURITY.md (Tier 3 -- 1 point)

### Quick Fix

Create `SECURITY.md` in the repository root.

### Full Solution

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| latest  | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please send an email to [{owner's email or security contact}] with:

- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You can expect an initial response within 48 hours. We will work with you to understand and address the issue before any public disclosure.

## Security Updates

Security updates will be released as patch versions. We recommend always using the latest version.
```

### Acceptance Criteria

- [ ] `SECURITY.md` exists in the repository root

### Notes

- If the repo owner has a security email, use it. Otherwise, use their GitHub profile email or a placeholder they can fill in.
- For org repos, there may be an org-level security policy. Check before creating a repo-level one.

---

## CONTRIBUTING.md (Tier 3 -- 1 point)

### Quick Fix

Create `CONTRIBUTING.md` in the repository root.

### Full Solution

Generate a CONTRIBUTING.md tailored to the detected tech stack:

```markdown
# Contributing to {repo}

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

1. Fork and clone the repository
2. Install dependencies:
   {tech-stack-specific instructions}
3. Create a branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Code Style

{tech-stack-specific style guidance, e.g., "Run `dotnet format` before committing" or "Follow PEP 8 guidelines"}

## Making Changes

1. Make your changes in a feature branch
2. Write or update tests as needed
3. Ensure all tests pass:
   {tech-stack-specific test command}
4. Commit your changes with a clear message

## Pull Request Process

1. Update documentation if your changes affect it
2. Ensure CI passes on your PR
3. Request a review from the maintainers
4. Address any review feedback

## Reporting Issues

- Use the GitHub issue tracker
- Check existing issues before creating a new one
- Use the provided issue templates when available

## Code of Conduct

Please be respectful and constructive in all interactions.
```

### Acceptance Criteria

- [ ] `CONTRIBUTING.md` exists in the repository root

### Notes

- Tailor the setup instructions to the actual tech stack. Do not use generic placeholder commands.
- If the project already has a code style enforcer (Prettier, ESLint, dotnet-format, Black), mention it explicitly.

---

## Security Alerts (Tier 3 -- 1 point)

### Quick Fix

```bash
gh api repos/{owner}/{repo}/vulnerability-alerts -X PUT
```

### Full Solution

Before suggesting dependency management changes, **detect the existing dependency manager**:

#### Detection

| Indicator | Tool Detected |
|-----------|--------------|
| `renovate.json` in repo root | **Renovate** |
| `.github/renovate.json` or `.github/renovate.json5` | **Renovate** |
| Open issue titled "Dependency Dashboard" | **Renovate** |
| `.github/dependabot.yml` | **Dependabot** |
| None of the above | No automated dependency management |

#### If Renovate is detected

- Enable GitHub vulnerability alerts (the quick fix above) for CVE notifications.
- Do **NOT** suggest adding `.github/dependabot.yml` or enabling Dependabot security updates. Renovate already handles dependency version update PRs, and running both tools creates duplicate PRs and confusion.
- Note in the backlog item: "Renovate handles dependency updates. GitHub vulnerability alerts provide CVE notifications independently."

#### If Dependabot is detected

- Enable vulnerability alerts if not already enabled.
- Dependabot is already configured. No additional action needed beyond ensuring alerts are active.

#### If no dependency manager is found

- Enable vulnerability alerts (quick fix).
- Optionally suggest adding `.github/dependabot.yml` for automated version updates:

```yaml
version: 2
updates:
  - package-ecosystem: "{ecosystem}"
    directory: "/"
    schedule:
      interval: "weekly"
```

Map ecosystems from the tech stack:

| Tech Stack | Ecosystem |
|-----------|-----------|
| .NET | `nuget` |
| Node.js | `npm` |
| Python | `pip` |
| Rust | `cargo` |
| Go | `gomod` |
| Java (Maven) | `maven` |
| Java (Gradle) | `gradle` |
| Ruby | `bundler` |
| PHP | `composer` |
| GitHub Actions | `github-actions` |

### Acceptance Criteria

- [ ] Vulnerability alerts are enabled (`gh api repos/{owner}/{repo}/vulnerability-alerts` returns 204)
- [ ] No open critical or high severity alerts

### Notes

- This check has **two parts**: alerts enabled (quick fix) and no open critical/high alerts (may require actual dependency updates).
- Enabling alerts is an API-only fix. Resolving open alerts may require dependency updates, which is a separate effort.
- The `vulnerability-alerts` endpoint requires admin access. If 403, report as WARN.

---

## .editorconfig Drift (Tier 3 -- 1 point)

### Quick Fix

Replace the repo's `.editorconfig` with the shared reference for the detected tech stack:

```bash
cp {skills-path}/shared/editorconfigs/{stack}.editorconfig .editorconfig
```

### Full Solution

1. Download the repo's current `.editorconfig` and compare it against the matching shared reference from `.claude/skills/shared/editorconfigs/`.
2. Review the diff to understand what's different — the repo may have intentional customizations.
3. If the differences are unintentional drift (e.g., inconsistent indentation settings, missing sections), replace with the shared reference.
4. If the repo has legitimate project-specific overrides, merge them into the shared reference as additional sections, keeping the shared base intact.

Tech stack detection for selecting the reference file:

| Indicator | Shared Reference |
|-----------|-----------------|
| `.csproj`, `.sln` | `dotnet.editorconfig` |
| `package.json`, `tsconfig.json` | `javascript.editorconfig` |
| `pyproject.toml`, `setup.py` | `python.editorconfig` |
| `Cargo.toml` | `rust.editorconfig` |
| `go.mod` | `go.editorconfig` |

### Acceptance Criteria

- [ ] `.editorconfig` content matches the shared reference for the detected tech stack
- [ ] Any project-specific overrides are documented with comments in the file

### Notes

- This check only runs if `.editorconfig` already exists — if it's missing, the Tier 2 `.editorconfig` check handles that.
- The shared references live in `.claude/skills/shared/editorconfigs/` and represent the canonical style per tech stack.
- When the repo has customizations that should be preserved, add them as additional sections after the shared base content, clearly commented.

---

## Funding (Tier 3 -- INFO only)

### Quick Fix

Create `.github/FUNDING.yml`:

```yaml
github: [{owner}]
```

### Full Solution

The FUNDING.yml file supports multiple platforms:

```yaml
github: [{owner}]
# patreon: username
# open_collective: project-name
# ko_fi: username
# custom: ["https://your-link.com"]
```

### Acceptance Criteria

- [ ] `.github/FUNDING.yml` exists

### Notes

- This is an **INFO-only check**. It carries no points and no penalty for missing.
- The funding file is purely optional and informational. Only suggest it if the user expresses interest in sponsorship.
- Do not auto-create this file during batch fixes unless the user explicitly asks for it.
