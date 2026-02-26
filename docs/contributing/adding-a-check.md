# Adding a Health Check

GHS currently has 38 health checks. Here's how to add a new one.

## Step 1: Choose a Category

Checks are organized into 7 categories:
- `documentation` --- project docs (README, LICENSE, CHANGELOG, etc.)
- `repo-settings` --- GitHub repo configuration
- `dev-config` --- developer tooling (.gitignore, .editorconfig, etc.)
- `ci-cd` --- CI/CD pipelines
- `community` --- community health (templates, security policy)
- `security` --- security posture
- `maintenance` --- ongoing project health

## Step 2: Create the Check File

Create `.claude/skills/shared/checks/{category}/{slug}.md` with this structure:

```yaml
---
check: Human-readable name
slug: kebab-case-slug
tier: 1|2|3
category: one of the 7 categories
points: 4|2|1
scoring: Normal|INFO only
---
```

Then include these sections:
- **What to Check** --- verification logic
- **Status Rules** --- when PASS, FAIL, WARN
- **Backlog Content** --- what to write if FAIL (title, description, acceptance criteria)

## Step 3: Register in the Index

Add the check to `.claude/skills/shared/checks/index.md`:
1. Add a row to the appropriate tier table
2. Update the Scoring Summary if tier totals change
3. Add to the Slug-to-Path Lookup table

## Step 4: Categorize for Fixing

Add the slug to the appropriate category in `.claude/skills/shared/item-categories.md`:
- Category A: API-only (no file changes)
- Category B: File changes (needs worktree)
- Category CI: Special CI diagnosis

## Step 5: Test

Run `ghs-repo-scan` against a test repo and verify your check appears correctly.
