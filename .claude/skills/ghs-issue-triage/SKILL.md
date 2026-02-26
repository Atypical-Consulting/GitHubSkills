---
name: ghs-issue-triage
description: >
  Verify and apply proper labels (type, priority, status) to GitHub issues — ensures a consistent
  label taxonomy exists on the repo, then classifies issues by type and priority. Use this skill
  whenever the user wants to label issues, triage issues, classify issues, organize issue labels,
  or says things like "triage my issues", "label all issues", "triage issue #42", "classify open
  issues", "add labels to issues", "auto-triage", "triage all --auto", or "set up issue labels".
  Do NOT use for analyzing issue implementation (use ghs-issue-analyze), implementing issues
  (use ghs-issue-implement), or scanning repo health (use ghs-repo-scan).
allowed-tools: "Bash(gh:*) Read"
compatibility: "Requires gh CLI (authenticated), network access"
license: MIT
metadata:
  author: phmatray
  version: 4.0.0
routes-to:
  - ghs-issue-analyze
  - ghs-issue-implement
routes-from:
  - ghs-repo-scan
---

# Issue Triage

Verify a consistent label taxonomy exists on a GitHub repository, then classify and label open issues by type and priority.

<context>
Purpose: Ensure consistent issue labeling by establishing a label taxonomy and classifying issues by type and priority.

Roles:
1. **Triage Agent** (you) — creates missing labels, fetches issues, classifies each by type and priority, applies labels after confirmation

This skill does not spawn sub-agents — classification benefits from seeing all issues together for consistent calibration.

Shared references (see `../shared/references/`):

| Reference | Purpose |
|-----------|---------|
| `../shared/references/gh-cli-patterns.md` | Authentication, repo detection, error handling, idempotent commands |
| `../shared/references/output-conventions.md` | Status indicators, table patterns, summary blocks |
</context>

<anti-patterns>

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Remove existing valid labels | Only add missing `type:*`, `priority:*`, and `status:triaged` labels; leave custom labels (e.g., `enhancement`, `help wanted`) in place | Removing user-created labels destroys existing workflows |
| Triage closed issues unless asked | Default scope is open issues only; include closed issues only when user explicitly requests | Closed issues are resolved — triaging them adds noise |
| Override manually-set priority labels | In batch-unlabeled mode, skip issues that already have a `priority:*` label; in batch-all mode, propose reclassification but flag it clearly | Respects manual curation by maintainers |
| Create labels that already exist | Always append `2>&1 \|\| true` to `gh label create` commands (see `gh-cli-patterns.md` § Idempotent Commands) | Avoids errors on duplicate creation |
| Treat PRs as issues | Filter out PRs by checking the `pullRequest` field in the JSON response from `gh issue list` | PRs have different workflows and labeling needs |
| Fail hard on a single API error | Continue with remaining operations (see `gh-cli-patterns.md` § Error Handling Conventions) | One failure should not abort the entire triage batch |

</anti-patterns>

<objective>
Classify and label open issues with consistent type, priority, and status labels.

Outputs:
- Label taxonomy created/verified on the repo
- Issues labeled with `type:*`, `priority:*`, and `status:triaged`
- Before/after summary table in terminal

Next routing:
- Suggest `ghs-issue-analyze` for complex issues — "For complex issues, run `/ghs-issue-analyze #{number}` before implementing"
- Suggest `ghs-issue-implement` to start working — "To implement triaged issues: `/ghs-issue-implement all triaged issues`"
</objective>

<process>

## Input

Three invocation modes:

- **Single issue**: `triage issue #42` — triages one specific issue
- **Batch (unlabeled)**: `triage all issues` — triages all open issues missing type/priority labels
- **Batch (all open)**: `triage all open issues` — re-triages every open issue

Two confirmation modes:

- **Interactive (default)**: AI proposes labels in a table, user confirms or adjusts before applying
- **Auto mode**: User says `triage all --auto` or `auto-triage` — classifies and applies directly without per-issue confirmation (for large batches where user trusts the classification)

## Label Taxonomy

The skill ensures these labels exist on the repo before triaging. Use `gh label create` to create any missing labels. Append `2>&1 || true` to skip labels that already exist (see `gh-cli-patterns.md` § Idempotent Commands).

### Type Labels

| Label | Color | Description |
|-------|-------|-------------|
| `type:bug` | `#d73a4a` | Something isn't working |
| `type:feature` | `#0075ca` | New feature or enhancement request |
| `type:docs` | `#0e8a16` | Documentation improvements |
| `type:chore` | `#e4e669` | Maintenance, dependencies, tooling |
| `type:test` | `#bfd4f2` | Test improvements or additions |
| `type:refactor` | `#d4c5f9` | Code refactoring without behavior change |
| `type:hotfix` | `#b60205` | Urgent production fix |

### Priority Labels

| Label | Color | Description | Criteria |
|-------|-------|-------------|----------|
| `priority:critical` | `#b60205` | Must fix immediately | Security vulnerability, data loss, production down |
| `priority:high` | `#d93f0b` | Should fix soon | Major feature broken, many users affected, blocks releases |
| `priority:medium` | `#fbca04` | Fix when possible | Minor bug, improvement, most feature requests |
| `priority:low` | `#0e8a16` | Nice to have | Cosmetic, very low impact, edge-case only |

### Status Labels

| Label | Color | Description |
|-------|-------|-------------|
| `status:triaged` | `#5319e7` | Classified and ready for analysis/work |
| `status:analyzing` | `#7057ff` | Under analysis (ghs-issue-analyze) |
| `status:in-progress` | `#9b59b6` | Implementation in progress |
| `status:blocked` | `#c5def5` | Blocked by external dependency |

## Phase 1 — Ensure Label Taxonomy

Check which labels already exist on the repo:

```bash
gh label list --repo {owner}/{repo} --json name --jq '.[].name'
```

Create any missing labels from the taxonomy above:

```bash
gh label create "type:bug" --repo {owner}/{repo} \
  --color "d73a4a" --description "Something isn't working" 2>&1 || true
```

Report what was created vs. already existed.

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

For each issue, analyze the title and body to determine type and priority using the decision tables below. Tables make classification consistent across runs — different phrasing of the same problem should map to the same label.

### Type Classification Rules

Each rule includes a trigger pattern, the resulting label, and a concrete example.

| Rule | Trigger (keywords in title/body) | Label | Example |
|------|----------------------------------|-------|---------|
| R1 | bug, broken, error, crash, doesn't work, regression, fails, exception | `type:bug` | "Login page crashes on submit" → `type:bug` |
| R2 | add, feature, request, enhancement, implement, new, support, enable | `type:feature` | "Add dark mode toggle" → `type:feature` |
| R3 | docs, documentation, README, typo in docs, wiki, guide | `type:docs` | "Update API docs for v2 endpoints" → `type:docs` |
| R4 | dependency, update, upgrade, bump, CI, tooling, renovate, dependabot | `type:chore` | "Bump lodash from 4.17.20 to 4.17.21" → `type:chore` |
| R5 | test, coverage, spec, e2e, unit test | `type:test` | "Add unit tests for auth module" → `type:test` |
| R6 | refactor, cleanup, reorganize, simplify, restructure | `type:refactor` | "Refactor database connection pooling" → `type:refactor` |
| R7 | *(none match)* | `type:feature` | Default — most issues request new behavior |

**Precedence**: When multiple rules match, prefer the more specific rule. If both "bug" and "feature" keywords appear, read the full context to decide. A request to "add error handling" is `type:feature`, not `type:bug`.

### Priority Classification Rules

| Rule | Signal | Label | Example |
|------|--------|-------|---------|
| P1 | Security vulnerability, data loss, production outage, auth bypass | `priority:critical` | "SQL injection in search endpoint" → `priority:critical` |
| P2 | Major feature broken, many users affected, blocks release, data corruption risk | `priority:high` | "Payment processing fails for 50% of users" → `priority:high` |
| P3 | Minor bug, improvement, most feature requests, usability issues | `priority:medium` | "Add pagination to results page" → `priority:medium` |
| P4 | Nice-to-have, cosmetic, very low impact, edge-case only | `priority:low` | "Align footer text on mobile landscape" → `priority:low` |

### Good and Bad Classification Examples

These examples clarify boundary cases where the wrong label is commonly assigned.

| Issue Title | GOOD Label | BAD Label | Why |
|-------------|-----------|-----------|-----|
| "Add error handling for API timeouts" | `type:feature` | `type:bug` | No existing behavior is broken — this adds a new capability |
| "Button color doesn't match design spec" | `type:bug` | `type:feature` | The implementation doesn't match the intended design — it's broken |
| "Upgrade React from 17 to 18" | `type:chore` | `type:feature` | Framework upgrade is maintenance, not a user-facing feature |
| "Refactor auth to support OAuth" | `type:feature` | `type:refactor` | Adds new OAuth capability — refactor is the method, feature is the goal |
| "Remove deprecated API endpoints" | `type:chore` | `type:refactor` | Removing dead code is maintenance, not restructuring |
| "Typo in error message" | `type:bug` | `type:docs` | Error messages are code output, not documentation |
| "Typo in README installation steps" | `type:docs` | `type:bug` | README is documentation, not runtime code |
| "App crashes when uploading 10GB file" | `priority:medium` | `priority:critical` | Edge case with workaround — not production-down |
| "Login fails for all users" | `priority:critical` | `priority:high` | Total auth failure = production outage |

### Confidence Levels

When proposing labels, indicate confidence for each:

| Confidence | Meaning | Action |
|------------|---------|--------|
| High | Strong signal from title + body + code context | Apply automatically in `--auto` mode |
| Medium | Reasonable inference but ambiguous signals | Apply in `--auto`, flag for review |
| Low | Insufficient signal, multiple valid options | Skip in `--auto`, propose to user |

## Phase 4 — Propose & Confirm

### Interactive mode (default)

Display a table of proposed labels:

```
## Triage Proposal: {owner}/{repo}

| # | Issue | Current Labels | + Type | + Priority | Rationale |
|---|-------|----------------|--------|------------|-----------|
| 1 | #12 Login page crashes | — | type:bug | priority:high | Crash report, user-facing |
| 2 | #15 Add dark mode | enhancement | type:feature | priority:medium | Feature request, non-urgent |
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

Display a before/after summary (see `output-conventions.md` § Issue Table, § Summary Block Patterns):

```
## Triage Results: {owner}/{repo}

| # | Issue | Before | After |
|---|-------|--------|-------|
| 1 | #12 Login page crashes | — | type:bug, priority:high, status:triaged |
| 2 | #15 Add dark mode | enhancement | type:feature, priority:medium, status:triaged |
...

---

Summary:
  Triaged: {n}/{total}
  Types: {n_bug} bugs, {n_feature} features, {n_docs} docs, {n_chore} chores
  Priority: {n_critical} critical, {n_high} high, {n_medium} medium, {n_low} low
```

</process>

## Edge Cases

- **Issue already has type/priority labels**: In batch-unlabeled mode, skip it. In batch-all mode, show current labels and propose reclassification only if the AI disagrees.
- **Closed issues**: Skip by default. Only include if the user explicitly asks.
- **Pull requests in issue list**: `gh issue list` may include PRs — filter them out by checking the `pullRequest` field.
- **Label creation fails**: Some repos restrict label creation to maintainers. Report which labels couldn't be created and continue with existing labels.
- **Very long issue bodies**: Truncate to ~2000 chars for classification (see `output-conventions.md` § Issue Display Limits) — title and first paragraphs are usually sufficient for determining type and priority.
- **No issues to triage**: Report "All open issues are already triaged" and exit cleanly.

## Examples

**Example 1: Triage a single issue**
User says: "triage issue #42"
Result: Fetches issue #42, proposes type + priority labels, user confirms, labels applied, status:triaged added.

**Example 2: Batch triage all unlabeled issues**
User says: "triage all issues"
Result: Fetches open issues, filters to unlabeled, proposes labels for each, user confirms, all labels applied.

**Example 3: Auto-triage**
User says: "auto-triage all issues"
Result: Same as batch but labels applied immediately without confirmation.

**Example 4: Set up labels only**
User says: "set up issue labels on my repo"
Result: Creates the full label taxonomy, reports what was created, done.
