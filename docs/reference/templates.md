# Output Templates

GHS uses reusable output templates for generated content like PR descriptions, review comments, and issue bodies. Templates live in `.claude/skills/shared/templates/` and use `{placeholder}` syntax for variable substitution.

## Available Templates

| Template | Used By | Purpose |
|----------|---------|---------|
| `pr-body.md` | backlog-fix, issue-implement, action-fix | PR description body |
| `analysis-comment.md` | issue-analyze | Issue analysis comment |
| `review-comment.md` | review-pr | PR review comment |
| `state-issue-body.md` | backlog-fix, orchestrate, dev-loop | State issue body |
| `sync-issue-body.md` | backlog-sync | Synced issue body |

## PR Body Template

Used when creating pull requests from fix agents or implementation agents.

```markdown
## Summary

{summary}

## Changes

{changes_list}

## Verification

{verification_results}

## References

{references}

---
<sub>Created by GHS `{skill_name}` v{version}</sub>
```

### Placeholders

| Placeholder | Description |
|-------------|-------------|
| `{summary}` | One-line description of what the PR does |
| `{changes_list}` | Bulleted list of files changed and what was modified |
| `{verification_results}` | How the fix was verified (tests, checks, manual) |
| `{references}` | Links to related issues, project items, or docs |
| `{skill_name}` | The skill that created the PR (e.g., `ghs-backlog-fix`) |
| `{version}` | Skill version |

## Analysis Comment Template

Posted as a GitHub comment on issues after analysis.

```markdown
## Issue Analysis

| Field | Value |
|-------|-------|
| **Feasibility** | {feasibility} |
| **Complexity** | {complexity} |
| **Effort** | {effort} |
| **Risk** | {risk} |

### Affected Areas

{affected_areas_list}

### Suggested Approach

{numbered_steps}

### Risks & Dependencies

{risks_list}

{open_questions_section}
```

### Placeholders

| Placeholder | Values |
|-------------|--------|
| `{feasibility}` | Feasible, Partially Feasible, Needs Clarification |
| `{complexity}` | Low, Medium, High, Very High |
| `{effort}` | S (< 1h), M (1-4h), L (4-8h), XL (> 8h) |
| `{risk}` | Low, Medium, High |

## Review Comment Template

Posted as a GitHub review on pull requests.

```markdown
## Code Review: PR #{number}

### Summary

{summary}

### Findings

#### Critical (must fix)
{critical_findings}

#### Warnings (should fix)
{warning_findings}

#### Suggestions (nice to have)
{suggestion_findings}

#### Praise
{praise}

### Verdict: {verdict}
```

### Verdict Values

| Verdict | Condition |
|---------|-----------|
| Request Changes | Any critical findings |
| Comment Only | Warnings only, no critical |
| Approve | Suggestions and praise only, or no findings |

## State Issue Body Template

Used for persisting session state as a GitHub Issue (labeled `ghs:state`).

```markdown
# State: {owner}/{repo}

## Decisions

| Decision | Value | Set By | Date |
|----------|-------|--------|------|
| {decision_name} | {decision_value} | {skill_name} | {YYYY-MM-DD} |

## Blockers

| Blocker | Affected Items | Status | Notes |
|---------|---------------|--------|-------|
| {blocker_description} | {affected_items} | ACTIVE | {notes} |
```

The state issue body also includes a hidden JSON block for machine-readable parsing.

## Sync Issue Body Template

Used when promoting draft project items to real GitHub Issues.

```markdown
| Field | Value |
|-------|-------|
| **Tier** | {tier_number} --- {tier_label} |
| **Points** | {points} |
| **Category** | {category} |
| **Detected** | {YYYY-MM-DD} |

## What's Missing
{whats_missing}

## Why It Matters
{why_it_matters}

## How to Fix
{how_to_fix}

## Acceptance Criteria
- [ ] {criterion_1}
- [ ] {criterion_2}
```

Includes a hidden metadata comment for deduplication and field sync.
