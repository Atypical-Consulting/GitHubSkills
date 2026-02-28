---
name: ghs-release
description: >
  Create a GitHub Release with auto-generated changelog from merged PRs and conventional commits
  since the last release. Detects current version, determines the next semver bump, groups changes
  by type, and creates a tagged release with structured notes. Use this skill whenever the user wants
  to create a release, prepare a changelog, check what the next release would look like, or says
  things like "create release", "release v1.2.0", "patch release", "what would the next release look
  like", "changelog", "prepare release", "draft release", "pre-release", "cut a release",
  "tag a release", "ship it", or "what changed since last release".
  Do NOT use for merging PRs (use ghs-merge-prs), fixing backlog items (use ghs-backlog-fix),
  scanning repo health (use ghs-repo-scan), or managing GitHub Actions (use ghs-action-fix).
allowed-tools: "Bash(gh:*) Bash(git:*) Read Glob Grep"
compatibility: "Requires gh CLI (authenticated), git, network access"
license: MIT
metadata:
  author: phmatray
  version: 1.0.0
routes-to:
  - ghs-backlog-board
routes-from:
  - ghs-merge-prs
  - ghs-backlog-fix
---

# Release Management

Automate GitHub Release creation: generate a changelog from commits and merged PRs since the last release, determine the version bump, create a Git tag and GitHub Release with structured release notes.

<context>
Purpose: Create GitHub Releases with auto-generated changelogs, semver version detection, and conventional commit classification.

Roles:
1. **Releaser** (you) — detects current version, gathers changes, classifies them, determines version bump, generates changelog, checks CI, creates the release

This skill does not spawn sub-agents — the release workflow is a single sequential pipeline.

Shared references:

| Reference | Purpose |
|-----------|---------|
| `../shared/references/gh-cli-patterns.md` | Authentication, repo detection, error handling, PR operations |
| `../shared/references/output-conventions.md` | Status indicators, table formats, summary blocks |
</context>

<anti-patterns>

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Create a release without checking CI status on the default branch | Run pre-flight CI check and warn if failing | Releasing broken code erodes trust and may require a hotfix release |
| Skip changelog generation and use a bare tag | Always generate a grouped changelog from PRs and commits | Empty release notes provide no value to users or contributors |
| Guess the next version number | Derive from conventional commits analysis or use user-provided explicit version | Wrong versions break semver contracts and confuse dependency consumers |
| Create a release on a non-default branch without user confirmation | Detect the target branch and confirm with user if it differs from default | Releasing from feature branches can ship incomplete or experimental work |
| Include unmerged PRs in the changelog | Filter strictly by merged state and merge date after last release | Unmerged PRs are not part of the release and mislead users |
| Skip draft mode for major releases | Default to `--draft` for major version bumps and confirm before publishing | Major releases deserve extra review since they signal breaking changes |
| Create a release when no changes exist since the last one | Warn the user and abort unless `--force` is specified | Empty releases add noise and confuse the version timeline |
| Delete or overwrite existing tags | Warn if the computed tag already exists and ask the user | Overwriting tags breaks anyone who already pulled the previous tag |

</anti-patterns>

## Scope Boundary

This skill **creates tags and releases only** — it never modifies code, merges PRs, deletes branches, or changes repository settings. The sole write actions are:

1. Creating a Git tag via `gh release create` (which tags automatically)
2. Creating a GitHub Release with generated notes

Everything else is read-only investigation.

<objective>
Create a GitHub Release with a structured changelog grouped by change type.

Outputs:
- GitHub Release URL (or dry-run preview in terminal)
- Terminal changelog preview with version summary

Next routing (see `output-conventions.md` @ Routing Suggestions):
- Suggest `ghs-backlog-board` to see updated dashboard — "To review status: `/ghs-backlog-board`"
- If there are open PRs remaining, suggest `ghs-merge-prs` — "To merge remaining PRs: `/ghs-merge-prs {owner}/{repo}`"
</objective>

<process>

## Input

- **Explicit version**: `release v2.0.0`, `create release v1.3.0`
- **Bump type**: `patch release`, `minor release`, `major release`
- **Auto-detect**: `create release`, `what would the next release look like`
- **Dry-run**: `prepare release`, `changelog`, `what would the next release look like` — show preview without creating
- **Pre-release**: `pre-release`, `release v1.0.0-beta.1`, `alpha release`
- **Draft**: `draft release` — creates release as draft

### Input Parsing Rules

| Rule | Trigger | Example |
|------|---------|---------|
| Explicit version overrides auto-detect | User provides a full semver string | `release v2.0.0` — use v2.0.0 regardless of commit analysis |
| Bump type narrows auto-detect | User specifies major/minor/patch | `patch release` — force patch bump even if commits suggest minor |
| Dry-run by default for informational queries | User asks "what would" or "changelog" or "prepare" | `what would the next release look like` — show preview, do not create |
| Pre-release suffix detection | Version contains `-alpha`, `-beta`, `-rc` | `release v1.0.0-beta.1` — set `--prerelease` flag |
| Draft flag detection | User says "draft" | `draft release` — set `--draft` flag |
| Repo detection | No explicit repo | Detect from `gh repo view` (see `gh-cli-patterns.md` @ Repo Detection) |

## Phase 1 — Detect Current Version

Determine the latest released version using multiple sources:

| Source | Command | Fallback |
|--------|---------|----------|
| Latest GitHub release | `gh release list --limit 1 --json tagName,publishedAt` | If empty, try git tags |
| Latest git tag | `git tag --sort=-v:refname \| head -1` | If empty, treat as first release |
| No previous release | N/A | Default to `v0.1.0` or user-specified version |

```bash
# Preferred: GitHub release (includes date for changelog range)
LAST_RELEASE=$(gh release list --repo {owner}/{repo} --limit 1 --json tagName,publishedAt -q '.[0]')

# Fallback: git tag
if [ -z "$LAST_RELEASE" ]; then
  LAST_TAG=$(git tag --sort=-v:refname | head -1)
fi
```

Extract the release date for the changelog query range. If using a git tag without a release, use the tag's commit date:

```bash
git log -1 --format=%aI {tag}
```

## Phase 2 — Gather Changes Since Last Release

### Merged PRs

```bash
gh pr list --repo {owner}/{repo} --state merged \
  --search "merged:>={last_release_date}" \
  --json number,title,labels,author,mergedAt \
  --limit 200
```

### Commits (for repos that don't use PRs)

```bash
git log {last_tag}..HEAD --oneline --format="%h %s" --no-merges
```

**Guard rail**: If both lists are empty, warn the user and abort:

```
[WARN] No changes found since {last_tag} ({last_release_date}).
       Nothing to release. Use --force to create an empty release.
```

## Phase 3 — Classify Changes

### Conventional Commits Mapping

| Prefix | Version Bump | Changelog Group |
|--------|-------------|-----------------|
| `feat:` / `feat(scope):` | minor | Features |
| `fix:` / `fix(scope):` | patch | Bug Fixes |
| `BREAKING CHANGE:` / `!:` (e.g., `feat!:`) | major | Breaking Changes |
| `docs:` / `docs(scope):` | patch | Documentation |
| `chore(deps):` / `build(deps):` / `deps:` | patch | Dependencies |
| `ci:` / `test:` / `refactor:` / `perf:` / `style:` / `chore:` / `build:` | patch | Other |

### Classification Rules

| Rule | Trigger | Example |
|------|---------|---------|
| PR title takes precedence over individual commits | PR has a conventional prefix in its title | PR #42 "feat: add dark mode" — classified as Features |
| Label-based fallback if no conventional prefix | PR has labels like `bug`, `enhancement`, `dependencies` | PR #43 labeled `bug` — classified as Bug Fixes |
| Commits without PRs are classified individually | Commit not associated with any PR | `fix: correct typo` — classified as Bug Fixes |
| Unknown prefix defaults to Other | No recognized prefix or label | `Update README` — classified as Other |
| BREAKING CHANGE in commit body also triggers major | Body contains `BREAKING CHANGE:` | `feat: new API\n\nBREAKING CHANGE: removed v1 endpoints` — major + Breaking Changes |

### Label-to-Group Mapping (Fallback)

| Label | Changelog Group |
|-------|-----------------|
| `bug`, `fix`, `type:bug` | Bug Fixes |
| `enhancement`, `feature`, `type:feature` | Features |
| `dependencies`, `deps`, `renovate`, `dependabot` | Dependencies |
| `documentation`, `docs`, `type:docs` | Documentation |
| `breaking`, `breaking-change` | Breaking Changes |

## Phase 4 — Determine Version Bump

If the user provided an explicit version, use it. Otherwise, compute from classified changes:

| Highest Change Type | Bump | Example |
|--------------------|------|---------|
| Breaking Changes present | major | v1.2.3 -> v2.0.0 |
| Features present (no breaking) | minor | v1.2.3 -> v1.3.0 |
| Only fixes/deps/docs/other | patch | v1.2.3 -> v1.2.4 |

### Pre-release Version Handling

| Current Version | Bump Type | Next Version |
|----------------|-----------|--------------|
| v1.0.0 | pre-release (alpha) | v1.1.0-alpha.1 (or user-specified) |
| v1.1.0-alpha.1 | pre-release (alpha) | v1.1.0-alpha.2 |
| v1.1.0-alpha.2 | pre-release (beta) | v1.1.0-beta.1 |
| v1.1.0-rc.1 | release | v1.1.0 |

### Guard Rails

| Rule | Trigger | Example |
|------|---------|---------|
| Warn if major bump detected | Conventional commits show breaking changes | `[WARN] Breaking changes detected — this will be a MAJOR release (v1.x -> v2.0.0). Proceed?` |
| Warn if tag exists | Computed tag already exists in git | `[WARN] Tag v1.3.0 already exists. Use a different version or --force to overwrite.` |
| Validate semver format | User-provided version doesn't match semver | `[FAIL] "v1.2" is not valid semver. Use format: v{major}.{minor}.{patch}[-prerelease]` |

## Phase 5 — Generate Changelog

Group classified changes into the changelog template:

```markdown
## What's Changed

### Breaking Changes
- {PR title or commit description} by @{author} in #{number}

### Features
- {PR title or commit description} by @{author} in #{number}

### Bug Fixes
- {PR title or commit description} by @{author} in #{number}

### Dependencies
- {PR title or commit description} by @{author} in #{number}

### Documentation
- {PR title or commit description} by @{author} in #{number}

### Other
- {PR title or commit description} by @{author} in #{number}

**Full Changelog**: https://github.com/{owner}/{repo}/compare/{prev_tag}...{next_tag}
```

**Rules:**
- Omit empty sections (if no breaking changes, skip that heading)
- Strip conventional commit prefixes from titles (e.g., `feat: add dark mode` becomes `Add dark mode`)
- Capitalize the first letter of each entry
- For commits without PRs, use the commit hash instead of `#{number}`
- Sort entries within each group by merge date (newest first)

## Phase 6 — Pre-flight Checks

Before creating the release, verify:

| Check | Command | Action on Failure |
|-------|---------|-------------------|
| CI status on default branch | `gh run list --repo {owner}/{repo} --branch {default_branch} --limit 1 --json status,conclusion` | Warn user; require `--force` to proceed |
| Target branch is default | `gh repo view --json defaultBranchRef -q '.defaultBranchRef.name'` | Warn and ask for confirmation if different |
| Tag does not already exist | `git tag -l {next_tag}` | Abort and ask user for a different version |
| Authenticated user has write access | `gh repo view --json viewerPermission` | Abort if insufficient permissions |

```
[PASS] CI passing on main (run #456)
[PASS] Targeting default branch: main
[PASS] Tag v1.3.0 does not exist
[PASS] Write access confirmed
```

If CI is failing:

```
[WARN] CI is FAILING on main (run #456 — conclusion: failure)
       Creating a release with failing CI is not recommended.
       Use --force to override, or wait for CI to pass.
```

## Phase 7 — Create Release (or Dry-Run Preview)

### Dry-Run Mode

If dry-run, display the changelog and version summary in the terminal without creating anything:

```
## Dry-Run Release Preview: {owner}/{repo}

  Version:  v1.2.3 -> v1.3.0 (minor bump)
  Tag:      v1.3.0
  Target:   main
  Mode:     dry-run (no release created)

{changelog}

---
Summary:
  Changes:   12 (3 features, 5 fixes, 2 deps, 2 other)
  Authors:   @alice, @bob, @charlie
  Status:    DRY-RUN — no release created

To create this release: `/ghs-release v1.3.0`
```

### Create Mode

```bash
gh release create {next_tag} \
  --repo {owner}/{repo} \
  --title "{next_tag}" \
  --notes "$(cat <<'EOF'
{changelog}
EOF
)" \
  --target {default_branch} \
  {--draft if draft mode} \
  {--prerelease if pre-release}
```

For major releases, default to `--draft` and inform the user:

```
[INFO] Major release v2.0.0 created as DRAFT.
       Review at: {release_url}
       To publish: gh release edit v2.0.0 --repo {owner}/{repo} --draft=false
```

## Phase 8 — Terminal Output

### Successful Release

```
## Release Created: {owner}/{repo}

  Version:  v1.2.3 -> v1.3.0
  Tag:      v1.3.0
  Target:   main
  Type:     {release | draft | pre-release}
  URL:      https://github.com/{owner}/{repo}/releases/tag/{next_tag}

### Changelog

{changelog}

---
Summary:
  Changes:   12 (3 features, 5 fixes, 2 deps, 2 other)
  Authors:   @alice, @bob, @charlie
  PRs:       #40, #41, #42, #43, #44, #45, #46, #47, #48, #49, #50, #51
  Status:    [PASS] Release created
```

### Failed Release

```
## Release Failed: {owner}/{repo}

  Version:  v1.3.0
  Error:    {error message}
  Status:   [FAIL] Release not created

Troubleshooting:
  - Check `gh auth status` for authentication
  - Verify write access to the repository
  - Ensure the tag does not already exist
```

</process>

## Edge Cases

| Scenario | Handling |
|----------|----------|
| **No previous releases** (first release) | Default to v0.1.0; gather all commits on default branch; note "Initial release" in changelog header |
| **Pre-release versions** | Detect `-alpha`, `-beta`, `-rc` suffixes; increment pre-release counter; set `--prerelease` flag |
| **No changes since last release** | Warn user and abort; suggest checking if PRs were merged to a different branch |
| **Failed CI on default branch** | Warn with run URL; require `--force` or wait for CI to pass |
| **Monorepo** | Note limitation — this skill creates a single release per repo; suggest manual scoping for monorepos |
| **Tag already exists** | Abort with error; suggest using a different version number |
| **Non-default branch target** | Warn and require explicit confirmation before creating |
| **Very large changelog (50+ PRs)** | Group normally but add a count summary; truncate individual entries if the body would exceed 10,000 characters |
| **Archived repository** | Detect via `gh repo view --json isArchived`; abort with warning |
| **No conventional commits** | Fall back to label-based classification; if no labels either, list all as "Other" |

## Examples

### Good Release Notes

```markdown
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
```

### Bad Release Notes

```markdown
## What's Changed

- feat: dark mode
- fix stuff
- bump deps
- misc changes
- Update README.md
```

(Missing: author attribution, PR links, grouping by type, full changelog link, capitalization)

### Example 1: Auto-detect Release

User says: `create release`
Result: Detects current version v1.2.3, analyzes commits, determines minor bump (features found), generates grouped changelog, checks CI, creates release v1.3.0, shows terminal summary with URL.

### Example 2: Explicit Version

User says: `release v2.0.0`
Result: Uses v2.0.0 as-is, generates changelog since v1.2.3, warns about major release, creates as draft, shows terminal summary.

### Example 3: Dry-Run Preview

User says: `what would the next release look like`
Result: Detects version, analyzes changes, shows changelog preview in terminal, does NOT create release. Suggests command to create.

### Example 4: Pre-release

User says: `release v1.3.0-beta.1`
Result: Creates pre-release with `--prerelease` flag, generates changelog, shows terminal summary.

### Example 5: No Changes

User says: `create release`
Result: Detects v1.2.3 as current, finds no merged PRs or commits since then, warns user, aborts without creating.
