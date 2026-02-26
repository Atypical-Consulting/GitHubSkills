# ghs-issue-triage

Verifies and applies proper labels (type, priority, status) to GitHub issues using a consistent 15-label taxonomy.

::: info Skill Info
**Version:** 2.0.0
**Trigger phrases:** "triage my issues", "label the issues", "triage phmatray/my-project", "classify open issues", "auto-triage", "set up issue labels"
:::

## What It Does

`ghs-issue-triage` ensures a consistent labeling system exists on your repository and then classifies open issues by type and priority.

### Label Taxonomy (15 labels)

**Type labels** (7): `type:bug`, `type:feature`, `type:docs`, `type:chore`, `type:test`, `type:refactor`, `type:hotfix`

**Priority labels** (4): `priority:critical`, `priority:high`, `priority:medium`, `priority:low`

**Status labels** (4): `status:triaged`, `status:analyzing`, `status:in-progress`, `status:blocked`

### Two Modes

- **Interactive (default)** — proposes labels in a table, you confirm or adjust before applying
- **Auto mode** — classifies and applies labels directly without per-issue confirmation (say "auto-triage" or "triage all --auto")

### Process

1. Check which labels exist on the repo and create any missing ones
2. Fetch open issues (all, or only unlabeled, depending on the mode)
3. Classify each issue by analyzing the title and body against keyword decision tables
4. Present the proposal table for confirmation (interactive mode)
5. Apply the labels
6. Display a before/after summary

## Example

```
## Triage Proposal: phmatray/my-project

| # | Issue                    | Current Labels | + Type       | + Priority     | Rationale              |
|---|--------------------------|----------------|--------------|----------------|------------------------|
| 1 | #12 Login page crashes   | --             | type:bug     | priority:high  | Crash report, user-facing |
| 2 | #15 Add dark mode        | enhancement    | type:feature | priority:medium| Feature request, non-urgent |
| 3 | #18 Fix typo in README   | --             | type:docs    | priority:low   | Documentation, cosmetic |

3 issues to triage. Confirm? (y/n/edit)
```

After applying:

```
## Triage Results: phmatray/my-project

| # | Issue                    | Before      | After                                       |
|---|--------------------------|-------------|---------------------------------------------|
| 1 | #12 Login page crashes   | --          | type:bug, priority:high, status:triaged     |
| 2 | #15 Add dark mode        | enhancement | type:feature, priority:medium, status:triaged|
| 3 | #18 Fix typo in README   | --          | type:docs, priority:low, status:triaged     |

---

Summary:
  Triaged: 3/3
  Types: 1 bug, 1 feature, 1 docs
  Priority: 0 critical, 1 high, 1 medium, 1 low
```

## Routes To

After triaging, GHS suggests:

- **[ghs-issue-analyze](/skills/ghs-issue-analyze)** — for complex issues that need investigation before implementation
- **[ghs-issue-implement](/skills/ghs-issue-implement)** — to start implementing triaged issues

## Technical Details

| Property | Value |
|----------|-------|
| Allowed tools | `Bash(gh:*)`, `Read` |
| Spawns sub-agents | No — classification benefits from seeing all issues together for consistency |
| Phases | 6 (Ensure Taxonomy, Fetch Issues, Classify, Propose, Apply Labels, Output) |
| Requires | `gh` CLI (authenticated), network access |
| Re-run safe | Yes — skips already-labeled issues in unlabeled mode |
