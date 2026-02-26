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

Read a structured backlog item, apply the fix to the target repository, verify acceptance criteria, and update the item's status.

## Prerequisites

- The `gh` CLI must be authenticated (`gh auth status`)
- The user must have write access to the target repository
- `git` must be available

## Input

The user provides a path to a backlog item markdown file (e.g., `backlog/phmatray_NewSLN/health-report/tier-1--description.md`).

If the user says "apply all" or references multiple items, process them one at a time in tier order (Tier 1 first), confirming each before proceeding.

## Step 1 — Parse the Backlog Item

Read the markdown file and extract these fields from the structured format:

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

If the file doesn't match this structure, tell the user and stop.

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

Backlog items fall into two categories. Determine which applies and plan accordingly.

### Category A — API-only fixes

These don't require file changes in the repo. They use `gh` commands directly.

Examples:
- **Description**: `gh repo edit {owner}/{repo} --description "..."`
- **Topics**: `gh repo edit {owner}/{repo} --add-topic ...`
- **Branch protection**: `gh api repos/{owner}/{repo}/branches/{branch}/protection -X PUT ...`
- **Security alerts**: `gh api repos/{owner}/{repo}/vulnerability-alerts -X PUT`

For these, craft the specific command based on the backlog item and the repo context. For description and topics, inspect the repo to propose meaningful values (don't use placeholders).

### Category B — File creation / modification

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

### Present the plan

Before executing, show the user:

```
## Plan: {Check Name}

Repository: {owner}/{repo}
Category:   {A — API-only | B — File creation}
Branch:     fix/{check-name-kebab} (from {default_branch})

### What I'll do:
{Numbered list of specific actions}

### Files to create/modify:
{List of files, or "None — API-only fix"}

Proceed? (y/n)
```

Wait for user confirmation before continuing.

## Step 4 — Apply the Fix

### For API-only fixes:

Run the `gh` command and capture the output. Verify the command succeeded (exit code 0).

### For file creation fixes:

1. Create a feature branch from the default branch:
   ```bash
   git checkout -b fix/{check-name-kebab}
   ```
2. Create or modify the files as planned
3. Stage and commit:
   ```bash
   git add {files}
   git commit -m "{descriptive message}"
   ```
4. Push the branch:
   ```bash
   git push -u origin fix/{check-name-kebab}
   ```
5. Create a PR:
   ```bash
   gh pr create --title "{title}" --body "{body}" --base {default_branch}
   ```
   The PR body should reference the backlog item and include the acceptance criteria as a checklist.

## Step 5 — Verify Acceptance Criteria

After applying the fix, verify each acceptance criterion from the backlog item.

For API-based checks, use `gh api` to confirm the change took effect. For file-based checks, confirm the file exists and meets the criteria (e.g., README > 500 bytes).

Report results:

```
## Verification

- [x] Repository description is a non-empty string
- [x] Description appears in `gh repo view` output
```

If any criterion fails, report which ones failed and suggest corrective action. Do not update the backlog item status.

## Step 6 — Update the Backlog Item

Once all acceptance criteria pass:

1. **Update the backlog item file**: Change `| **Status** | FAIL |` to `| **Status** | PASS |` and check all acceptance criteria boxes.

2. **Update SUMMARY.md**: Find the item's row in the Action Items table and change its status from `FAIL` to `PASS`. If a PR was created, add the PR URL. Move the item from "Action Items" to "Passing Checks" if you want a clean summary — but at minimum update the status column.

3. **Report to the user**:
   ```
   ## Done

   [PASS] {Check Name} — {one-line summary of what was done}
   PR: {url if created, or "N/A — API-only fix"}
   Points recovered: {points}
   ```

## Edge Cases

- **WARN items**: These indicate permission issues. Before applying, check if the user now has sufficient permissions. If not, explain what permissions are needed.
- **Already PASS**: If the status is already PASS, tell the user and skip.
- **Multiple items**: When processing multiple items, some may depend on others (e.g., CI/CD workflows reference branch names). Process Tier 1 first, then Tier 2, then Tier 3.
- **Merge conflicts**: If the feature branch can't be created cleanly, report the conflict and let the user decide how to proceed.
- **PR already exists**: Check if a branch `fix/{check-name-kebab}` already exists. If so, ask the user whether to update it or create a new one.
