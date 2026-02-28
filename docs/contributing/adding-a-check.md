# Adding a Health Check

GHS currently has 63 health checks across 2 modules (core and .NET). Here's how to add a new one.

## Step 1: Choose a Module and Category

Checks are organized by module, then by category within each module.

**Core module** (always active) — 7 categories:
- `documentation` --- project docs (README, LICENSE, CHANGELOG, etc.)
- `repo-settings` --- GitHub repo configuration
- `dev-config` --- developer tooling (.gitignore, .editorconfig, etc.)
- `ci-cd` --- CI/CD pipelines
- `community` --- community health (templates, security policy)
- `security` --- security posture
- `maintenance` --- ongoing project health

**.NET module** (activates on `.sln` detection) — 4 categories:
- `build-config` --- build infrastructure (Directory.Build.props, global.json, etc.)
- `code-quality` --- analyzers, nullable, warnings
- `testing` --- tests, coverage, benchmarks
- `packaging` --- NuGet, SourceLink, multi-targeting

## Step 2: Create the Check File

Create the check file in the appropriate module and category directory:

- Core checks: `.claude/skills/shared/checks/core/{category}/{slug}.md`
- .NET checks: `.claude/skills/shared/checks/dotnet/{category}/{slug}.md`

Use this frontmatter structure:

```yaml
---
check: Human-readable name
slug: kebab-case-slug
tier: 1|2|3
category: one of the module's categories
points: 4|2|1
scoring: Normal|INFO only
---
```

Then include these sections:
- **What to Check** --- verification logic
- **Status Rules** --- when PASS, FAIL, WARN
- **Project Item Content** --- what to create as a GitHub Project item if FAIL (title, description, acceptance criteria)

## Step 3: Register in the Module Index

Add the check to the appropriate module's `index.md`:

- Core: `.claude/skills/shared/checks/core/index.md`
- .NET: `.claude/skills/shared/checks/dotnet/index.md`

Steps:
1. Add a row to the appropriate tier table
2. Update the Scoring Summary if tier totals change
3. Add to the Slug-to-Path Lookup table

## Step 4: Categorize for Fixing

Add the slug to the appropriate category in `.claude/skills/shared/references/item-categories.md`:
- Category A: API-only (no file changes)
- Category B: File changes (needs worktree)
- Category CI: Special CI diagnosis

For .NET checks, most are Category B (file changes to `.csproj` or `Directory.Build.props`).

## Step 5: Update Documentation

Update the docs site to reflect the new check:
1. Add to the appropriate tier page in `docs/checks/`
2. Update check counts in `docs/checks/index.md`
3. Update the HomeContent stats if totals changed

## Step 6: Test

Run `ghs-repo-scan` against a test repo and verify your check appears correctly.

## Adding a New Module

To add an entirely new language module (e.g., Python, Node):

1. Create `checks/{module}/index.md` with the module's check registry
2. Create category subdirectories with check files
3. Add the module to `checks/index.md` (the module registry)
4. Add a stack detection rule (e.g., `pyproject.toml` for Python)
5. Update `shared/references/scoring-logic.md` with the module's max points
6. Update `shared/references/config.md` with the module constants
7. Update `shared/references/item-categories.md` with fix routing
8. Update `shared/references/projects-format.md` with the new project item fields for the module
9. Update consumer skills (ghs-repo-scan, ghs-backlog-board, ghs-backlog-score, ghs-backlog-fix)
