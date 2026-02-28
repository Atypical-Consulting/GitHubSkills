# Shared Implementation Workflow

Reusable patterns for skills that clone repositories, create worktrees, and produce PRs. Referenced by `ghs-backlog-fix` and `ghs-issue-implement`.

---

## §1 — Repository Preparation

### Path Resolution

All paths must be **absolute** to avoid breakage when the working directory changes (e.g., inside subagents, after `cd`, or when skills run from different directories). Compute the root path once at the start:

```bash
# Resolve GHS_ROOT once at skill start (the GitHubSkills project root)
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

### Default Branch Detection

```bash
git -C "$REPO_PATH" rev-parse --abbrev-ref HEAD
```

### Tech Stack Detection

Scan the repo root for project files to determine the tech stack:

| File | Stack |
|------|-------|
| `*.csproj`, `*.sln` | .NET |
| `package.json` | Node.js / JavaScript |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `pyproject.toml`, `setup.py`, `requirements.txt` | Python |
| `Gemfile` | Ruby |
| `pom.xml`, `build.gradle` | Java / JVM |

See also `gh-prerequisites.md#repo-context-detection` for detailed detection logic.

---

## §2 — Worktree Management

### Path Convention

```
repos/{owner}_{repo}/                                  ← main clone (stays on default branch)
repos/{owner}_{repo}--worktrees/{prefix}--{slug}/      ← one worktree per item
```

- Worktrees are **siblings** to the main clone, never inside it — nesting worktrees inside the clone causes git to confuse working trees and corrupt the index.
- The `repos/` directory is gitignored — cloned repos are ephemeral working copies, not project artifacts.
- `{prefix}` is the branch prefix (e.g., `fix`, `feat`, `docs`, `impl`).
- `{slug}` is a short, kebab-case identifier for the item.

### Creation

```bash
WT_PATH="$WT_DIR/{prefix}--{slug}"
mkdir -p "$WT_DIR"

git -C "$REPO_PATH" worktree add "$WT_PATH" -b {prefix}/{slug}
```

### Cleanup

```bash
# For each completed item (PASS or FAILED, not NEEDS_HUMAN):
git -C "$REPO_PATH" worktree remove "$WT_DIR/{prefix}--{slug}" --force

# After all removals:
git -C "$REPO_PATH" worktree prune

# Remove the worktrees directory if empty:
rmdir "$WT_DIR" 2>/dev/null || true
```

### NEEDS_HUMAN Retention

For items that require human judgment, leave the worktree in place and print instructions:

```
[NEEDS_HUMAN] {slug} — worktree left at repos/{owner}_{repo}--worktrees/{prefix}--{slug}/
  Reason: {error message from agent}
  To continue manually: cd repos/{owner}_{repo}--worktrees/{prefix}--{slug}
  To remove: git -C repos/{owner}_{repo} worktree remove ../repos/{owner}_{repo}--worktrees/{prefix}--{slug}
```

---

## §3 — Branch / Commit / Push / PR Workflow

### Agent Instructions for File-Change Items

Each agent working in a worktree should:

1. **Make changes** in the worktree directory only — modifying the main clone would corrupt other agents' worktrees since they share the same git object store
2. **Stage files**:
   ```bash
   git -C {worktree_path} add {files}
   ```
3. **Commit** with a descriptive message:
   ```bash
   git -C {worktree_path} commit -m "{descriptive message}"
   ```
4. **Push** the branch:
   ```bash
   git -C {worktree_path} push -u origin {prefix}/{slug}
   ```
5. **Create a PR**:
   ```bash
   gh pr create --repo {owner}/{repo} \
     --head {prefix}/{slug} --base {default_branch} \
     --title "{title}" --body "{body}"
   ```

### PR Body Structure

The PR body should include:
- A summary of what was changed and why
- A reference to the source (backlog item path, issue number, etc.)
- Acceptance criteria as a checklist (if available) — reviewers need to know what "done" looks like
- For issues: include `Fixes #{number}` — this triggers GitHub's auto-close when the PR is merged

---

## §4 — Agent Result Contract

Every agent must return a fenced JSON object with this structure:

```json
{
  "source": "health|issue",
  "slug": "{identifier}",
  "status": "PASS|FAILED|NEEDS_HUMAN",
  "pr_url": "https://github.com/{owner}/{repo}/pull/N or null",
  "verification": ["List of verification checks performed"],
  "error": "Error message or null"
}
```

| Field | Description |
|-------|-------------|
| `source` | Where the item came from: `"health"` for backlog health checks, `"issue"` for GitHub issues |
| `slug` | Short identifier (e.g., `license`, `42-login-bug`) |
| `status` | `PASS` = fix applied successfully, `FAILED` = fix failed, `NEEDS_HUMAN` = requires manual intervention |
| `pr_url` | URL of created PR, or `null` for API-only fixes |
| `verification` | Array of verification steps that passed |
| `error` | Error description if status is FAILED or NEEDS_HUMAN, otherwise `null` |

For Category A agents handling multiple items, return a JSON **array** of these objects.

---

## §5 — Pre-flight Checks

### Branch Conflict Detection

Before creating worktrees, check for existing remote branches:

```bash
git -C "$REPO_PATH" ls-remote --heads origin 'refs/heads/{prefix}/*'
```

Flag any conflicts in the plan table with a warning indicator. If the user confirms, use the `-B` flag on `worktree add` to force-create the branch.

### Existing PR Detection

Check if a PR already exists for a branch:

```bash
gh pr list --repo {owner}/{repo} --head {prefix}/{slug} --json number,url
```

If a PR exists, skip creating a new one — report the existing PR URL instead.

---

## §6 — Content Filter Workaround

Some files (notably Code of Conduct) contain text that triggers API content filters when generated inline. If an agent fails with "Output blocked by content filtering policy", handle the item by downloading the canonical version from an official URL:

```bash
# Example: Code of Conduct
curl -sL "https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md" \
  -o CODE_OF_CONDUCT.md
sed -i '' 's/\[INSERT CONTACT METHOD\]/via GitHub issues/' CODE_OF_CONDUCT.md
```

The orchestrator should detect content filter failures and retry the item with this download-based approach rather than failing it outright.
