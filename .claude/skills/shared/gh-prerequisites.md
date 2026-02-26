# GitHub CLI Prerequisites and Error Handling

Shared prerequisites, repo detection, context detection, and common edge cases for all skills. Consumed by: ghs-repo-scan, ghs-backlog-fix, ghs-backlog-board, ghs-issue-triage, ghs-issue-analyze, ghs-issue-implement, ghs-merge-prs.

## Table of Contents

1. [Required Tools](#required-tools)
2. [Permission and Error Handling](#permission-and-error-handling)
3. [Repo Detection](#repo-detection)
4. [Repo Context Detection](#repo-context-detection)
5. [Common Edge Cases](#common-edge-cases)

---

## Required Tools

### gh CLI

The GitHub CLI must be installed and authenticated.

```bash
gh auth status
```

- If this fails, instruct the user to run `gh auth login`.
- All GitHub API interactions must use `gh api` or `gh` subcommands — `gh` handles authentication tokens, pagination, and rate limiting automatically; raw `curl` would need all of that manually.

### Git

Git must be available for any skill that clones or modifies repositories.

```bash
git --version
```

---

## Permission and Error Handling

Handle API errors gracefully based on HTTP status codes:

| Status | Meaning | Action |
|--------|---------|--------|
| **200** | Success | Process the response normally |
| **404** | Not found | The resource does not exist. This is a legitimate check failure (FAIL). |
| **403** | Forbidden | Insufficient permissions. Report as "unable to check (insufficient permissions)". Do **not** count as FAIL -- use WARN status instead. |
| **429** / rate limit headers | Rate limited | Wait for the `Retry-After` duration (or 60 seconds if not specified) and retry **once**. If the retry also fails, report the error and continue. |

### General principles

- Never fail hard on a single API error — one failing check shouldn't prevent the other 15+ checks from running. Report the error for that check and continue.
- Distinguish between "the thing doesn't exist" (404 = FAIL) and "we can't check" (403 = WARN) — WARN items are excluded from scoring so users aren't penalized for permission gaps.
- If `gh` commands fail with authentication errors, stop and tell the user to re-authenticate.

---

## Repo Detection

When the user does not provide an `owner/repo` argument, detect it automatically.

### Detection order

1. **Explicit argument**: If the user provides `owner/repo`, use it directly.
2. **Current git remote**: If in a git repository, detect from the remote:
   ```bash
   gh repo view --json nameWithOwner -q '.nameWithOwner'
   ```
3. **Ask the user**: If neither method works, prompt: "Which repository should I scan? Please provide it in `owner/repo` format."

### Validation

After detection, verify the repo is accessible:

```bash
gh repo view {owner}/{repo} --json name -q '.name'
```

If this fails with 404, the repo doesn't exist or the user lacks access. Report clearly.

---

## Repo Context Detection

After identifying the target repository, gather context to tailor checks and fixes.

### Tech stack detection

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

### Default branch name

```bash
gh repo view {owner}/{repo} --json defaultBranchRef -q '.defaultBranchRef.name'
```

Common values: `main`, `master`, `develop`. Always detect — assuming `main` breaks repos that use `master` or custom branch names.

### Visibility

```bash
gh repo view {owner}/{repo} --json isPrivate -q '.isPrivate'
```

Returns `true` (private) or `false` (public). Note this in reports and tailor advice accordingly (e.g., private repos may not need FUNDING.yml).

### Fork status

```bash
gh repo view {owner}/{repo} --json isFork,parent -q '{fork: .isFork, parent: .parent.nameWithOwner}'
```

Forks inherit settings from upstream. If the repo is a fork, note this in reports -- some checks (like branch protection) may not apply.

### Solo vs team repo

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

### Dependency manager detection

Check which dependency management tool is in use:

| Check | Tool |
|-------|------|
| `renovate.json`, `.github/renovate.json`, `.github/renovate.json5` exists | **Renovate** |
| Open issue titled "Dependency Dashboard" | **Renovate** |
| `.github/dependabot.yml` exists | **Dependabot** |
| Neither found | No automated dependency management |

This detection is critical for the Security Alerts check -- do not suggest conflicting tools.

---

## Common Edge Cases

### Private repositories

All `gh` checks work for private repos as long as the authenticated user has access. Note in the report header whether the repo is public or private, since some recommendations differ (e.g., FUNDING.yml is less relevant for private repos).

### Organization-level settings

Branch protection and security alert settings may be managed at the organization level. If API calls return 403 for these checks:
- Report the check as WARN (not FAIL).
- Add a note: "This setting may be managed at the organization level."

### Forks

Forks often inherit settings from the upstream repository. When the repo is a fork:
- Note it prominently in the report header.
- Branch protection, security settings, and issue templates may come from the parent repo.
- Some checks (like description and topics) are independent and should still be evaluated.

### Empty or new repositories

If the repository has zero commits or was very recently created:
- Several checks will naturally fail (README, LICENSE, .gitignore, CI/CD).
- Add a note: "This appears to be a new repository -- focus on Tier 1 items first."
- Branch protection may not be possible until there is at least one commit on the default branch.

### Archived repositories

If `gh repo view` shows the repo is archived, warn the user that changes cannot be pushed. Health scanning is still useful for informational purposes, but ghs-backlog-fix will not work.

### Repos with many issues

Cap the terminal display at 20 issues (most recent), but save all issues to the backlog. Note in the output: "(+N more -- see backlog/issues/ for full list)".

### Issues with very long bodies

Truncate the issue body to 500 characters in backlog item files. Append "..." and include a link to the full issue on GitHub.
