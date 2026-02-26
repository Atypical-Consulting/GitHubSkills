---
name: apply-backlog-item
description: >
  Applies a backlog item fix to a GitHub repository — clones the repo, generates quality content,
  verifies acceptance criteria, and creates a PR. Use this skill whenever the user wants to apply,
  fix, or resolve a backlog item, references a backlog markdown file, or says things like "apply this
  backlog item", "fix this issue", "resolve this finding", "work on this backlog item", "apply
  tier-1--readme", or points to any file under backlog/. Also trigger when the user says "apply all
  backlog items", "fix all findings", or "resolve all tier 1 items".
  Do NOT use for scanning repos (use repo-scan), viewing backlog status (use backlog-dashboard), or general code review.
metadata:
  author: phmatray
  version: 2.0.0
---

# Apply Backlog Item

Read a structured backlog item (health finding or GitHub issue), apply the fix to the target repository, verify acceptance criteria, and update the item's status.

## Prerequisites

See `../shared/gh-prerequisites.md` for authentication, repo detection, and error handling.

Additionally, the user must have **write access** to the target repository (required for pushing branches and creating PRs).

## Input

The user provides a path to a backlog item markdown file. This can be either:
- A health item: `backlog/phmatray_NewSLN/health/tier-1--description.md`
- An issue item: `backlog/phmatray_NewSLN/issues/issue-42--login-bug.md`

If the user says "apply all" or references multiple items, process them one at a time in priority order (health Tier 1 first, then Tier 2, Tier 3, then issues), confirming each before proceeding.

## Step 1 — Parse the Backlog Item

Read the markdown file and determine the item type from the `Source` field in the metadata table.

For the backlog item format specification, see `../shared/backlog-format.md`.

You can parse backlog items programmatically: `python ../shared/scripts/parse_backlog_item.py <path-to-item.md>`

### Health items (Source: "Health Check")

Key fields: Check name (title), Repository, Tier, Points, Current status, What's missing, Quick fix, Full solution, Acceptance criteria.

### Issue items (Source: "Issue #N")

Key fields: Issue title, Repository, Issue number, Labels, Description, GitHub URL.

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

After cloning/pulling, detect the default branch name and the tech stack by scanning for common project files (e.g., `*.csproj`, `package.json`, `Cargo.toml`, `pyproject.toml`, `go.mod`). For tech stack detection details, see `../shared/gh-prerequisites.md#repo-context-detection`.

## Step 3 — Plan the Fix

### For health items

Health items fall into two categories:

#### Category A — API-only fixes

These don't require file changes in the repo. They use `gh` commands directly.

Checks in this category: Description, Topics, Branch protection, Security alerts.

For these, craft the specific command based on the backlog item and the repo context. For description and topics, inspect the repo to propose meaningful values (don't use placeholders).

**Branch protection — solo maintainer awareness**: Before applying branch protection, detect whether the repo is solo-maintained (single owner, no team collaborators). For solo repos, use a lightweight config that won't lock the maintainer out.

#### Category B — File creation / modification

These require creating or editing files in the local clone, then committing and pushing.

Checks in this category: README, .gitignore, CI/CD workflows, CODEOWNERS, Issue templates, PR template, SECURITY.md, CONTRIBUTING.md, LICENSE.

For detailed fix strategies per health check, read `../shared/fix-suggestions.md`.

For file creation items, generate thoughtful, repo-aware content — not just the minimal quick-fix stub. Inspect the repo to understand the project name, purpose, tech stack, build tools, existing documentation patterns, and license type.

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

## Examples

**Example 1: Apply a single health item**
User says: "apply backlog/phmatray_NewSLN/health/tier-1--readme.md"
Result: Reads the item, clones the repo, generates a real README based on the project structure, creates branch `fix/readme`, commits, pushes, opens PR, verifies acceptance criteria, updates backlog item status to PASS.

**Example 2: Apply an issue fix**
User says: "fix backlog/phmatray_NewSLN/issues/issue-42--login-page-crashes.md"
Result: Reads the issue details, fetches full issue body from GitHub, plans code changes, creates branch `fix/issue-42--login-page-crashes`, implements fix, opens PR with "Fixes #42", updates backlog status to PR CREATED.

**Example 3: Apply all tier 1 items**
User says: "apply all tier 1 items for phmatray/NewSLN"
Result: Processes each Tier 1 FAIL item in order (README, LICENSE, Description, Branch Protection), confirming each before proceeding. API-only fixes applied directly, file changes go through PR workflow.

## Troubleshooting

**Item status is already PASS**
The fix has already been applied. The skill will skip it and tell you.

**"Permission denied" when pushing branch**
You need write access to the repository. Check `gh repo view --json viewerPermission`.

**PR creation fails**
Common causes: branch already exists (skill will ask whether to update or create new), or the default branch is protected and you need to create PRs from forks.

**Complex issue — too many changes needed**
For issues requiring significant code changes, the skill will present a plan and let you guide the implementation rather than auto-fixing.

**Merge conflict on feature branch**
If the branch can't be created cleanly from the default branch, the skill reports the conflict and lets you decide how to proceed.
