# Adding a Skill

## Step 1: Create the Skill Directory

Create `.claude/skills/ghs-{name}/SKILL.md`.

## Step 2: Write the SKILL.md

### Frontmatter

Use this frontmatter format with all required fields:

```yaml
---
name: ghs-{name}
description: >
  One-line description.

  Trigger: "trigger phrase 1", "trigger phrase 2".
  Do NOT use for {out-of-scope tasks} (use {other-skill}).
argument-hint: "[owner/repo] [--flag <value>]"
allowed-tools: "Bash(gh:*) Read [etc]"
compatibility: "Requires gh CLI (authenticated), git, network access"
license: MIT
metadata:
  author: your-name
  version: 1.0.0
routes-to:
  - ghs-{next-skill}
routes-from:
  - ghs-{previous-skill}
---
```

### Frontmatter Fields

| Field | Required | Description |
|-------|----------|-------------|
| `name` | Yes | Skill identifier with `ghs-` prefix (e.g., `ghs-repo-scan`) |
| `description` | Yes | Multi-line description with trigger phrases and "Do NOT use for" routing |
| `argument-hint` | Yes | Free-form string showing expected args: `<required>`, `[optional]`, `(no arguments)` |
| `allowed-tools` | Yes | Tool whitelist for the skill's execution |
| `compatibility` | Yes | Runtime requirements (gh CLI, git, jq, etc.) |
| `license` | Yes | License identifier (MIT) |
| `metadata` | Yes | Author and version info |
| `routes-to` | No | Skills suggested after this one completes |
| `routes-from` | No | Skills that may invoke this one |

### Argument Hint Syntax

The `argument-hint` field documents what arguments the skill accepts:

| Syntax | Meaning | Example |
|--------|---------|---------|
| `<arg>` | Required argument | `<owner/repo#number>` |
| `[arg]` | Optional argument | `[owner/repo]` |
| `(no arguments)` | Skill takes no args | `(no arguments)` |
| `--flag` | Boolean flag | `--dry-run` |
| `--flag <value>` | Value flag | `--tier 1\|2\|3` |

## Step 3: Structure the Body

### Required Body Tags

Wrap major sections in XML tags following GSD conventions:

| Tag | Required | Purpose |
|-----|----------|---------|
| `<execution_context>` | Yes | Lists shared reference files the skill depends on |
| `<required_reading>` | Yes | Prerequisites to read before execution (state, project data, etc.) |
| `<context>` | Yes | Purpose, roles, key definitions |
| `<anti-patterns>` | Yes | 3-column `Do NOT \| Do Instead \| Why` table |
| `<objective>` | Yes | Goal, outputs, next actions |
| `<process>` | Yes | Step-by-step execution flow |
| `<rules>` | No | Additional constraints |
| `<examples>` | No | Good/bad output pairs |

### Execution Context

List all shared references the skill depends on inside `<execution_context>`:

```xml
<execution_context>
References:
- ../shared/references/gh-cli-patterns.md
- ../shared/references/output-conventions.md
- ../shared/references/ui-brand.md
- ../shared/references/argument-parsing.md
</execution_context>
```

### Required Reading

Declare what data must be loaded before execution:

```xml
<required_reading>
- Read project items via `gh project item-list` before any operation
- Check state issue for blockers and previous session context
</required_reading>
```

## Step 4: Use Templates for Generated Output

For skills that generate PRs, comments, or issues, use the reusable templates in `.claude/skills/shared/templates/`:

| Template | Used By | Purpose |
|----------|---------|---------|
| `pr-body.md` | backlog-fix, issue-implement, action-fix | PR description body |
| `analysis-comment.md` | issue-analyze | Issue analysis comment |
| `review-comment.md` | review-pr | PR review comment |
| `state-issue-body.md` | backlog-fix, orchestrate, dev-loop | State issue body |
| `sync-issue-body.md` | backlog-sync | Synced issue body |

Templates use `{placeholder}` syntax for variable substitution.

## Step 5: Add Dry-Run Support (Mutation Skills)

If your skill modifies external state (creates PRs, merges, creates releases), add `--dry-run` support:

- Document `--dry-run` in the `argument-hint` field
- Add a "Dry-Run Mode" section in the `<process>` block
- Prefix all would-be mutations with `[DRY RUN]` in output
- Display the dry-run indicator box from `ui-brand.md`

## Step 6: Register the Skill

Update `CLAUDE.md` in the "Available Skills" section with your new skill.

## Step 7: Test

Open Claude Code and trigger the skill with one of its trigger phrases.

## Tips

- Use the `gh` CLI for all GitHub API interactions
- Handle errors gracefully: 404 = missing, 403 = insufficient permissions
- Follow the status indicator convention: `[PASS]`, `[FAIL]`, `[WARN]`, `[INFO]`
- Use the `Task` tool for parallel agent work
- Reference shared docs from `.claude/skills/shared/references/`
- Use templates from `.claude/skills/shared/templates/` for generated output
- Use typed checkpoints from `checkpoint-patterns.md` for human-in-the-loop interactions
- Follow the visual branding from `ui-brand.md` for stage banners, boxes, and symbols
