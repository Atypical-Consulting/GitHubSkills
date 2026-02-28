# Agent Spawning

Patterns for parallel worktree-based agent execution. GHS spawns sub-agents to perform health fixes and issue implementations concurrently, each in its own git worktree.

## Repository Cloning

Repos are cloned to `repos/` (gitignored). All paths must be resolved to **absolute paths** before use --- relative paths break inside subagents.

```bash
GHS_ROOT="$(cd "$(dirname "$(git rev-parse --git-dir)")" && pwd)"
REPO_PATH="$GHS_ROOT/repos/{owner}_{repo}"
WT_DIR="$GHS_ROOT/repos/{owner}_{repo}--worktrees"
```

## Worktree Layout

Worktrees are **siblings** to the main clone, never nested inside it (nesting corrupts the git index):

```
repos/{owner}_{repo}/                                  <- main clone
repos/{owner}_{repo}--worktrees/{prefix}--{slug}/      <- one worktree per item
```

### Branch Prefix Convention

| Source | Prefix | Example |
|--------|--------|---------|
| Health fix | `fix/` | `fix/license` |
| Bug issue | `fix/` | `fix/42-login-crash` |
| Feature issue | `feat/` | `feat/15-dark-mode` |
| Docs issue | `docs/` | `docs/18-update-readme` |
| Default | `impl/` | `impl/50-misc-task` |

## Parallel Execution

All agents are spawned via the Task tool with `subagent_type: general-purpose`. Agents are launched in a **single Task tool message** for parallel execution.

| Skill | Agents Spawned |
|-------|----------------|
| ghs-repo-scan | 3 health check agents (one per tier) + 1 issues agent |
| ghs-backlog-fix | 1 Category A agent + N Category B agents + optional CI agent |
| ghs-issue-implement | N implementation agents (one per issue) |

## Agent Categories

| Category | Description | Worktree? | Agent Count |
|----------|-------------|-----------|-------------|
| **A** (API-only) | `gh` commands, no file changes | No | 1 (handles all API items) |
| **B** (file changes) | Create/modify files, commit, push, PR | Yes --- one each | 1 per item |
| **CI** (special) | Diagnose CI failures before fixing | Yes | 1 per CI item |

## Context Budgeting

Each agent prompt includes:

- Repository info: owner, repo, default branch
- Item-specific info: tier, slug, check details, acceptance criteria
- Worktree path (for B/CI agents)
- Tech stack detection results
- Synced issue number (for `Fixes #N` in commits)
- Analysis comment content (for issue-implement, if available)

Agents return results via the [Agent Result Contract](./agent-contract) --- they do not write to the GitHub Project directly.

## Wave-Based Execution

When items have dependencies, agents are organized into waves instead of flat parallel execution.

### Dependency Examples

| Item | Depends On | Reason |
|------|-----------|--------|
| CI workflow health | .editorconfig, .gitignore | Workflows may reference these files |
| Branch protection status checks | CI workflows | Checks require passing workflows |
| Contributing guide | LICENSE, README | Links to these files |

### Wave Construction

1. Items with no dependencies go to Wave 1
2. Items whose dependencies are all in Wave 1 go to Wave 2
3. Repeat until all items are assigned
4. Circular dependencies are flagged as NEEDS_HUMAN

Flat parallel (single wave) is the default. Waves activate only when the dependency graph has edges.

## Bounded Retries

| Attempt | Action |
|---------|--------|
| 1st failure | Re-run with error context appended |
| 2nd failure | Re-run with error + stricter constraints |
| 3rd failure | Mark as `NEEDS_HUMAN`, preserve worktree |

## Worktree Cleanup

Completed and failed worktrees are removed after execution. NEEDS_HUMAN worktrees are left in place with instructions for manual continuation.

```bash
git -C "$REPO_PATH" worktree remove "$WT_DIR/{prefix}--{slug}" --force
git -C "$REPO_PATH" worktree prune
rmdir "$WT_DIR" 2>/dev/null || true
```
