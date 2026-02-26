# GitHubSkills — Claude Skills for GitHub Repositories

A collection of Claude Code skills for auditing, managing, and improving GitHub repositories.

## Project Structure

```
.claude/skills/          — Skill definitions (SKILL.md files)
backlog/                 — Saved health report backlog items per repo
.gh-skills/backlog-items/ — Ideas and planned skills not yet implemented
```

## Skill Conventions

- Each skill lives in `.claude/skills/<skill-name>/SKILL.md`
- Skill names use `kebab-case`
- Skills must use the `gh` CLI for all GitHub API interactions (never raw `curl` to api.github.com)
- Skills should handle errors gracefully: 404 = missing, 403 = insufficient permissions (don't fail hard)
- Output should be clean, scannable terminal text — use tables, status indicators (`[PASS]`, `[FAIL]`, `[WARN]`, `[INFO]`), and progress bars where appropriate
- Skills should detect the current repo from `gh repo view` when no explicit repo is provided
- Follow the SKILL.md frontmatter format: `name`, `description` (with trigger phrases)

## Available Skills

- **repo-health-check** — Audit a repository against quality best practices, produce a scored health report, and save actionable findings as structured markdown backlog items

## Adding New Skills

1. Create `.claude/skills/<skill-name>/SKILL.md`
2. Include frontmatter with `name` and `description` (include trigger phrases in the description)
3. Define: Prerequisites, Input, Checks/Steps, Output Format
4. Update the "Available Skills" list above
