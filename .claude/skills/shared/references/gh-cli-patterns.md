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
