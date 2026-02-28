# Item Categories

Classification of health check items by fix strategy. The orchestrator uses this classification to route items to the correct agent type and determine whether a worktree is needed.

## Why Categories Matter

Different checks need fundamentally different fix approaches:

- **API-only fixes** (like setting a repo description) don't need file changes or branches
- **File-change fixes** (like adding a LICENSE) need worktrees, branches, and PRs
- **CI fixes** need a diagnostic step before any changes

Routing items to the wrong category wastes resources or misses required steps.

## Core Module Categories

| Category | Description | Worktree? | Checks |
|----------|-------------|-----------|--------|
| **A** (API-only) | Uses `gh` commands directly | No | branch-protection, security-alerts, description, topics, delete-branch-on-merge, merge-strategy, homepage-url, stale-branches, github-releases |
| **B** (file changes) | Creates/modifies files, commits, pushes, creates PR | Yes | license, editorconfig, codeowners, issue-templates, pr-template, security-md, contributing-md, code-of-conduct, readme, gitignore, ci-cd-workflows, changelog, gitattributes, version-pinning, dependency-update-config |
| **CI** (special) | Diagnoses CI failures before fixing | Yes | ci-workflow-health, action-version-pinning, workflow-permissions, workflow-naming, workflow-timeouts, workflow-concurrency |

## .NET Module Categories

| Category | Description | Worktree? | Checks |
|----------|-------------|-----------|--------|
| **B** (file changes) | Modifies .NET project files | Yes | dotnet-build-props, dotnet-global-json, dotnet-central-packages, dotnet-nullable, dotnet-implicit-usings, dotnet-xml-docs, dotnet-warnings-as-errors, dotnet-deterministic, dotnet-analyzers, dotnet-analysis-level, dotnet-sourcelink, dotnet-local-tools, dotnet-nuget-metadata, dotnet-aot-ready |
| **A** (inspection-only) | Read-only checks, no fix needed | No | dotnet-tests-exist, dotnet-solution-structure, dotnet-code-coverage, dotnet-benchmarks, dotnet-internals-visible, dotnet-multi-target |

.NET INFO-only checks (`dotnet-target-framework`, `dotnet-package-count`, `dotnet-build-system`) never produce FAIL results and are never routed for fixing.

## Classification Rules

1. **Issue items** are always Category B --- they require code changes
2. **Core health items** are classified by slug using the Core Module table
3. **.NET health items** are classified by slug using the .NET Module table
4. Unknown slugs default to Category B (file changes are the safe assumption)

## Category Notes

### Category A

- All items handled by a single agent in one batch
- No worktree or branch needed --- changes via GitHub API
- Solo-maintainer repos use lightweight branch protection (no required PR reviews)
- .NET Category A items are inspection-only --- fixes are too context-dependent to automate

### Category B

- One agent per item, each in its own worktree
- Agent inspects the repo to produce context-aware content (not boilerplate)
- PR body includes acceptance criteria as a checklist
- .NET agents read existing `Directory.Build.props` and `.csproj` files before making changes

### Category CI

- Mandatory diagnostic step before any fix attempt
- Must read actual CI failure logs (`gh run view --log-failed`)
- Verify workflow YAML is valid after changes
