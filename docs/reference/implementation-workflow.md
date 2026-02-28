# Implementation Workflow

Reusable patterns for skills that clone repositories, create worktrees, and produce PRs. Referenced by ghs-backlog-fix and ghs-issue-implement.

## Repository Preparation

### Path Resolution

All paths must be **absolute** to avoid breakage inside subagents or after directory changes:

```bash
GHS_ROOT="$(cd "$(dirname "$(git rev-parse --git-dir)")" && pwd)"
REPO_PATH="$GHS_ROOT/repos/{owner}_{repo}"
WT_DIR="$GHS_ROOT/repos/{owner}_{repo}--worktrees"
```

### Clone or Pull

```bash
if [ -d "$REPO_PATH" ]; then
  git -C "$REPO_PATH" pull --ff-only
else
  mkdir -p "$GHS_ROOT/repos"
  gh repo clone {owner}/{repo} "$REPO_PATH"
fi
```

### Tech Stack Detection

| File | Stack |
|------|-------|
| `*.csproj`, `*.sln` | .NET |
| `package.json` | Node.js / JavaScript |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pyproject.toml`, `setup.py` | Python |
| `Gemfile` | Ruby |
| `pom.xml`, `build.gradle` | Java / JVM |

## Worktree Management

### Layout

```
repos/{owner}_{repo}/                                  <- main clone (default branch)
repos/{owner}_{repo}--worktrees/{prefix}--{slug}/      <- one worktree per item
```

Worktrees are **siblings** to the main clone, never nested inside it. The `repos/` directory is gitignored.

### Creation

```bash
WT_PATH="$WT_DIR/{prefix}--{slug}"
mkdir -p "$WT_DIR"
git -C "$REPO_PATH" worktree add "$WT_PATH" -b {prefix}/{slug}
```

### Cleanup

Completed and failed worktrees are removed. NEEDS_HUMAN worktrees are left in place with instructions:

```
[NEEDS_HUMAN] {slug} --- worktree left at repos/{owner}_{repo}--worktrees/{prefix}--{slug}/
  To continue: cd repos/{owner}_{repo}--worktrees/{prefix}--{slug}
  To remove:   git -C repos/{owner}_{repo} worktree remove <path>
```

## Branch / Commit / Push / PR

Each agent in a worktree follows this workflow:

1. **Make changes** in the worktree directory only
2. **Stage**: `git -C {worktree_path} add {files}`
3. **Commit**: `git -C {worktree_path} commit -m "{message}"`
4. **Push**: `git -C {worktree_path} push -u origin {prefix}/{slug}`
5. **Create PR**: `gh pr create --repo {owner}/{repo} --head {prefix}/{slug} --base {default_branch} --title "{title}" --body "{body}"`

For issues, include `Fixes #{number}` in the commit or PR body to trigger GitHub's auto-close on merge.

## Pre-flight Checks

### Branch Conflict Detection

```bash
git -C "$REPO_PATH" ls-remote --heads origin 'refs/heads/{prefix}/*'
```

If a branch exists and the user confirms, use `-B` to force-create.

### Existing PR Detection

```bash
gh pr list --repo {owner}/{repo} --head {prefix}/{slug} --json number,url
```

If a PR already exists, skip creation and report the existing URL.

## Content Filter Workaround

If an agent fails with "Output blocked by content filtering policy", retry with a download-based approach:

```bash
curl -sL "{canonical_url}" -o {filename}
sed -i '' 's/\[INSERT CONTACT METHOD\]/via GitHub issues/' {filename}
```

## Agent Result Contract

Every agent returns a fenced JSON result:

```json
{
  "source": "health|issue",
  "slug": "{identifier}",
  "status": "PASS|FAILED|NEEDS_HUMAN",
  "pr_url": "https://github.com/{owner}/{repo}/pull/N or null",
  "verification": ["List of checks performed"],
  "error": "Error message or null"
}
```

See [Agent Result Contract](./agent-contract) for full details.
