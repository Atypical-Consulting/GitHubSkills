# ghs-release

Create a GitHub Release with auto-generated changelog from merged PRs and conventional commits since the last release.

::: info Skill Info
**Version:** 1.0.0
**Arguments:** `[owner/repo] [--bump major|minor|patch] [--pre-release] [--dry-run]`
**Trigger phrases:** "create release", "release v1.2.0", "patch release", "what would the next release look like", "changelog", "prepare release", "draft release", "pre-release", "cut a release", "ship it"
:::

## What It Does

`ghs-release` detects the current version, gathers changes since the last release, classifies them using conventional commit prefixes and PR labels, determines the semver bump, generates a grouped changelog, and creates a tagged GitHub Release.

### Scope Boundary

**Creates tags and releases only** — never modifies code, merges PRs, deletes branches, or changes repository settings.

### Process

1. **Detect current version** — From latest GitHub release, git tags, or default to `v0.1.0`
2. **Gather changes** — Merged PRs and commits since last release
3. **Classify changes** — Map conventional commit prefixes and labels to changelog groups
4. **Determine version bump** — Major (breaking), minor (features), or patch (fixes)
5. **Generate changelog** — Grouped by type with author attribution and PR links
6. **Pre-flight checks** — CI status, target branch, tag availability, write access
7. **Create release** — Or show dry-run preview
8. **Display** — Terminal summary with changelog and release URL

### Conventional Commits Mapping

| Prefix | Version Bump | Changelog Group |
|--------|-------------|-----------------|
| `feat:` | minor | Features |
| `fix:` | patch | Bug Fixes |
| `BREAKING CHANGE:` / `feat!:` | major | Breaking Changes |
| `docs:` | patch | Documentation |
| `chore(deps):` | patch | Dependencies |
| `ci:` / `test:` / `refactor:` / `perf:` | patch | Other |

### Input Modes

| Mode | Trigger | Example |
|------|---------|---------|
| Auto-detect | `create release` | Analyze commits to determine bump |
| Explicit version | `release v2.0.0` | Use specified version as-is |
| Bump type | `patch release` | Force a specific bump type |
| Dry-run | `what would the next release look like` | Preview without creating |
| Pre-release | `release v1.0.0-beta.1` | Set `--prerelease` flag |
| Draft | `draft release` | Create as draft for review |

## Example

### Dry-Run Preview

```
## Dry-Run Release Preview: phmatray/my-project

  Version:  v1.2.3 -> v1.3.0 (minor bump)
  Tag:      v1.3.0
  Target:   main
  Mode:     dry-run (no release created)

## What's Changed

### Features
- Add dark mode support for dashboard by @alice in #42
- Implement webhook retry logic by @bob in #38

### Bug Fixes
- Fix login timeout on slow connections by @charlie in #41
- Correct pagination offset in API response by @alice in #40

### Dependencies
- Update actions/checkout action to v6 by @renovate in #39
- Update dependency node to v24 by @renovate in #37

**Full Changelog**: https://github.com/owner/repo/compare/v1.2.3...v1.3.0

---
Summary:
  Changes:   6 (2 features, 2 fixes, 2 deps)
  Authors:   @alice, @bob, @charlie, @renovate
  Status:    DRY-RUN — no release created

To create this release: /ghs-release v1.3.0
```

### Successful Release

```
## Release Created: phmatray/my-project

  Version:  v1.2.3 -> v1.3.0
  Tag:      v1.3.0
  Target:   main
  Type:     release
  URL:      https://github.com/owner/repo/releases/tag/v1.3.0

---
Summary:
  Changes:   6 (2 features, 2 fixes, 2 deps)
  Authors:   @alice, @bob, @charlie
  Status:    [PASS] Release created
```

## Pre-flight Checks

| Check | Action on Failure |
|-------|-------------------|
| CI status on default branch | Warn; require `--force` to proceed |
| Target branch is default | Warn and ask for confirmation |
| Tag does not already exist | Abort; ask for different version |
| Write access confirmed | Abort if insufficient permissions |

## Routes To

- **[ghs-backlog-board](/skills/ghs-backlog-board)** — view updated dashboard after release

## Routes From

- **[ghs-merge-prs](/skills/ghs-merge-prs)** — release after merging PRs
- **[ghs-backlog-fix](/skills/ghs-backlog-fix)** — release after fixing backlog

## Technical Details

| Property | Value |
|----------|-------|
| Allowed tools | `Bash(gh:*)`, `Bash(git:*)`, `Read`, `Glob`, `Grep` |
| Spawns sub-agents | No — single sequential pipeline |
| Phases | 8 (Detect, Gather, Classify, Version, Changelog, Pre-flight, Create, Display) |
| Requires | `gh` CLI (authenticated), `git`, network access |
