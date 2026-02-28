# .NET Health Checks Module

Module: `dotnet` — Activates when a `.sln` file is detected in the repository root.

Registry of .NET-specific health checks covering build configuration, code quality, testing, and packaging best practices.

Consumed by: ghs-repo-scan (orchestrator and check agents), ghs-backlog-fix, ghs-backlog-board, ghs-backlog-score.

## Directory Structure

```
dotnet/
├── index.md                    ← this file
├── build-config/               ← build infrastructure and SDK configuration
├── code-quality/               ← analyzers, nullable, warnings, language features
├── testing/                    ← test projects, coverage, benchmarks
└── packaging/                  ← NuGet metadata, SourceLink, multi-targeting
```

## Activation

```bash
gh api repos/{owner}/{repo}/contents/ --jq '.[].name' 2>/dev/null | grep -q '\.sln$'
```

If the command succeeds (exit 0), this module is active.

## Check Registry

### Tier 1 — Required (4 points each)

| Check | Slug | Category | File | Scoring |
|-------|------|----------|------|---------|
| Directory.Build.props | `dotnet-build-props` | build-config | [dotnet-build-props.md](build-config/dotnet-build-props.md) | Normal |
| Test Project Exists | `dotnet-tests-exist` | testing | [dotnet-tests-exist.md](testing/dotnet-tests-exist.md) | Normal |

### Tier 2 — Recommended (2 points each)

| Check | Slug | Category | File | Scoring |
|-------|------|----------|------|---------|
| Nullable Reference Types | `dotnet-nullable` | code-quality | [dotnet-nullable.md](code-quality/dotnet-nullable.md) | Normal |
| global.json SDK Pinning | `dotnet-global-json` | build-config | [dotnet-global-json.md](build-config/dotnet-global-json.md) | Normal |
| Code Coverage | `dotnet-code-coverage` | testing | [dotnet-code-coverage.md](testing/dotnet-code-coverage.md) | Normal |
| Central Package Mgmt | `dotnet-central-packages` | build-config | [dotnet-central-packages.md](build-config/dotnet-central-packages.md) | Normal |
| XML Documentation | `dotnet-xml-docs` | code-quality | [dotnet-xml-docs.md](code-quality/dotnet-xml-docs.md) | Normal |
| NuGet Metadata | `dotnet-nuget-metadata` | packaging | [dotnet-nuget-metadata.md](packaging/dotnet-nuget-metadata.md) | Normal |
| Solution Structure | `dotnet-solution-structure` | build-config | [dotnet-solution-structure.md](build-config/dotnet-solution-structure.md) | Normal |
| Implicit Usings | `dotnet-implicit-usings` | code-quality | [dotnet-implicit-usings.md](code-quality/dotnet-implicit-usings.md) | Normal |

### Tier 3 — Nice to Have (1 point each)

| Check | Slug | Category | File | Scoring |
|-------|------|----------|------|---------|
| TreatWarningsAsErrors | `dotnet-warnings-as-errors` | code-quality | [dotnet-warnings-as-errors.md](code-quality/dotnet-warnings-as-errors.md) | Normal |
| Deterministic Builds | `dotnet-deterministic` | build-config | [dotnet-deterministic.md](build-config/dotnet-deterministic.md) | Normal |
| SourceLink | `dotnet-sourcelink` | packaging | [dotnet-sourcelink.md](packaging/dotnet-sourcelink.md) | Normal |
| Analyzers Configured | `dotnet-analyzers` | code-quality | [dotnet-analyzers.md](code-quality/dotnet-analyzers.md) | Normal |
| AnalysisLevel | `dotnet-analysis-level` | code-quality | [dotnet-analysis-level.md](code-quality/dotnet-analysis-level.md) | Normal |
| Benchmark Project | `dotnet-benchmarks` | testing | [dotnet-benchmarks.md](testing/dotnet-benchmarks.md) | Normal |
| dotnet-tools.json | `dotnet-local-tools` | build-config | [dotnet-local-tools.md](build-config/dotnet-local-tools.md) | Normal |
| AOT Ready | `dotnet-aot-ready` | packaging | [dotnet-aot-ready.md](packaging/dotnet-aot-ready.md) | Normal |
| InternalsVisibleTo | `dotnet-internals-visible` | testing | [dotnet-internals-visible.md](testing/dotnet-internals-visible.md) | Normal |
| Multi-Targeting | `dotnet-multi-target` | packaging | [dotnet-multi-target.md](packaging/dotnet-multi-target.md) | Normal |
| Target Framework | `dotnet-target-framework` | build-config | [dotnet-target-framework.md](build-config/dotnet-target-framework.md) | **INFO only** |
| Package Count | `dotnet-package-count` | packaging | [dotnet-package-count.md](packaging/dotnet-package-count.md) | **INFO only** |
| Build System | `dotnet-build-system` | build-config | [dotnet-build-system.md](build-config/dotnet-build-system.md) | **INFO only** |

## Scoring Summary

| Tier | Checks | Points each | Subtotal |
|------|--------|-------------|----------|
| Tier 1 | 2 | 4 | 8 |
| Tier 2 | 8 | 2 | 16 |
| Tier 3 | 10 (excluding 3 INFO) | 1 | 10 |
| **Total** | **23** | | **34** |

- WARN items are excluded from both earned and possible totals.
- INFO items (Target Framework, Package Count, Build System) carry no points and no penalty.
- Percentage: `earned / possible * 100`, rounded to nearest integer.

## Category Summary

| Category | Checks | Description |
|----------|--------|-------------|
| build-config | 8 | Build infrastructure: Directory.Build.props, global.json, CPM, solution structure, deterministic builds, local tools, TFM reporting, build system detection |
| code-quality | 6 | Code quality settings: nullable, implicit usings, XML docs, warnings-as-errors, analyzers, analysis level |
| testing | 4 | Testing infrastructure: test projects, code coverage, benchmarks, InternalsVisibleTo |
| packaging | 5 | NuGet packaging: metadata, SourceLink, AOT readiness, multi-targeting, package count |

## Slug-to-Path Lookup

Agents use this table to resolve check file paths from slugs:

| Slug | Path |
|------|------|
| `dotnet-build-props` | `build-config/dotnet-build-props.md` |
| `dotnet-global-json` | `build-config/dotnet-global-json.md` |
| `dotnet-central-packages` | `build-config/dotnet-central-packages.md` |
| `dotnet-solution-structure` | `build-config/dotnet-solution-structure.md` |
| `dotnet-deterministic` | `build-config/dotnet-deterministic.md` |
| `dotnet-local-tools` | `build-config/dotnet-local-tools.md` |
| `dotnet-target-framework` | `build-config/dotnet-target-framework.md` |
| `dotnet-build-system` | `build-config/dotnet-build-system.md` |
| `dotnet-nullable` | `code-quality/dotnet-nullable.md` |
| `dotnet-implicit-usings` | `code-quality/dotnet-implicit-usings.md` |
| `dotnet-xml-docs` | `code-quality/dotnet-xml-docs.md` |
| `dotnet-warnings-as-errors` | `code-quality/dotnet-warnings-as-errors.md` |
| `dotnet-analyzers` | `code-quality/dotnet-analyzers.md` |
| `dotnet-analysis-level` | `code-quality/dotnet-analysis-level.md` |
| `dotnet-tests-exist` | `testing/dotnet-tests-exist.md` |
| `dotnet-code-coverage` | `testing/dotnet-code-coverage.md` |
| `dotnet-benchmarks` | `testing/dotnet-benchmarks.md` |
| `dotnet-internals-visible` | `testing/dotnet-internals-visible.md` |
| `dotnet-nuget-metadata` | `packaging/dotnet-nuget-metadata.md` |
| `dotnet-sourcelink` | `packaging/dotnet-sourcelink.md` |
| `dotnet-aot-ready` | `packaging/dotnet-aot-ready.md` |
| `dotnet-multi-target` | `packaging/dotnet-multi-target.md` |
| `dotnet-package-count` | `packaging/dotnet-package-count.md` |

## How Agents Use This Index

Each check agent receives a module (`dotnet`) and tier assignment. It:
1. Reads this index to find the checks in its tier
2. For each check, uses the **Slug-to-Path Lookup** table to find the check file: `{category}/{slug}.md`
3. Reads the individual check file
4. Runs the verification command from the check file
5. Determines PASS/FAIL/WARN based on status rules
6. If FAIL/WARN, includes the Backlog Content section data in the structured result and returns it to the orchestrator for project item creation
7. Returns structured results to the orchestrator
