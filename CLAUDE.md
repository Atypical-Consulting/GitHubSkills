# GitHubSkills — Claude Skills for GitHub Repositories

A collection of Claude Code skills for auditing, managing, and improving GitHub repositories.

## Project Structure

```
.claude/skills/          — Skill definitions (SKILL.md files)
backlog/                 — Backlog items per repo (health findings + issues)
  {owner}_{repo}/
    SUMMARY.md           — Unified repo summary
    health/              — Health check findings
    issues/              — Open GitHub issues
repos/                   — Local clones of target repositories (gitignored)
.gh-skills/backlog-items/ — Ideas and planned skills not yet implemented
```

## Skill Conventions

- Each skill lives in `.claude/skills/<skill-name>/SKILL.md`
- Skill names use the `ghs-` prefix with `kebab-case` (e.g., `ghs-repo-scan`)
- Directory names match the skill name exactly (e.g., `ghs-repo-scan/`)
- Skills must use the `gh` CLI for all GitHub API interactions (never raw `curl` to api.github.com)
- Skills should handle errors gracefully: 404 = missing, 403 = insufficient permissions (don't fail hard)
- Output should be clean, scannable terminal text — use tables, status indicators (`[PASS]`, `[FAIL]`, `[WARN]`, `[INFO]`), and progress bars where appropriate
- Skills should detect the current repo from `gh repo view` when no explicit repo is provided
- Follow the SKILL.md frontmatter format: `name`, `description` (with trigger phrases)

## Available Skills

### Core Workflow (scan → sync → view → fix)

- **ghs-repo-scan** — Scan a repository for quality best practices and open issues, produce a scored report, and save all findings as structured markdown backlog items
- **ghs-backlog-board** — Show a dashboard of all backlog items (health + issues) across audited repositories with scores, progress, and next-action recommendations
- **ghs-backlog-fix** — Apply backlog item fixes using parallel worktree-based agents: clone the repo once, create worktrees, launch agents simultaneously, verify acceptance criteria, and create PRs

### Sync

- **ghs-backlog-sync** — Sync health backlog items to GitHub Issues for team visibility and tracking

### Issue Management (triage → analyze → implement)

- **ghs-issue-triage** — Verify and apply proper labels (type, priority, status) to GitHub issues
- **ghs-issue-analyze** — Deep-analyze a GitHub issue and post a structured analysis comment
- **ghs-issue-implement** — Implement a GitHub issue using worktree-based agents, then create a PR

### Actions

- **ghs-merge-prs** — Merge open PRs (own, Renovate, or all) with CI-aware confirmation, batch support, and automatic branch cleanup

### Utilities

- **ghs-backlog-score** — Calculate and display the health score for a repository from its backlog items
- **ghs-backlog-next** — Recommend the highest-impact next item to fix across all audited repositories

## Adding New Skills

1. Create `.claude/skills/ghs-<skill-name>/SKILL.md`
2. Include frontmatter with `name: ghs-<skill-name>`, `description` (with trigger phrases), `allowed-tools`, and `compatibility`
3. Define: Prerequisites, Input, Checks/Steps, Output Format
4. Update the "Available Skills" list above
