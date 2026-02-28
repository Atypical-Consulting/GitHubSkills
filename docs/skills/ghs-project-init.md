# ghs-project-init

Scaffold a new GitHub repository with all quality essentials to achieve a 100% health score from ghs-repo-scan.

::: info Skill Info
**Version:** 1.0.0
**Trigger phrases:** "init project", "create repo", "scaffold repository", "new project", "project init", "bootstrap project", "create a 100% repo", "set up new repo", "start a new project"
:::

## What It Does

`ghs-project-init` creates a new GitHub repository (or scaffolds an existing empty one) with every file and setting that `ghs-repo-scan` checks. It uses the GSD framework for orchestrating the scaffolding pipeline, producing a repo that targets 100% on its first scan.

### Scope Boundary

**Creates new repositories and their initial files.** Does NOT modify existing repos with code, re-scan repos, or implement features.

### GSD Dependency

GSD is a **hard requirement** for this skill. The scaffolding pipeline is inherently multi-phase and benefits from GSD's structured execution, atomic commits, and verification guarantees. If GSD is not installed, the skill fails fast with install instructions.

### Process

1. **Parse input** — Extract repo name, owner, stack/visibility/license hints
2. **Pre-flight** — Check gh auth, GSD installed, repo name available
3. **Gather preferences** — Tech stack, license, visibility, description, topics, code owners
4. **Show plan** — Display all files to create, wait for confirmation
5. **Create repo** — `gh repo create` with clone
6. **GSD scaffolding** — Invoke GSD to generate all files in dependency order
7. **Push & configure** — Push commits, set API settings (description, topics, branch protection, merge strategy, labels)
8. **Verify** — Check all expected files exist and score the result

### Tech Stack Templates

| Stack | .gitignore | CI Workflow | README Badges | Dependency Config |
|-------|-----------|-------------|---------------|-------------------|
| .NET | VisualStudio | `dotnet build`, `dotnet test` | NuGet, .NET, Build | renovate.json (.NET preset) |
| Node.js | Node | `npm ci`, `npm test` | npm, Node, Build | renovate.json (Node preset) |
| Python | Python | `pip install`, `pytest` | PyPI, Python, Build | renovate.json (Python preset) |
| Rust | Rust | `cargo build`, `cargo test` | crates.io, Rust, Build | renovate.json (Rust preset) |
| Go | Go | `go build`, `go test ./...` | Go Reference, Build | renovate.json (Go preset) |
| Generic | Minimal (OS, IDE) | Basic lint/check | License, Build | renovate.json (base) |

### Files Created

#### Tier 1 --- Required (4 pts each)
- `README.md` --- Full README with description, badges, installation, usage, features, TOC, license
- `LICENSE` --- User-selected license file

#### Tier 2 --- Recommended (2 pts each)
- `.gitignore` --- Stack-tailored patterns
- `.github/workflows/ci.yml` --- CI pipeline with build, test, permissions, timeouts, concurrency
- `.editorconfig` --- Standard editor configuration
- `CODEOWNERS` --- Code ownership
- `.github/ISSUE_TEMPLATE/bug_report.yml` --- Bug report template
- `.github/ISSUE_TEMPLATE/feature_request.yml` --- Feature request template
- `.github/PULL_REQUEST_TEMPLATE.md` --- PR template
- `CHANGELOG.md` --- Keep a Changelog format

#### Tier 3 --- Nice to Have (1 pt each)
- `SECURITY.md` --- Security policy
- `CONTRIBUTING.md` --- Contribution guidelines
- `CODE_OF_CONDUCT.md` --- Contributor Covenant
- `.github/renovate.json` --- Dependency update config
- `.gitattributes` --- Git attributes for line endings

#### API Settings (no files)
- Repository description and topics
- Branch protection (after first push)
- Delete branch on merge
- Merge strategy (squash preferred)
- Standard labels (type, priority, status)

## Example

```
## Project Init: phmatray/my-api

Repository: https://github.com/phmatray/my-api
Visibility: public
License:    MIT
Stack:      .NET

### Files Created

#### Tier 1 --- Required
  [PASS] README.md
  [PASS] LICENSE (MIT)

#### Tier 2 --- Recommended
  [PASS] .gitignore (.NET)
  [PASS] .github/workflows/ci.yml
  [PASS] .editorconfig
  [PASS] CODEOWNERS
  [PASS] .github/ISSUE_TEMPLATE/bug_report.yml
  [PASS] .github/ISSUE_TEMPLATE/feature_request.yml
  [PASS] .github/PULL_REQUEST_TEMPLATE.md
  [PASS] CHANGELOG.md

#### Tier 3 --- Nice to Have
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
  Repository URL:   https://github.com/phmatray/my-api

To verify: /ghs-repo-scan phmatray/my-api
To view dashboard: /ghs-backlog-board
```

## Routes To

- **[ghs-repo-scan](/skills/ghs-repo-scan)** --- verify the new repo's health score
- **[ghs-backlog-board](/skills/ghs-backlog-board)** --- see the repo on the dashboard

## Technical Details

| Property | Value |
|----------|-------|
| Allowed tools | `Bash(gh:*)`, `Bash(git:*)`, `Bash(python3:*)`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, `Skill` |
| Spawns sub-agents | No --- delegates to GSD framework |
| Phases | 7 (Parse, Pre-flight, Preferences, Create, Scaffold, Configure, Verify) |
| Circuit breaker | 3 attempts per GSD phase, then NEEDS_HUMAN |
| Requires | `gh` CLI (authenticated), `git`, GSD framework, network access |
