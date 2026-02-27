# Item Categories

Classification of health check items by fix strategy. The orchestrator uses this table to route items to the correct agent type and determine whether a worktree is needed.

## Why Categories Matter

Different checks need fundamentally different fix approaches. API-only fixes (like setting a repo description) don't need file changes or branches. File-change fixes (like adding a LICENSE) need worktrees, branches, and PRs. CI fixes need a diagnostic step before any changes — jumping straight to a fix wastes time when the root cause hasn't been identified. Routing items to the wrong category either wastes resources (unnecessary worktree for an API call) or misses steps (skipping diagnosis for CI failures).

## Core Module Categories

| Category | Description | Worktree? | Agent | Checks |
|----------|-------------|-----------|-------|--------|
| **A** (API-only) | Uses `gh` commands directly, no file changes | No | `category-a-agent.md` | branch-protection, security-alerts, description, topics, delete-branch-on-merge, merge-strategy, homepage-url, stale-branches, github-releases |
| **B** (file changes) | Creates/modifies files, commits, pushes, creates PR | Yes — one per item | `category-b-agent.md` | license, editorconfig, codeowners, issue-templates, pr-template, security-md, contributing-md, code-of-conduct, readme, gitignore, ci-cd-workflows, changelog, gitattributes, version-pinning, dependency-update-config |
| **CI** (special) | Diagnoses CI failures before fixing | Yes | `category-ci-agent.md` | ci-workflow-health, action-version-pinning, workflow-permissions, workflow-naming, workflow-timeouts, workflow-concurrency |

## .NET Module Categories

| Category | Description | Worktree? | Checks |
|----------|-------------|-----------|--------|
| **B** (file changes) | Creates/modifies .NET project files, commits, pushes, creates PR | Yes — one per item | dotnet-build-props, dotnet-global-json, dotnet-central-packages, dotnet-nullable, dotnet-implicit-usings, dotnet-xml-docs, dotnet-warnings-as-errors, dotnet-deterministic, dotnet-analyzers, dotnet-analysis-level, dotnet-sourcelink, dotnet-local-tools, dotnet-nuget-metadata, dotnet-aot-ready |
| **A** (inspection-only) | Read-only checks that report status, no fix needed | No | dotnet-tests-exist, dotnet-solution-structure, dotnet-code-coverage, dotnet-benchmarks, dotnet-internals-visible, dotnet-multi-target |

Note: .NET INFO-only checks (`dotnet-target-framework`, `dotnet-package-count`, `dotnet-build-system`) never produce FAIL results and are never routed for fixing.

## Classification Rules

1. **Issue items** are always Category B — they require code changes
2. **Core health items** are classified by their slug using the Core Module table above
3. **.NET health items** are classified by their slug using the .NET Module table above
4. If a slug isn't listed, default to Category B (file changes are the safe assumption)

## Category A Notes

- All items handled by a single agent in one batch
- No worktree or branch needed — changes are made via the GitHub API
- Solo-maintainer detection: if the repo has a single owner and no collaborators, use lightweight branch protection rules (requiring PR reviews would block the only person who can merge)
- For .NET Category A items: these are inspection-only — they report whether a practice is followed but the fix is too context-dependent to automate (e.g., "add test projects" requires understanding the domain)

## Category B Notes

- One agent per item, each in its own worktree
- Agent must inspect the repo to produce context-aware content (not boilerplate)
- PR body must include acceptance criteria as a checklist
- For .NET Category B items: agents should read existing `Directory.Build.props` and `.csproj` files to understand current settings before making changes

## Category CI Notes

- Mandatory diagnostic step before any fix attempt
- Must read actual CI failure logs (`gh run view --log-failed`)
- Verify workflow YAML is valid after changes
