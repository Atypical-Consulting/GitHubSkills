# State Persistence

Pattern for persisting session state using GitHub Issues. State is stored as a real GitHub Issue on the target repository, allowing decisions, blockers, and session history to survive across context resets.

## Purpose

Without state persistence, each session starts from scratch. The state issue records:

- **What was attempted** --- items fixed, failed, or retried
- **Decisions made** --- user preferences (PR strategy, merge method, skip lists)
- **Blockers encountered** --- permission issues, API limits, content filter failures
- **Session history** --- when each session ran and what it accomplished

## State Issue Location

State is stored as a GitHub Issue with the `ghs:state` label:

```bash
gh issue list --repo {owner}/{repo} --label "ghs:state" --state open \
  --json number,title,body --limit 1
```

Title convention: `[GHS State] {owner}/{repo}`

## State Issue Format

### Issue Body (Decisions and Blockers)

The body contains a machine-readable JSON block in an HTML comment plus human-readable markdown tables:

```markdown
<!-- ghs:state
{
  "decisions": [
    {"decision": "PR merge method", "value": "squash", "set_by": "user", "date": "2026-02-28"}
  ],
  "blockers": [
    {"blocker": "No admin access", "affected_items": ["branch-protection"], "status": "ACTIVE"}
  ]
}
-->

## Decisions

| Decision | Value | Set By | Date |
|----------|-------|--------|------|
| PR merge method | squash | user | 2026-02-28 |

## Blockers

| Blocker | Affected Items | Status | Notes |
|---------|---------------|--------|-------|
| No admin access | branch-protection | ACTIVE | Need org admin |
```

The JSON in the HTML comment is the machine-readable source of truth. The markdown tables are human-readable duplicates for the GitHub UI.

### Issue Comments (Session Entries)

Each session appends a comment:

```markdown
## 2026-02-28 --- ghs-backlog-fix (batch)

**Items attempted**: 5
**Results**: 3 PASS, 1 FAILED, 1 NEEDS_HUMAN

| Item | Status | PR | Notes |
|------|--------|-----|-------|
| tier-1--license | PASS | #42 | MIT license added |
| tier-1--readme | PASS | #43 | Template applied |
| tier-2--gitignore | FAILED | --- | Content filter |

**Score change**: 45% -> 68% (+23)
```

## Lifecycle

### Which Skills Create State Issues

| Skill | Creates State? | Reason |
|-------|-----------------------|--------|
| ghs-backlog-fix | Yes | After first fix attempt |
| ghs-issue-implement | Yes | After first implementation attempt |
| ghs-action-fix | Yes | After first CI fix attempt |
| ghs-repo-scan | No | Read-only |
| ghs-backlog-board | No | Read-only dashboard |
| ghs-backlog-sync | No | Syncs to project, no session state |

### Reading State

At the start of a mutation skill:

1. Find the state issue by label
2. Parse JSON from the HTML comment
3. Read the latest 5 comments for session history

From the parsed state:
- **Active blockers** --- skip blocked items
- **Decisions** --- apply user preferences
- **Last session** --- show "Last activity: {date}"

### Writing State

- **Session comment**: Appended after each skill run with results table and score change
- **Body update**: When decisions or blockers change, update the issue body JSON and tables
- **New decisions**: Recorded when users state preferences or skills discover constraints
- **New blockers**: Added when items fail due to external constraints
- **Blocker resolution**: Status updated to RESOLVED when cleared

## GSD Integration

When ghs-issue-implement uses GSD, the GSD framework maintains its own `.planning/STATE.md` inside the worktree. The state issue captures the **outcome**, not GSD's internal state.

| GSD's STATE.md | GHS State Issue |
|----------------|-----------------|
| Inside worktree | GitHub Issue on target repo |
| Planning decisions | Repo-level preferences |
| Phase progress | Session results and score changes |
| Ephemeral (cleaned with worktree) | Persistent on GitHub |
