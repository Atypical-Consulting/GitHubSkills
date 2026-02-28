# gh CLI Patterns

Common `gh` CLI patterns used across all GHS skills. All GitHub API interactions must use `gh` --- it handles authentication, pagination, and rate limiting automatically.

## Authentication

```bash
gh auth status
```

If this fails, instruct the user to run `gh auth login`. For project operations, verify the `project` scope:

```bash
gh auth status 2>&1 | grep -q "project" || echo "[FAIL] Run: gh auth refresh -s project"
```

## Repo Detection

| Priority | Source | Command |
|----------|--------|---------|
| 1 | Explicit argument | `owner/repo` from user input |
| 2 | Git remote | `gh repo view --json nameWithOwner -q '.nameWithOwner'` |
| 3 | Ask user | Prompt if detection fails |

## Repo Metadata Queries

| Query | Command |
|-------|---------|
| Default branch | `gh repo view {owner}/{repo} --json defaultBranchRef -q '.defaultBranchRef.name'` |
| Visibility | `gh repo view {owner}/{repo} --json isPrivate -q '.isPrivate'` |
| Fork status | `gh repo view {owner}/{repo} --json isFork,parent -q '{fork: .isFork, parent: .parent.nameWithOwner}'` |
| Owner type | `gh repo view {owner}/{repo} --json owner -q '.owner.type'` |
| Viewer permission | `gh repo view --json viewerPermission` |
| Authenticated user | `gh api user --jq '.login'` |

## Issue Operations

```bash
# List open issues
gh issue list --repo {owner}/{repo} --state open --json number,title,body,labels --limit 100

# View single issue
gh issue view {number} --repo {owner}/{repo} --json number,title,body,labels,comments,state

# Create issue
gh issue create --title "{title}" --body "{body}" --label "{labels}" --repo {owner}/{repo}

# Edit labels
gh issue edit {number} --repo {owner}/{repo} --add-label "{labels}"

# Comment on issue
gh issue comment {number} --body "{comment}" --repo {owner}/{repo}
```

## PR Operations

```bash
# List open PRs with CI status
gh pr list --repo {owner}/{repo} --state open \
  --json number,title,headRefName,statusCheckRollup,mergeable,reviewDecision --limit 100

# Create PR
gh pr create --repo {owner}/{repo} \
  --head {prefix}/{slug} --base {default_branch} \
  --title "{title}" --body "{body}"

# Merge PR
gh pr merge {number} --repo {owner}/{repo} --squash --delete-branch
```

## Label Operations

```bash
# List labels
gh label list --repo {owner}/{repo} --json name --jq '.[].name'

# Create label (idempotent)
gh label create "{name}" --color "{hex}" --description "{desc}" --repo {owner}/{repo} 2>&1 || true
```

## Project Operations

GitHub Projects (ProjectsV2) track health findings per repository. Key operations:

```bash
# List projects (filter by GHS prefix)
gh project list --owner {owner} --format json --jq '.projects[] | select(.title | startswith("[GHS]"))'

# Add draft item
gh project item-create {number} --owner {owner} --title "{title}" --body "{body}" --format json

# List items
gh project item-list {number} --owner {owner} --format json --limit 500

# Edit item field (requires 3-ID lookup: project ID, item ID, field ID)
gh project item-edit --project-id {project_node_id} --id {item_node_id} --field-id {field_node_id} --text "{value}"
```

## Tech Stack Detection

| File(s) | Tech Stack |
|---------|------------|
| `*.csproj`, `*.sln` | .NET |
| `package.json` | Node.js / JavaScript |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pyproject.toml`, `setup.py` | Python |
| `Gemfile` | Ruby |
| `pom.xml`, `build.gradle` | Java / JVM |

## Error Handling

| HTTP Status | Meaning | Action |
|-------------|---------|--------|
| 200 | Success | Process normally |
| 404 | Not found | Resource doesn't exist --- legitimate FAIL |
| 403 | Forbidden | Insufficient permissions --- report as WARN |
| 429 / rate limit | Rate limited | Report to user, do not retry in a loop |

Append `2>&1 || true` to `gh` commands that may return non-zero for expected conditions (e.g., label creation, resource checks returning 404).
