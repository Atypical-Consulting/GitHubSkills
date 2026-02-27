# Check Registry

GHS uses a **modular check system** with a core module (always active) and language-specific modules that activate based on stack detection. Currently **63 health checks** across 2 modules.

## Modules

| Module | Checks | Max Points | Activation |
|--------|--------|------------|------------|
| **Core** | 40 scored + 3 INFO | 74 | Always active |
| **.NET** | 20 scored + 3 INFO | 34 | `.sln` detected in repo root |

When a language module is active, scores are combined with weighted averaging:

```
Combined = core_pct x 60% + language_pct x 40%
```

If no language module is active, the core score is used at 100% weight.

## Core Checks

40 checks across 7 categories covering universal repository best practices.

### Scoring

| Tier | Checks | Points Each | Subtotal |
|------|--------|-------------|----------|
| Tier 1 — Required | 4 | 4 | 16 |
| Tier 2 — Recommended | 22 | 2 | 44 |
| Tier 3 — Nice to Have | 14 scored + 3 INFO | 1 | 14 |
| **Total** | **40 scored** | | **74** |

### All Core Checks

| # | Check | Slug | Tier | Category | Points |
|---|-------|------|------|----------|--------|
| 1 | README exists | `readme` | 1 | Documentation | 4 |
| 2 | LICENSE exists | `license` | 1 | Documentation | 4 |
| 3 | Repository description set | `description` | 1 | Repo Settings | 4 |
| 4 | Branch protection enabled | `branch-protection` | 1 | Repo Settings | 4 |
| 5 | .gitignore exists | `gitignore` | 2 | Dev Config | 2 |
| 6 | CI/CD workflows present | `ci-cd-workflows` | 2 | CI/CD | 2 |
| 7 | CI workflow health | `ci-workflow-health` | 2 | CI/CD | 2 |
| 8 | Action version pinning | `action-version-pinning` | 2 | CI/CD | 2 |
| 9 | Workflow permissions | `workflow-permissions` | 2 | CI/CD | 2 |
| 10 | .editorconfig exists | `editorconfig` | 2 | Dev Config | 2 |
| 11 | CODEOWNERS exists | `codeowners` | 2 | Dev Config | 2 |
| 12 | Issue templates configured | `issue-templates` | 2 | Community | 2 |
| 13 | PR template exists | `pr-template` | 2 | Community | 2 |
| 14 | Repository topics set | `topics` | 2 | Repo Settings | 2 |
| 15 | CHANGELOG exists | `changelog` | 2 | Documentation | 2 |
| 16 | Delete branch on merge | `delete-branch-on-merge` | 2 | Repo Settings | 2 |
| 17 | GitHub releases present | `github-releases` | 2 | Maintenance | 2 |
| 18 | No stale issues | `stale-issues` | 2 | Maintenance | 2 |
| 19 | No stale PRs | `stale-prs` | 2 | Maintenance | 2 |
| 20 | No stale branches | `stale-branches` | 2 | Maintenance | 2 |
| 21 | Merge strategy configured | `merge-strategy` | 2 | Repo Settings | 2 |
| 22 | README has description | `readme-description` | 2 | Documentation | 2 |
| 23 | README has badges | `readme-badges` | 2 | Documentation | 2 |
| 24 | README has installation | `readme-installation` | 2 | Documentation | 2 |
| 25 | README has usage section | `readme-usage` | 2 | Documentation | 2 |
| 26 | README has features section | `readme-features` | 2 | Documentation | 2 |
| 27 | Workflow naming | `workflow-naming` | 3 | CI/CD | 1 |
| 28 | Workflow timeouts | `workflow-timeouts` | 3 | CI/CD | 1 |
| 29 | Workflow concurrency | `workflow-concurrency` | 3 | CI/CD | 1 |
| 30 | SECURITY.md exists | `security-md` | 3 | Community | 1 |
| 31 | CONTRIBUTING.md exists | `contributing-md` | 3 | Documentation | 1 |
| 32 | Security alerts enabled | `security-alerts` | 3 | Security | 1 |
| 33 | .editorconfig drift | `editorconfig-drift` | 3 | Dev Config | 1 |
| 34 | Code of conduct | `code-of-conduct` | 3 | Documentation | 1 |
| 35 | Homepage URL set | `homepage-url` | 3 | Repo Settings | 1 |
| 36 | .gitattributes exists | `gitattributes` | 3 | Dev Config | 1 |
| 37 | Version pinning | `version-pinning` | 3 | Dev Config | 1 |
| 38 | Dependency update config | `dependency-update-config` | 3 | Security | 1 |
| 39 | README has table of contents | `readme-toc` | 3 | Documentation | 1 |
| 40 | README mentions license | `readme-license-mention` | 3 | Documentation | 1 |
| 41 | FUNDING.yml exists | `funding` | 3 | Documentation | INFO |
| 42 | Discussions enabled | `discussions-enabled` | 3 | Repo Settings | INFO |
| 43 | Commit signoff required | `commit-signoff` | 3 | Repo Settings | INFO |

### By Category

| Category | Checks | Description |
|----------|--------|-------------|
| **Documentation** | 13 | README, LICENSE, CHANGELOG, CONTRIBUTING, code of conduct, funding, and README content quality |
| **Repo Settings** | 8 | Description, branch protection, topics, delete-branch-on-merge, merge strategy, homepage URL, discussions, commit signoff |
| **Dev Config** | 6 | .gitignore, .editorconfig, CODEOWNERS, .editorconfig drift, .gitattributes, version pinning |
| **CI/CD** | 7 | Workflow presence, health, version pinning, permissions, naming, timeouts, concurrency |
| **Community** | 3 | Issue templates, PR template, SECURITY.md |
| **Security** | 2 | Security alerts, dependency update config |
| **Maintenance** | 4 | GitHub releases, stale issues, stale PRs, stale branches |

## .NET Module Checks

23 checks across 4 categories for .NET-specific best practices. Activates when a `.sln` file is detected in the repository root.

### Scoring

| Tier | Checks | Points Each | Subtotal |
|------|--------|-------------|----------|
| Tier 1 — Required | 2 | 4 | 8 |
| Tier 2 — Recommended | 8 | 2 | 16 |
| Tier 3 — Nice to Have | 10 scored + 3 INFO | 1 | 10 |
| **Total** | **20 scored** | | **34** |

### All .NET Checks

| # | Check | Slug | Tier | Category | Points |
|---|-------|------|------|----------|--------|
| 1 | Directory.Build.props | `dotnet-build-props` | 1 | Build Config | 4 |
| 2 | Test Project Exists | `dotnet-tests-exist` | 1 | Testing | 4 |
| 3 | Nullable Reference Types | `dotnet-nullable` | 2 | Code Quality | 2 |
| 4 | global.json SDK Pinning | `dotnet-global-json` | 2 | Build Config | 2 |
| 5 | Code Coverage | `dotnet-code-coverage` | 2 | Testing | 2 |
| 6 | Central Package Management | `dotnet-central-packages` | 2 | Build Config | 2 |
| 7 | XML Documentation | `dotnet-xml-docs` | 2 | Code Quality | 2 |
| 8 | NuGet Metadata | `dotnet-nuget-metadata` | 2 | Packaging | 2 |
| 9 | Solution Structure | `dotnet-solution-structure` | 2 | Build Config | 2 |
| 10 | Implicit Usings | `dotnet-implicit-usings` | 2 | Code Quality | 2 |
| 11 | TreatWarningsAsErrors | `dotnet-warnings-as-errors` | 3 | Code Quality | 1 |
| 12 | Deterministic Builds | `dotnet-deterministic` | 3 | Build Config | 1 |
| 13 | SourceLink | `dotnet-sourcelink` | 3 | Packaging | 1 |
| 14 | Analyzers Configured | `dotnet-analyzers` | 3 | Code Quality | 1 |
| 15 | AnalysisLevel | `dotnet-analysis-level` | 3 | Code Quality | 1 |
| 16 | Benchmark Project | `dotnet-benchmarks` | 3 | Testing | 1 |
| 17 | dotnet-tools.json | `dotnet-local-tools` | 3 | Build Config | 1 |
| 18 | AOT Ready | `dotnet-aot-ready` | 3 | Packaging | 1 |
| 19 | InternalsVisibleTo | `dotnet-internals-visible` | 3 | Testing | 1 |
| 20 | Multi-Targeting | `dotnet-multi-target` | 3 | Packaging | 1 |
| 21 | Target Framework | `dotnet-target-framework` | 3 | Build Config | INFO |
| 22 | Package Count | `dotnet-package-count` | 3 | Packaging | INFO |
| 23 | Build System | `dotnet-build-system` | 3 | Build Config | INFO |

### By Category

| Category | Checks | Description |
|----------|--------|-------------|
| **Build Config** | 8 | Directory.Build.props, global.json, Central Package Management, solution structure, deterministic builds, local tools, target framework, build system |
| **Code Quality** | 6 | Nullable, implicit usings, XML docs, warnings-as-errors, analyzers, analysis level |
| **Testing** | 4 | Test projects, code coverage, benchmarks, InternalsVisibleTo |
| **Packaging** | 5 | NuGet metadata, SourceLink, AOT, multi-targeting, package count |

## Tier Deep Dives

### Core Module
- [Tier 1 — Required](/checks/tier-1) (4 checks, 4 pts each)
- [Tier 2 — Recommended](/checks/tier-2) (22 checks, 2 pts each)
- [Tier 3 — Nice to Have](/checks/tier-3) (17 checks, 1 pt or INFO)

### .NET Module
- [Tier 1 — Required](/checks/dotnet-tier-1) (2 checks, 4 pts each)
- [Tier 2 — Recommended](/checks/dotnet-tier-2) (8 checks, 2 pts each)
- [Tier 3 — Nice to Have](/checks/dotnet-tier-3) (13 checks, 1 pt or INFO)
