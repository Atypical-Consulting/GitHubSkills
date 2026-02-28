# Agent Spawning Reference

Patterns for parallel worktree-based agent execution. Used by ghs-repo-scan, ghs-backlog-fix, and ghs-issue-implement.

## Repository Cloning

Repos are cloned to `repos/` (gitignored, ephemeral working copies):

```bash
if [ -d "repos/{owner}_{repo}" ]; then
  git -C repos/{owner}_{repo} pull
else
  mkdir -p repos
  gh repo clone {owner}/{repo} repos/{owner}_{repo}
fi
```

Detect default branch after clone/pull:

```bash
git -C repos/{owner}_{repo} rev-parse --abbrev-ref HEAD
```

## Worktree Creation

Worktrees are **siblings** to the main clone, never inside it (nesting corrupts the git index):

```
repos/{owner}_{repo}/                                  <- main clone (stays on default branch)
repos/{owner}_{repo}--worktrees/{prefix}--{slug}/      <- one worktree per item
```

### Create

```bash
mkdir -p repos/{owner}_{repo}--worktrees

git -C repos/{owner}_{repo} worktree add \
  ../repos/{owner}_{repo}--worktrees/{prefix}--{slug} \
  -b {prefix}/{slug}
```

### Branch Prefix Convention

| Source | Prefix | Example |
|--------|--------|---------|
| Health fix | `fix/` | `fix/license` |
| Bug issue | `fix/` | `fix/42-login-crash` |
| Feature issue | `feat/` | `feat/15-dark-mode` |
| Docs issue | `docs/` | `docs/18-update-readme` |
| Hotfix issue | `fix/` | `fix/99-security-vuln` |
| Default | `impl/` | `impl/50-misc-task` |

### Pre-flight Checks

Before creating worktrees, check for conflicts:

```bash
# Existing remote branches
git -C repos/{owner}_{repo} ls-remote --heads origin 'refs/heads/{prefix}/*'

# Existing PRs for branch
gh pr list --repo {owner}/{repo} --head {prefix}/{slug} --json number,url
```

If branch exists and user confirms, use `-B` flag to force-create.

## Agent Spawning

All agents are spawned via the **Task tool** with `subagent_type: general-purpose`.

### Parallel Execution Pattern

Spawn all agents in a **single Task tool message** for parallel execution:

| Skill | Agents |
|-------|--------|
| ghs-repo-scan | 3 health check agents (one per tier) + 1 issues agent |
| ghs-backlog-fix | 1 Category A agent + N Category B agents + optional CI agent |
| ghs-issue-implement | N implementation agents (one per issue) |

### Agent Categories (ghs-backlog-fix)

| Category | Description | Worktree? | Agent Count |
|----------|-------------|-----------|-------------|
| A (API-only) | `gh` commands, no file changes | No | 1 (handles all API items) |
| B (file changes) | Create/modify files, commit, push, PR | Yes — one each | 1 per item |
| CI (special) | Diagnose CI failures before fixing | Yes | 1 per CI item |

### Context Budgeting (What to Pass to Agents)

Each agent prompt should include:
- Repository info: `{owner}`, `{repo}`, `{default_branch}`
- Item-specific info: tier, slug, check details, acceptance criteria
- Worktree path (for B/CI agents)
- Tech stack detection results
- Synced issue number (if applicable, for commit message `Fixes #{number}`)
- Analysis comment content (for issue-implement, if available from ghs-issue-analyze)

### Agent Result Contract

Every agent returns fenced JSON:

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

Category A agents handling multiple items return a JSON **array** of these objects.

## Agent Workflow in Worktree

1. Make changes in worktree directory only
2. Stage: `git -C {worktree_path} add {files}`
3. Commit: `git -C {worktree_path} commit -m "{message}"`
4. Push: `git -C {worktree_path} push -u origin {prefix}/{slug}`
5. Create PR: `gh pr create --repo {owner}/{repo} --head {prefix}/{slug} --base {default_branch} --title "{title}" --body "{body}"`
6. For issues: include `Fixes #{number}` in commit/PR body for auto-close

## Wave-Based Execution

When fixing multiple items with dependencies, organize agents into waves instead of spawning all at once. This prevents conflicts (e.g., a CI workflow fix that depends on `.editorconfig` being present).

### Dependency Detection

Before spawning agents, build a dependency graph from item classification:

| Item | Depends On | Reason |
|------|-----------|--------|
| CI workflow health | .editorconfig, .gitignore | Workflows may reference these files |
| Branch protection status checks | CI workflows | Status checks require passing workflows |
| CODEOWNERS | Team structure | CODEOWNERS references teams/users |
| Contributing guide | LICENSE, README | Links to these files |

### Wave Construction

```
1. Identify items with no dependencies → Wave 1
2. Identify items whose dependencies are all in Wave 1 → Wave 2
3. Repeat until all items are assigned
4. Items with circular dependencies → flag as NEEDS_HUMAN
```

### Execution Pattern

```
Wave 1: Spawn all Wave 1 agents in a single Task message (parallel)
  → Wait for all to complete
  → Recalculate health score (progress update)
  → Record results in STATE.md

Wave 2: Spawn all Wave 2 agents in a single Task message (parallel)
  → Only if Wave 1 dependencies passed
  → Skip items whose dependencies failed (mark as BLOCKED)
  → Wait for all to complete
  → Recalculate health score

Wave N: Continue until all waves complete
```

### When to Use Waves vs. Flat Parallel

| Scenario | Strategy |
|----------|----------|
| All items are independent (common case) | Flat parallel — single wave, same as current behavior |
| Dependencies detected between items | Wave-based — respect ordering |
| User requests specific ordering | Wave-based — user-defined waves |
| Single item | No waves needed — direct execution |

Flat parallel is the default. Wave-based execution activates only when the dependency graph has edges.

---

## Bounded Retries

| Attempt | Action |
|---------|--------|
| 1st failure | Re-run with error context appended to prompt |
| 2nd failure | Re-run with error + stricter constraints |
| 3rd failure | Mark as `NEEDS_HUMAN`, preserve worktree |

Content filter failures: retry with download-based approach (see `../edge-cases.md`).

## Worktree Cleanup

```bash
# Remove completed/failed worktrees
git -C repos/{owner}_{repo} worktree remove \
  ../repos/{owner}_{repo}--worktrees/{prefix}--{slug} --force

# Prune stale worktree references
git -C repos/{owner}_{repo} worktree prune

# Remove directory if empty
rmdir repos/{owner}_{repo}--worktrees 2>/dev/null || true
```

NEEDS_HUMAN worktrees are **not** cleaned up -- left in place with instructions for manual continuation.
