---
name: ghs:issue-triage
description: >
  Verify and apply proper labels (type, priority, status) to GitHub issues — ensures a consistent
  label taxonomy exists on the repo, then classifies issues by type and priority. Use this skill
  whenever the user wants to label issues, triage issues, classify issues, organize issue labels,
  or says things like "triage my issues", "label all issues", "triage issue #42", "classify open
  issues", "add labels to issues", "auto-triage", "triage all --auto", or "set up issue labels".
  Do NOT use for analyzing issue implementation (use ghs:issue-analyze), implementing issues
  (use ghs:issue-implement), or scanning repo health (use ghs:repo-scan).
metadata:
  author: phmatray
  version: 1.0.0
---

# Issue Triage

Verify a consistent label taxonomy exists on a GitHub repository, then classify and label open issues by type and priority.

## Prerequisites

See `../shared/gh-prerequisites.md` for authentication, repo detection, and error handling.

## Input

Three invocation modes:

- **Single issue**: `triage issue #42` — triages one specific issue
- **Batch (unlabeled)**: `triage all issues` — triages all open issues missing type/priority labels
- **Batch (all open)**: `triage all open issues` — re-triages every open issue

Two confirmation modes:

- **Interactive (default)**: AI proposes labels in a table, user confirms or adjusts before applying
- **Auto mode**: User says `triage all --auto` or `auto-triage` — AI classifies and applies directly without per-issue confirmation (for large batches where user trusts the classification)

## Label Taxonomy

The skill ensures these labels exist on the repo before triaging. Use `gh label create` to create any missing labels (skip existing ones with `2>&1 || true`).

### Type Labels (blue shades)

| Label | Color | Description |
|-------|-------|-------------|
| `type:bug` | `#d73a4a` | Something isn't working |
| `type:feature` | `#0075ca` | New feature or enhancement request |
| `type:docs` | `#0e8a16` | Documentation improvements |
| `type:chore` | `#e4e669` | Maintenance, dependencies, tooling |
| `type:test` | `#bfd4f2` | Test improvements or additions |
| `type:refactor` | `#d4c5f9` | Code refactoring without behavior change |
| `type:hotfix` | `#b60205` | Urgent production fix |

### Priority Labels (red → green)

| Label | Color | Description |
|-------|-------|-------------|
| `priority:critical` | `#b60205` | Must fix immediately — production impact |
| `priority:high` | `#d93f0b` | Should fix soon — significant impact |
| `priority:medium` | `#fbca04` | Fix when possible — moderate impact |
| `priority:low` | `#0e8a16` | Nice to have — minimal impact |

### Status Labels (purple shades)

| Label | Color | Description |
|-------|-------|-------------|
| `status:triaged` | `#5319e7` | Classified and ready for analysis/work |
| `status:analyzing` | `#7057ff` | Under analysis (ghs:issue-analyze) |
| `status:in-progress` | `#9b59b6` | Implementation in progress |
| `status:blocked` | `#c5def5` | Blocked by external dependency |

---

## Phase 1 — Ensure Label Taxonomy

Check which labels already exist on the repo:

```bash
gh label list --repo {owner}/{repo} --json name --jq '.[].name'
```

Create any missing labels from the taxonomy above:

```bash
gh label create "type:bug" --repo {owner}/{repo} \
  --color "d73a4a" --description "Something isn't working" 2>&1 || true
# ... repeat for all labels
```

Report what was created vs. already existed:

```
## Label Setup: {owner}/{repo}

Created: type:bug, type:feature, priority:critical, priority:high, ...
Already existed: type:docs, priority:medium, ...
```

## Phase 2 — Fetch Issues

### Single issue mode

```bash
gh issue view {number} --repo {owner}/{repo} --json number,title,body,labels,assignees,state
```

### Batch mode (unlabeled)

Fetch all open issues that lack both type and priority labels:

```bash
gh issue list --repo {owner}/{repo} --state open --json number,title,body,labels,assignees \
  --limit 100
```

Filter locally: keep issues where no label starts with `type:` or `priority:`.

### Batch mode (all open)

Same fetch, no filtering.

## Phase 3 — Classify Issues

For each issue, analyze the title and body to determine:

1. **Type**: Match against the type taxonomy. Use these heuristics:
   - Contains "bug", "broken", "error", "crash", "doesn't work", "regression" → `type:bug`
   - Contains "add", "feature", "request", "enhancement", "implement", "new" → `type:feature`
   - Contains "docs", "documentation", "README", "typo in docs" → `type:docs`
   - Contains "dependency", "update", "upgrade", "bump", "CI", "tooling" → `type:chore`
   - Contains "test", "coverage", "spec" → `type:test`
   - Contains "refactor", "cleanup", "reorganize" → `type:refactor`
   - If unclear, default to `type:feature`

2. **Priority**: Assess impact and urgency:
   - Security vulnerability, data loss, production down → `priority:critical`
   - Major feature broken, many users affected → `priority:high`
   - Minor bug, improvement, most feature requests → `priority:medium`
   - Nice-to-have, cosmetic, very low impact → `priority:low`

## Phase 4 — Propose & Confirm

### Interactive mode (default)

Display a table of proposed labels:

```
## Triage Proposal: {owner}/{repo}

| # | Issue | Current Labels | + Type | + Priority | Rationale |
|---|-------|----------------|--------|------------|-----------|
| 1 | #12 Login page crashes | — | type:bug | priority:high | Crash report, user-facing |
| 2 | #15 Add dark mode | enhancement | type:feature | priority:medium | Feature request, non-urgent |
| 3 | #18 Update README | — | type:docs | priority:low | Documentation only |
...

{N} issues to triage. Confirm? (y/n/edit)
```

- **y**: Apply all proposed labels
- **n**: Cancel
- **edit**: Let user adjust specific rows (e.g., "change #15 to priority:high")

### Auto mode

Skip the confirmation step — apply labels directly. Print results as they're applied.

## Phase 5 — Apply Labels

For each issue in the confirmed plan:

```bash
gh issue edit {number} --repo {owner}/{repo} \
  --add-label "type:{type},priority:{priority},status:triaged"
```

Handle issues that already have a `type:` or `priority:` label — remove the old one before adding the new one if reclassifying:

```bash
gh issue edit {number} --repo {owner}/{repo} --remove-label "type:bug"
gh issue edit {number} --repo {owner}/{repo} --add-label "type:feature"
```

## Phase 6 — Output

Display a before/after summary:

```
## Triage Results: {owner}/{repo}

| # | Issue | Before | After |
|---|-------|--------|-------|
| 1 | #12 Login page crashes | — | type:bug, priority:high, status:triaged |
| 2 | #15 Add dark mode | enhancement | type:feature, priority:medium, status:triaged |
| 3 | #18 Update README | — | type:docs, priority:low, status:triaged |

---

Summary:
  Triaged: {n}/{total}
  Types: {n_bug} bugs, {n_feature} features, {n_docs} docs, {n_chore} chores
  Priority: {n_critical} critical, {n_high} high, {n_medium} medium, {n_low} low
```

## Edge Cases

- **Issue already has type/priority labels**: In batch-unlabeled mode, skip it. In batch-all mode, show current labels and propose reclassification only if the AI disagrees.
- **Closed issues**: Skip by default. Only include if the user explicitly asks.
- **Pull requests in issue list**: `gh issue list` may include PRs — filter them out by checking the `pullRequest` field.
- **Label creation fails**: Some repos restrict label creation to maintainers. Report which labels couldn't be created and continue with existing labels.
- **Very long issue bodies**: Truncate to ~2000 chars for classification — title and first paragraphs are usually sufficient.
- **No issues to triage**: Report "All open issues are already triaged" and exit cleanly.

## Examples

**Example 1: Triage a single issue**
User says: "triage issue #42"
Result: Fetches issue #42, proposes type + priority labels, user confirms, labels are applied, status:triaged added.

**Example 2: Batch triage all unlabeled issues**
User says: "triage all issues"
Result: Fetches open issues, filters to unlabeled, proposes labels for each, user confirms table, all labels applied.

**Example 3: Auto-triage**
User says: "auto-triage all issues"
Result: Same as batch but labels are applied immediately without confirmation.

**Example 4: Set up labels only**
User says: "set up issue labels on my repo"
Result: Creates the full label taxonomy, reports what was created, done.
