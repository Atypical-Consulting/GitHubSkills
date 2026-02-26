# Adding a Skill

## Step 1: Create the Skill Directory

Create `.claude/skills/ghs-{name}/SKILL.md`.

## Step 2: Write the SKILL.md

Use this frontmatter format:

```yaml
---
name: ghs-{name}
description: |
  One-line description.

  Trigger: "trigger phrase 1", "trigger phrase 2"
allowed-tools: Bash(gh:*) Read [etc]
version: 1.0.0
compatibility: claude-code-v1
---
```

## Step 3: Structure the Skill

Follow this structure:
1. **Prerequisites** --- what the skill needs
2. **Input** --- what the user provides
3. **Phases** --- numbered steps the skill performs
4. **Output Format** --- terminal output specification
5. **Routing** --- what skills to suggest next

## Step 4: Register the Skill

Update `CLAUDE.md` in the "Available Skills" section with your new skill.

## Step 5: Test

Open Claude Code and trigger the skill with one of its trigger phrases.

## Tips

- Use the `gh` CLI for all GitHub API interactions
- Handle errors gracefully: 404 = missing, 403 = insufficient permissions
- Follow the status indicator convention: `[PASS]`, `[FAIL]`, `[WARN]`, `[INFO]`
- Use the `Task` tool for parallel agent work
- Reference shared configs from `.claude/skills/shared/`
