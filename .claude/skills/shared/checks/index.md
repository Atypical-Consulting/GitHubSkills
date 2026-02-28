# Health Check Modules

Registry of all health check modules. Each module has its own `index.md` with tier tables, slug-to-path lookups, and scoring summaries.

Consumed by: ghs-repo-scan (orchestrator), ghs-backlog-fix, ghs-backlog-board, ghs-backlog-score, ghs-backlog-next.

## Directory Structure

```
checks/
├── index.md                        ← this file (module registry)
├── core/                           ← always active — language-agnostic checks
│   ├── index.md
│   ├── documentation/
│   ├── repo-settings/
│   ├── dev-config/
│   ├── ci-cd/
│   ├── community/
│   ├── security/
│   └── maintenance/
└── dotnet/                         ← activates when .sln detected
    ├── index.md
    ├── build-config/
    ├── code-quality/
    ├── testing/
    └── packaging/
```

## Module Registry

| Module | Slug | Detection | Checks | Max Points | Weight |
|--------|------|-----------|--------|------------|--------|
| Core | `core` | Always active | 40 | 74 | 60% (when language module active) or 100% (solo) |
| .NET | `dotnet` | `.sln` file in repo root | 23 | 34 | 40% |

## Stack Detection

The orchestrator detects the repository's tech stack early in the scan by checking for marker files:

| Marker File | Module | Detection Command |
|-------------|--------|-------------------|
| `*.sln` | `dotnet` | `gh api repos/{owner}/{repo}/contents/ --jq '.[].name' \| grep -q '\.sln$'` |
| `package.json` | `node` (future) | — |
| `pyproject.toml` or `setup.py` | `python` (future) | — |
| `go.mod` | `go` (future) | — |
| `Cargo.toml` | `rust` (future) | — |
| `pom.xml` or `build.gradle` | `java` (future) | — |

A repository may activate **multiple** language modules (e.g., a mono-repo with both .NET and Node). Each detected module runs independently.

## Scoring

### Single module (core only)

```
score = core_earned / core_possible * 100
```

### Multiple modules (core + language)

```
core_pct   = core_earned / core_possible * 100
lang_pct   = lang_earned / lang_possible * 100
score      = round(core_pct * 0.6 + lang_pct * 0.4)
```

- Core always contributes 60% of the combined score.
- Language module contributes 40%.
- If multiple language modules are active, they split the 40% equally (e.g., 2 modules = 20% each).
- WARN and INFO items are excluded from both earned and possible totals (same as before).

### Backlog storage

Findings are stored as items in the repository's GitHub Project. The orchestrator creates project items from the structured JSON results returned by each check agent — no local files are written.

## How Agents Use Modules

1. **Orchestrator** detects stack → determines active modules
2. For each active module, reads `checks/{module}/index.md`
3. Spawns check agents per module — 1 agent per tier per module
4. Each agent reads its module's index, runs checks, writes backlog items to the module's backlog subdirectory
5. Orchestrator aggregates scores across modules using the weighted formula
6. Output displays results grouped by module with a combined score

## Adding a New Module

1. Create `checks/{module-slug}/index.md` with tier tables, slug-to-path lookup, and scoring summary
2. Create category subdirectories with individual check files
3. Add the module to the **Module Registry** table above
4. Add its marker file to the **Stack Detection** table
5. Update `shared/references/item-categories.md` with fix routing for new checks
6. Update `shared/references/backlog-format.md` with the new backlog subdirectory
