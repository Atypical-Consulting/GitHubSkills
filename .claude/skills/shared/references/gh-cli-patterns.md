# gh CLI Patterns Reference

Common `gh` CLI patterns used across all GitHubSkills skills. All GitHub API interactions must use `gh` — it handles authentication, pagination, and rate limiting automatically.

## Authentication Check

```bash
gh auth status
```

If this fails, instruct the user to run `gh auth login`.

## Repo Detection

```bash
# Auto-detect from current git remote
gh repo view --json nameWithOwner -q '.nameWithOwner'

# Validate repo is accessible
gh repo view {owner}/{repo} --json name -q '.name'
```

Detection order: explicit argument > git remote > ask the user.

## Repo Metadata Queries

| Query | Command |
|-------|---------|
| Default branch | `gh repo view {owner}/{repo} --json defaultBranchRef -q '.defaultBranchRef.name'` |
| Visibility | `gh repo view {owner}/{repo} --json isPrivate -q '.isPrivate'` |
| Fork status | `gh repo view {owner}/{repo} --json isFork,parent -q '{fork: .isFork, parent: .parent.nameWithOwner}'` |
| Owner type | `gh repo view {owner}/{repo} --json owner -q '.owner.type'` |
| Issues enabled | `gh repo view {owner}/{repo} --json hasIssuesEnabled -q '.hasIssuesEnabled'` |
| Viewer permission | `gh repo view --json viewerPermission` |
| Collaborator count | `gh api repos/{owner}/{repo}/collaborators --jq 'length'` |
| Authenticated user | `gh api user --jq '.login'` |

## Issue Operations

```bash
# List open issues
gh issue list --repo {owner}/{repo} --state open --json number,title,body,labels,assignees --limit 100

# List by label
gh issue list --repo {owner}/{repo} --state open --label "{label}" --json number,title,body,labels,comments --limit 50

# List all states with specific label
gh issue list --label "ghs:health-check" --state all --json number,title,state,body --limit 500 --repo {owner}/{repo}

# View single issue
gh issue view {number} --repo {owner}/{repo} --json number,title,body,labels,comments,assignees,state,createdAt

# Create issue
gh issue create --title "{title}" --body "{body}" --label "{labels}" --repo {owner}/{repo}

# Edit issue (add/remove labels, update body)
gh issue edit {number} --repo {owner}/{repo} --add-label "{labels}"
gh issue edit {number} --repo {owner}/{repo} --remove-label "{labels}"
gh issue edit {number} --repo {owner}/{repo} --body "{body}"

# Comment on issue
gh issue comment {number} --body "{comment}" --repo {owner}/{repo}

# Close / reopen issue
gh issue close {number} --comment "{comment}" --repo {owner}/{repo}
gh issue reopen {number} --repo {owner}/{repo}
```

## PR Operations

```bash
# List open PRs with CI status
gh pr list --repo {owner}/{repo} --state open \
  --json number,title,author,headRefName,statusCheckRollup,mergeable,reviewDecision,isDraft --limit 100

# Check for existing PR on a branch
gh pr list --repo {owner}/{repo} --head {prefix}/{slug} --json number,url

# Create PR
gh pr create --repo {owner}/{repo} \
  --head {prefix}/{slug} --base {default_branch} \
  --title "{title}" --body "{body}"

# Merge PR (strategies)
gh pr merge {number} --repo {owner}/{repo} --merge --delete-branch     # regular merge
gh pr merge {number} --repo {owner}/{repo} --squash --delete-branch    # squash merge
gh pr merge {number} --repo {owner}/{repo} --squash --delete-branch --admin  # bypass checks
```

## Label Operations

```bash
# List existing labels
gh label list --repo {owner}/{repo} --json name --jq '.[].name'

# Create label (idempotent — append 2>&1 || true)
gh label create "{name}" --color "{hex}" --description "{desc}" --repo {owner}/{repo} 2>&1 || true
```

## API Calls

```bash
# Generic API call
gh api repos/{owner}/{repo}/{endpoint} --jq '{expression}'

# CI run logs
gh run view --log-failed
```

## Error Handling Conventions

| HTTP Status | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Process normally |
| 404 | Not found | Resource doesn't exist — legitimate FAIL |
| 403 | Forbidden | Insufficient permissions — report as WARN, not FAIL |
| 429 / rate limit | Rate limited | Report to user, do not retry in a loop |

### Idempotent Commands

Append `2>&1 || true` to `gh` commands that may return non-zero for expected conditions (e.g., label creation when label exists, resource checks returning 404). This prevents agents from treating expected non-zero exits as crashes.

### General Principles

- Never fail hard on a single API error — continue with remaining operations
- Distinguish "doesn't exist" (404 = FAIL) from "can't check" (403 = WARN)
- If authentication errors occur, stop and tell the user to re-authenticate

## Git Requirement

Git must be available for any skill that clones or modifies repositories.

```bash
git --version
```

## Repo Context Detection

After identifying the target repository, gather context to tailor checks and fixes.

### Tech Stack Detection

Scan the repository root for common project files to determine the tech stack:

| File(s) | Tech Stack | Relevant Templates |
|---------|------------|-------------------|
| `*.csproj`, `*.sln`, `*.fsproj` | .NET | VisualStudio.gitignore, dotnet CI |
| `package.json` | Node.js / JavaScript | Node.gitignore, npm CI |
| `Cargo.toml` | Rust | Rust.gitignore, cargo CI |
| `pyproject.toml`, `setup.py`, `requirements.txt` | Python | Python.gitignore, pip/pytest CI |
| `go.mod` | Go | Go.gitignore, go CI |
| `pom.xml`, `build.gradle` | Java / JVM | Java.gitignore, maven/gradle CI |
| `Gemfile` | Ruby | Ruby.gitignore, bundler CI |
| `composer.json` | PHP | Composer.gitignore, php CI |

If multiple indicators are found, the repo is multi-stack. Tailor .gitignore and CI suggestions to cover all detected stacks.

### Default Branch Name

```bash
gh repo view {owner}/{repo} --json defaultBranchRef -q '.defaultBranchRef.name'
```

Common values: `main`, `master`, `develop`. Always detect — assuming `main` breaks repos that use `master` or custom branch names.

### Visibility

```bash
gh repo view {owner}/{repo} --json isPrivate -q '.isPrivate'
```

Returns `true` (private) or `false` (public). Note this in reports and tailor advice accordingly (e.g., private repos may not need FUNDING.yml).

### Fork Status

```bash
gh repo view {owner}/{repo} --json isFork,parent -q '{fork: .isFork, parent: .parent.nameWithOwner}'
```

Forks inherit settings from upstream. If the repo is a fork, note this in reports — some checks (like branch protection) may not apply.

### Solo vs Team Repo

Detect whether the repository has a single maintainer or multiple collaborators:

```bash
gh api repos/{owner}/{repo}/collaborators --jq 'length'
```

- **Solo repo** (1 collaborator or API returns 403 on a personal repo): Adjust branch protection suggestions to not require PR reviews.
- **Team repo** (2+ collaborators or org-owned): Full branch protection with required reviews is appropriate.

If the collaborators API returns 403 (common for non-admin users), fall back to checking if the repo is org-owned:

```bash
gh repo view {owner}/{repo} --json owner -q '.owner.type'
```

- `User` = likely solo (unless collaborators were added)
- `Organization` = likely team

### Dependency Manager Detection

Check which dependency management tool is in use:

| Check | Tool |
|-------|------|
| `renovate.json`, `.github/renovate.json`, `.github/renovate.json5` exists | **Renovate** |
| Open issue titled "Dependency Dashboard" | **Renovate** |
| `.github/dependabot.yml` exists | **Dependabot** |
| Neither found | No automated dependency management |

This detection is critical for the Security Alerts check — do not suggest conflicting tools.

## Common Edge Cases

### Private Repositories

All `gh` checks work for private repos as long as the authenticated user has access. Note in the report header whether the repo is public or private, since some recommendations differ (e.g., FUNDING.yml is less relevant for private repos).

### Organization-Level Settings

Branch protection and security alert settings may be managed at the organization level. If API calls return 403 for these checks:
- Report the check as WARN (not FAIL).
- Add a note: "This setting may be managed at the organization level."

### Forks

Forks often inherit settings from the upstream repository. When the repo is a fork:
- Note it prominently in the report header.
- Branch protection, security settings, and issue templates may come from the parent repo.
- Some checks (like description and topics) are independent and should still be evaluated.

### Empty or New Repositories

If the repository has zero commits or was very recently created:
- Several checks will naturally fail (README, LICENSE, .gitignore, CI/CD).
- Add a note: "This appears to be a new repository — focus on Tier 1 items first."
- Branch protection may not be possible until there is at least one commit on the default branch.

### Archived Repositories

If `gh repo view` shows the repo is archived, warn the user that changes cannot be pushed. Health scanning is still useful for informational purposes, but ghs-backlog-fix will not work.

### Repos with Many Issues

Cap the terminal display at 20 issues (most recent), but save all issues to the backlog. Note in the output: "(+N more — see backlog/issues/ for full list)".

### Issues with Very Long Bodies

Truncate the issue body to 500 characters in backlog item files. Append "..." and include a link to the full issue on GitHub.
