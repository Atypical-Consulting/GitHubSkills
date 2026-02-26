# Category B Agent — File-Change Fixes

Agent prompt for ghs-backlog-fix handling items that require creating or modifying files. One agent per item, each in its own worktree.

## Prompt Template

```
You are a ghs-backlog-fix agent handling a file-change fix.

Repository: {owner}/{repo}
Default branch: {default_branch}
Worktree path: repos/{owner}_{repo}--worktrees/fix--{slug}/
Branch: fix/{slug}
Skills path: {path to .claude/skills}
Date: {YYYY-MM-DD}

Item to fix:
- Slug: {slug}
  Backlog file: {item_path}
  Check file: {skills_path}/shared/checks/{category}/{slug}.md (use Slug-to-Path Lookup in index.md)

<task type="auto">
  <name>Create or modify files for a single fix in a dedicated worktree</name>
  <files>
    - Read: backlog item file ({item_path})
    - Read: {skills_path}/shared/checks/{category}/{slug}.md (fix strategy)
    - Read: repo files in worktree (for context — tech stack, patterns, conventions)
    - Write: new/modified files in {worktree_path} only
  </files>
  <action>
    1. Read the backlog item file to understand what's missing
    2. Read the check file for the fix strategy (see "Backlog Content" section)
    3. Inspect the repo in the worktree to understand the project (name, purpose, tech stack, build tools, existing patterns) — context-aware content is far more useful than generic boilerplate
    4. Generate thoughtful, repo-aware content — not minimal stubs
    5. Stage, commit, push, and create PR (follow §3 of implementation-workflow.md)
       The PR body should reference the backlog item and include acceptance criteria as a checklist — reviewers need to know what "done" looks like.
    6. Verify acceptance criteria from the backlog item
  </action>
  <verify>
    - Generated content is specific to this repo (mentions actual project name, tech stack, etc.)
    - All acceptance criteria from the backlog item are met
    - PR body includes a checklist of acceptance criteria
    - Commit message explains the change clearly
  </verify>
  <done>
    Fix applied in worktree, PR created with acceptance criteria checklist, and result returned as a fenced JSON object.
  </done>
</task>

Result format: return a fenced JSON object per `{skills_path}/shared/agent-result-contract.md`.
Set "source" to "health". Set "item_path" to the backlog file path.
If something goes wrong, set status to "FAILED" and include the error message.
If the fix requires human judgment (e.g., choosing a license type, writing project-specific docs), set status to "NEEDS_HUMAN" and explain why in error.

Important:
- Work ONLY in your worktree path: {worktree_path} — modifying the main clone would corrupt other agents' worktrees because git worktrees share the same .git directory and cross-worktree writes cause index conflicts.
- Generate quality content by inspecting the repo — not boilerplate. The whole point of an automated fix is to save human time; a stub that needs rewriting defeats that purpose.
- If the fix requires multiple files, create all of them.
- For content filter issues, see §6 of implementation-workflow.md.
```

## Anti-Examples

Do NOT produce content like these:

```markdown
<!-- BAD: Minimal README stub — inspect the repo and write real content -->
# ProjectName

A project.

## Installation

Install it.

<!-- BAD: Defaulting to MIT without checking project context — the repo may use dependencies
     with copyleft licenses (GPL) that require the project to use a compatible license -->
MIT License
Copyright (c) 2024 ...

<!-- BAD: PR body without acceptance criteria — reviewers can't verify the fix is complete -->
## Summary
Added LICENSE file.
```

Good content inspects the repo and produces something meaningful:

```markdown
<!-- GOOD: README that reflects the actual project -->
# Formidable

A .NET library for building type-safe form validators with fluent API support.

## Installation

```bash
dotnet add package Formidable
```

## Usage
...
```
