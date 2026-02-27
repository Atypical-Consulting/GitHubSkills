# .NET — Tier 3 — Nice to Have

Tier 3 .NET checks verify polish and advanced configuration. Scored checks are worth **1 point** each. Three checks are **INFO only** (no score impact). These checks only run when a `.sln` file is detected.

## Scored Checks (1 pt each)

### TreatWarningsAsErrors

| Slug | Category |
|------|----------|
| `dotnet-warnings-as-errors` | Code Quality |

Treats all compiler warnings as errors, enforcing a zero-warning policy. Prevents warnings from accumulating and being ignored.

---

### Deterministic Builds

| Slug | Category |
|------|----------|
| `dotnet-deterministic` | Build Config |

`<Deterministic>true</Deterministic>` ensures identical source code produces identical binaries. Essential for reproducible builds and supply chain security.

---

### SourceLink

| Slug | Category |
|------|----------|
| `dotnet-sourcelink` | Packaging |

Embeds source repository metadata in NuGet packages, allowing debuggers to automatically download source code. Makes debugging third-party packages seamless.

---

### Analyzers Configured

| Slug | Category |
|------|----------|
| `dotnet-analyzers` | Code Quality |

Detects whether Roslyn analyzers are configured (via `<EnableNETAnalyzers>` or explicit analyzer packages). Static analysis catches bugs and enforces coding standards at compile time.

---

### AnalysisLevel

| Slug | Category |
|------|----------|
| `dotnet-analysis-level` | Code Quality |

Checks that `<AnalysisLevel>` is set (e.g., `latest-all` or `latest-recommended`). Controls the aggressiveness of built-in .NET analyzers.

---

### Benchmark Project

| Slug | Category |
|------|----------|
| `dotnet-benchmarks` | Testing |

Detects a BenchmarkDotNet project. Performance benchmarks prevent regressions and provide data-driven optimization decisions.

---

### dotnet-tools.json

| Slug | Category |
|------|----------|
| `dotnet-local-tools` | Build Config |

Checks for `.config/dotnet-tools.json`, which pins local .NET tool versions. Ensures all developers use the same tool versions (formatters, analyzers, generators).

---

### AOT Ready

| Slug | Category |
|------|----------|
| `dotnet-aot-ready` | Packaging |

Detects `<PublishAot>true</PublishAot>` or `<IsAotCompatible>true</IsAotCompatible>`. Native AOT compilation produces smaller, faster binaries with no JIT overhead.

---

### InternalsVisibleTo

| Slug | Category |
|------|----------|
| `dotnet-internals-visible` | Testing |

Detects `[InternalsVisibleTo]` attributes or `<InternalsVisibleTo>` in project files. Allows test projects to access internal members without making them public.

---

### Multi-Targeting

| Slug | Category |
|------|----------|
| `dotnet-multi-target` | Packaging |

Detects `<TargetFrameworks>` with multiple entries (e.g., `net8.0;net9.0`). Multi-targeting maximizes library compatibility across .NET versions.

---

## INFO Checks (0 pts)

These checks are reported but do not affect the score. They provide useful context about the .NET solution.

### Target Framework

| Slug | Category |
|------|----------|
| `dotnet-target-framework` | Build Config |

Reports the target framework(s) used across the solution and flags end-of-life (EOL) versions. Informational only — framework choice depends on project requirements.

---

### Package Count

| Slug | Category |
|------|----------|
| `dotnet-package-count` | Packaging |

Reports the total number of `<PackageReference>` entries across all projects. Provides a snapshot of dependency complexity. Not scored because dependency count alone doesn't indicate quality.

---

### Build System

| Slug | Category |
|------|----------|
| `dotnet-build-system` | Build Config |

Detects custom build systems (NUKE, Cake, FAKE) alongside standard `dotnet build`. Informational — build system choice is a team preference.
