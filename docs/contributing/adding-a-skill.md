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

Wrap major sections in XML tags following GSD conventions:

1. **`<context>`** --- purpose, roles, shared references table
2. **`<anti-patterns>`** --- 3-column table: `Do NOT | Do Instead | Why`
3. **`<objective>`** --- expected outputs and routing
4. **`<process>`** --- phased execution steps
5. **`<rules>`** --- rule/trigger/example triples (if applicable)

## Step 4: Register the Skill

Update `CLAUDE.md` in the "Available Skills" section with your new skill.

## Step 5: Test

Open Claude Code and trigger the skill with one of its trigger phrases.

## Tips

- Use the `gh` CLI for all GitHub API interactions
- Handle errors gracefully: 404 = missing, 403 = insufficient permissions
- Follow the status indicator convention: `[PASS]`, `[FAIL]`, `[WARN]`, `[INFO]`
- Use the `Task` tool for parallel agent work
- Reference shared docs from `.claude/skills/shared/references/`
