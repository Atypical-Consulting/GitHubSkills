---
name: apply-backlog-item
description: >
  Applies a backlog item fix to a GitHub repository — clones the repo, generates quality content,
  verifies acceptance criteria, and creates a PR. Use this skill whenever the user wants to apply,
  fix, or resolve a backlog item, references a backlog markdown file, or says things like "apply this
  backlog item", "fix this issue", "resolve this finding", "work on this backlog item", "apply
  tier-1--readme", or points to any file under backlog/. Also trigger when the user says "apply all
  backlog items", "fix all findings", or "resolve all tier 1 items".
---

# Apply Backlog Item

Read a structured backlog item (health finding or GitHub issue), apply the fix to the target repository, verify acceptance criteria, and update the item's status.

## Prerequisites

- The `gh` CLI must be authenticated (`gh auth status`)
- The user must have write access to the target repository
- `git` must be available

## Input

The user provides a path to a backlog item markdown file. This can be either:
- A health item: `backlog/phmatray_NewSLN/health/tier-1--description.md`
- An issue item: `backlog/phmatray_NewSLN/issues/issue-42--login-bug.md`

If the user says "apply all" or references multiple items, process them one at a time in priority order (health Tier 1 first, then Tier 2, Tier 3, then issues), confirming each before proceeding.

## Step 1 — Parse the Backlog Item

Read the markdown file and determine the item type from the `Source` field in the metadata table.

### Health items (Source: "Health Check")

Extract these fields:

| Field | Where to find it |
|-------|-----------------|
| **Check name** | The `# Title` at the top |
| **Repository** | The `Repository` row in the metadata table |
| **Tier** | The `Tier` row (e.g., "1 — Required") |
| **Points** | The `Points` row |
| **Current status** | The `Status` row (FAIL or WARN) |
| **What's missing** | The "What's Missing" section |
| **Quick fix** | The bash command in "How to Fix > Quick Fix" |
| **Full solution** | The prose/template in "How to Fix > Full Solution" |
| **Acceptance criteria** | The checkbox list in "Acceptance Criteria" |

### Issue items (Source: "Issue #N")

Extract these fields:

| Field | Where to find it |
|-------|-----------------|
| **Issue title** | The `# Title` at the top |
| **Repository** | The `Repository` row |
| **Issue number** | The `Source` row (parse the number from "Issue #N") |
| **Labels** | The `Labels` row |
| **Description** | The "Description" section |
| **GitHub URL** | The "References" section |

If the file doesn't match either structure, tell the user and stop.

## Step 2 — Prepare the Local Clone

Check if the target repo is already cloned locally:

```
repos/{owner}_{repo}/
```

This directory lives as a sibling to `backlog/` in the working directory.

- **If it exists**, `cd` into it and run `git pull` to get the latest.
- **If it doesn't exist**, clone it:
  ```bash
  mkdir -p repos
  gh repo clone {owner}/{repo} repos/{owner}_{repo}
  ```

After cloning/pulling, detect the default branch name and the tech stack by scanning for common project files (e.g., `*.csproj`, `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`).

## Step 3 — Plan the Fix

### For health items

Health items fall into two categories:

#### Category A — API-only fixes

These don't require file changes in the repo. They use `gh` commands directly.

Examples:
- **Description**: `gh repo edit {owner}/{repo} --description "..."`
- **Topics**: `gh repo edit {owner}/{repo} --add-topic ...`
- **Branch protection**: `gh api repos/{owner}/{repo}/branches/{branch}/protection -X PUT ...`
- **Security alerts**: `gh api repos/{owner}/{repo}/vulnerability-alerts -X PUT`

For these, craft the specific command based on the backlog item and the repo context. For description and topics, inspect the repo to propose meaningful values (don't use placeholders).

#### Category B — File creation / modification

These require creating or editing files in the local clone, then committing and pushing.

Examples:
- **README.md**: Generate a real README based on the repo's actual structure, tech stack, and license
- **.gitignore**: Use the appropriate GitHub template for the detected tech stack
- **CI/CD workflows**: Generate a workflow matching the detected build system
- **CODEOWNERS**: Use the repo owner as the default
- **Issue templates**: Create bug_report.md and feature_request.md
- **PR template**: Create a pull_request_template.md
- **SECURITY.md**: Generate with the owner's contact info
- **CONTRIBUTING.md**: Generate with setup instructions matching the tech stack

For file creation items, generate thoughtful, repo-aware content — not just the minimal quick-fix stub. Inspect the repo to understand:
- Project name and purpose (from existing files, directory structure)
- Tech stack and build tools
- Existing documentation patterns
- License type

### For issue items

Issue fixes are always Category B (file changes + PR). The approach:

1. Read the full issue from GitHub to get the complete body (the backlog item may have a truncated version):
   ```bash
   gh issue view {number} --repo {owner}/{repo}
   ```
2. Understand what the issue is asking for
3. Plan the code changes needed
4. The PR will reference the issue with "Fixes #{number}" to auto-close it on merge

### Present the plan

Before executing, show the user:

```
## Plan: {Title}

Repository: {owner}/{repo}
Source:     {Health Check — Tier N | Issue #N}
Branch:     fix/{slug} (from {default_branch})

### What I'll do:
{Numbered list of specific actions}

### Files to create/modify:
{List of files, or "None — API-only fix"}

Proceed? (y/n)
```

Wait for user confirmation before continuing.

## Step 4 — Apply the Fix

### For API-only fixes (health Category A):

Run the `gh` command and capture the output. Verify the command succeeded (exit code 0).

### For file changes (health Category B and all issue fixes):

1. Create a feature branch from the default branch:
   ```bash
   git checkout -b fix/{slug}
   ```
   For health items, the slug is `{check-name-kebab}`. For issues, use `issue-{number}--{title-kebab}` (truncated).

2. Create or modify the files as planned
3. Stage and commit:
   ```bash
   git add {files}
   git commit -m "{descriptive message}"
   ```
   For issue fixes, include "Fixes #{number}" in the commit message.
4. Push the branch:
   ```bash
   git push -u origin fix/{slug}
   ```
5. Create a PR:
   ```bash
   gh pr create --title "{title}" --body "{body}" --base {default_branch}
   ```
   The PR body should:
   - For health items: reference the backlog item and include acceptance criteria as a checklist
   - For issue items: include "Fixes #{number}" to auto-close the issue, and summarize the changes

## Step 5 — Verify Acceptance Criteria

### For health items

After applying the fix, verify each acceptance criterion from the backlog item.

For API-based checks, use `gh api` to confirm the change took effect. For file-based checks, confirm the file exists and meets the criteria (e.g., README > 500 bytes).

Report results:

```
## Verification

- [x] Repository description is a non-empty string
- [x] Description appears in `gh repo view` output
```

If any criterion fails, report which ones failed and suggest corrective action. Do not update the backlog item status.

### For issue items

Verification is simpler — confirm:
- The PR was created successfully
- The PR references the issue number
- The files were modified as planned

## Step 6 — Update the Backlog Item

Once verification passes:

### For health items

1. **Update the backlog item file**: Change `| **Status** | FAIL |` to `| **Status** | PASS |` and check all acceptance criteria boxes.

2. **Update SUMMARY.md**: Find the item's row in the Health — Action Items table and change its status from `FAIL` to `PASS`. If a PR was created, add the PR URL.

3. **Report to the user**:
   ```
   ## Done

   [PASS] {Check Name} — {one-line summary of what was done}
   PR: {url if created, or "N/A — API-only fix"}
   Points recovered: {points}
   ```

### For issue items

1. **Update the backlog item file**: Change `| **Status** | OPEN |` to `| **Status** | PR CREATED |` and add a `| **PR** | {url} |` row to the metadata table.

2. **Update SUMMARY.md**: Find the issue row in the Open Issues table and add the PR link.

3. **Report to the user**:
   ```
   ## Done

   [PR] Issue #{number}: {title} — {one-line summary}
   PR: {url}
   Issue will auto-close when PR is merged.
   ```

## Edge Cases

- **WARN items**: These indicate permission issues. Before applying, check if the user now has sufficient permissions. If not, explain what permissions are needed.
- **Already PASS**: If the status is already PASS, tell the user and skip.
- **Already closed issues**: If the issue is already closed on GitHub, update the local backlog item status to CLOSED and skip.
- **Multiple items**: When processing multiple items, process health Tier 1 first, then Tier 2, Tier 3, then issues by age (oldest first).
- **Merge conflicts**: If the feature branch can't be created cleanly, report the conflict and let the user decide how to proceed.
- **PR already exists**: Check if a branch `fix/{slug}` already exists. If so, ask the user whether to update it or create a new one.
- **Complex issues**: Some issues may require significant code changes. If the issue seems too complex to auto-fix, present a plan and let the user guide the implementation.
