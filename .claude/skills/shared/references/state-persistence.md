# State Persistence Reference

Pattern for persisting session state across context resets and conversations. Adapted from GSD's STATE.md pattern for use in backlog directories.

## Table of Contents

1. [Purpose](#purpose)
2. [File Location](#file-location)
3. [STATE.md Format](#statemd-format)
4. [Lifecycle](#lifecycle)
5. [Reading State](#reading-state)
6. [Writing State](#writing-state)

---

## Purpose

Without state persistence, each session starts from scratch — re-reading backlog items, re-discovering what was already attempted, and potentially re-trying failed approaches. STATE.md solves this by recording:

- **What was attempted** — which items were fixed, which failed, which approaches were tried
- **Decisions made** — user preferences for this repo (PR strategy, merge method, skip certain checks)
- **Blockers encountered** — permission issues, API limits, content filter failures
- **Session history** — when each session ran, what it accomplished

---

## File Location

```
backlog/{owner}_{repo}/STATE.md
```

Co-located with SUMMARY.md and health/issue items. Created on first write (not by ghs-repo-scan — only by skills that modify state like ghs-backlog-fix, ghs-issue-implement).

---

## STATE.md Format

```markdown
# State: {owner}/{repo}

## Decisions

| Decision | Value | Set By | Date |
|----------|-------|--------|------|
| PR merge method | squash | user | 2026-02-28 |
| Skip branch protection check | yes (no admin access) | ghs-backlog-fix | 2026-02-28 |
| GSD complexity threshold | high+ | user | 2026-02-28 |

## Blockers

| Blocker | Affected Items | Status | Notes |
|---------|---------------|--------|-------|
| No admin access | branch-protection, security-alerts | ACTIVE | Need org admin to grant access |
| Content filter on CoC | code-of-conduct | RESOLVED | Used download workaround |

## Recent Sessions

### 2026-02-28 — ghs-backlog-fix (batch)

**Items attempted**: 5
**Results**: 3 PASS, 1 FAILED, 1 NEEDS_HUMAN

| Item | Status | PR | Notes |
|------|--------|-----|-------|
| tier-1--license | PASS | #42 | MIT license added |
| tier-1--readme | PASS | #43 | Template applied |
| tier-2--editorconfig | PASS | #44 | — |
| tier-2--gitignore | FAILED | — | Content filter, retry with download |
| tier-1--branch-protection | NEEDS_HUMAN | — | Requires admin access |

**Score change**: 45% → 68% (+23)

### 2026-02-27 — ghs-issue-implement (#15)

**Complexity**: High (GSD path)
**GSD phases completed**: 1/1
**Result**: PASS — PR #41 created
**Verification**: 4/4 acceptance criteria passed
```

---

## Lifecycle

### Creation

STATE.md is created the first time a mutation skill runs against a repo:

| Skill | Creates STATE.md? | When |
|-------|--------------------|------|
| ghs-repo-scan | No | Read-only — doesn't modify repo state |
| ghs-backlog-board | No | Read-only dashboard |
| ghs-backlog-fix | **Yes** | After first fix attempt (regardless of success) |
| ghs-issue-implement | **Yes** | After first implementation attempt |
| ghs-backlog-sync | No | Syncs to GitHub, doesn't track local state |
| ghs-issue-triage | No | Labels only, no implementation state |
| ghs-action-fix | **Yes** | After first CI fix attempt |

### Updates

Each mutation skill appends a new session entry and updates blockers/decisions as needed. Skills should:

1. **Read STATE.md** at the start (if it exists) to learn about previous attempts and active blockers
2. **Skip known-blocked items** unless the user explicitly asks to retry
3. **Append a session entry** after completing work
4. **Update blocker status** when blockers are resolved
5. **Record new decisions** when the user expresses a preference

### Pruning

Session history can grow long. Keep the **last 10 sessions** — older entries are summarized into a single line:

```markdown
### Older Sessions (summarized)

- 2026-02-15: ghs-backlog-fix — 2 items fixed, score 30% → 45%
- 2026-02-10: ghs-repo-scan — initial scan, 12 FAIL items detected
```

---

## Reading State

### At Skill Start

When a mutation skill begins, check for STATE.md:

```
1. Read backlog/{owner}_{repo}/STATE.md (if exists)
2. Extract active blockers → skip blocked items in plan
3. Extract decisions → apply user preferences (merge method, skip list)
4. Extract last session → show "Last activity: {date} — {summary}"
```

### For Dashboard (ghs-backlog-board)

When displaying a repo on the dashboard, STATE.md enriches the view:

| Field | Source |
|-------|--------|
| Last activity | Most recent session date |
| Active blockers | Count of ACTIVE blockers |
| Decisions | Any user preferences that affect display |

### For Next-Item (ghs-backlog-next)

When recommending the next item, STATE.md helps avoid recommending:
- Items with ACTIVE blockers
- Items that failed in the last session (unless the user asks to retry)
- Items the user has explicitly decided to skip

---

## Writing State

### Session Entry Template

```markdown
### {YYYY-MM-DD} — {skill-name} ({mode})

**Items attempted**: {N}
**Results**: {pass} PASS, {fail} FAILED, {human} NEEDS_HUMAN

| Item | Status | PR | Notes |
|------|--------|-----|-------|
| {slug} | {status} | {pr_url or —} | {brief note} |

**Score change**: {before}% → {after}% ({delta})
```

### Decision Entry

Add a row to the Decisions table when:
- User explicitly states a preference ("always use squash merge for this repo")
- A skill discovers a constraint ("no admin access, skip branch protection")
- User overrides a default ("use GSD even for medium complexity issues")

### Blocker Entry

Add a row to the Blockers table when:
- An item fails due to an external constraint (permissions, rate limits)
- A dependency is missing (CI must pass before certain checks work)
- A human decision is needed (architectural choice, license selection)

Update status to RESOLVED when the blocker is cleared.

---

## Integration with GSD

When `ghs-issue-implement` uses the GSD path, the GSD framework maintains its own `.planning/STATE.md` inside the worktree. The ghs-skill's `backlog/{owner}_{repo}/STATE.md` captures the **outcome** — not the GSD internal state.

| GSD's STATE.md | ghs STATE.md |
|----------------|--------------|
| Inside worktree `.planning/` | Inside `backlog/{owner}_{repo}/` |
| GSD planning decisions | Repo-level decisions and preferences |
| Phase progress and blockers | Session results and score changes |
| Ephemeral (cleaned with worktree) | Persistent across sessions |

After GSD completes, the orchestrator extracts relevant outcomes (pass/fail, verification results, any blockers) and records them in the backlog STATE.md.
