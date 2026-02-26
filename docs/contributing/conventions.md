# Conventions

## Naming
- Skill names: `ghs-` prefix + kebab-case (e.g., `ghs-repo-scan`)
- Directory names match skill names exactly
- Check slugs: kebab-case (e.g., `branch-protection`)
- Backlog files: `tier-{N}--{slug}.md` for health, `issue-{number}--{title-kebab}.md` for issues

## Trigger Phrases
- Include 2-4 natural trigger phrases in the skill description
- Cover common phrasings (e.g., "scan my repo", "audit my project", "run a health check")

## Status Indicators

| Indicator | Meaning | Color |
|-----------|---------|-------|
| `[PASS]` | Check passed | Green |
| `[FAIL]` | Check failed (action needed) | Red |
| `[WARN]` | Cannot verify (permissions/API) | Yellow |
| `[INFO]` | Informational (no score impact) | Blue |

## Terminal Output
- Use tables for structured data
- Progress bars: `████░░░░` (8 chars wide, filled with `█`, empty with `░`)
- Keep output scannable --- headers, spacing, alignment

## Allowed Tools

Common patterns:
- Read-only skills: `Read Glob`
- GitHub API skills: `Bash(gh:*) Read`
- Fix skills: `Bash(gh:*) Bash(git:*) Read Write Edit Glob Grep Task`

## Shared Resources
- Check registry: `.claude/skills/shared/checks/index.md`
- Scoring config: `.claude/skills/shared/config.md`
- Backlog format: `.claude/skills/shared/backlog-format.md`
- Agent contract: `.claude/skills/shared/agent-result-contract.md`
