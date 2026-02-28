# State Persistence Reference

Pattern for persisting session state using GitHub Issues. State is stored as a real GitHub Issue on the target repository, with decisions and blockers in the issue body and session entries as issue comments.

## Table of Contents

1. [Purpose](#purpose)
2. [State Issue Location](#state-issue-location)
3. [State Issue Format](#state-issue-format)
4. [Lifecycle](#lifecycle)
5. [Reading State](#reading-state)
6. [Writing State](#writing-state)

---

## Purpose

Without state persistence, each session starts from scratch — re-discovering what was already attempted and potentially re-trying failed approaches. The state issue solves this by recording:

- **What was attempted** — which items were fixed, which failed, which approaches were tried
- **Decisions made** — user preferences for this repo (PR strategy, merge method, skip certain checks)
- **Blockers encountered** — permission issues, API limits, content filter failures
- **Session history** — when each session ran, what it accomplished (as issue comments)

---

## State Issue Location

State is stored as a GitHub Issue on the target repository:

```bash
# Find the state issue
gh issue list --repo {owner}/{repo} --label "ghs:state" --state open \
  --json number,title,body --limit 1

# The state issue title follows this convention:
# [GHS State] {owner}/{repo}
```

The `ghs:state` label is created idempotently during the first write:

```bash
gh label create "ghs:state" --color "1d76db" --description "GHS session state tracking" --repo {owner}/{repo} 2>&1 || true
```

---

## State Issue Format

### Issue Body (Decisions & Blockers)

The issue body contains structured data in an HTML comment block (machine-readable) plus a human-readable section:

```markdown
<!-- ghs:state
{
  "decisions": [
    {"decision": "PR merge method", "value": "squash", "set_by": "user", "date": "2026-02-28"},
    {"decision": "Skip branch protection check", "value": "yes (no admin access)", "set_by": "ghs-backlog-fix", "date": "2026-02-28"}
  ],
  "blockers": [
    {"blocker": "No admin access", "affected_items": ["branch-protection", "security-alerts"], "status": "ACTIVE", "notes": "Need org admin to grant access"},
    {"blocker": "Content filter on CoC", "affected_items": ["code-of-conduct"], "status": "RESOLVED", "notes": "Used download workaround"}
  ]
}
-->

# State: {owner}/{repo}

## Decisions

| Decision | Value | Set By | Date |
|----------|-------|--------|------|
| PR merge method | squash | user | 2026-02-28 |
| Skip branch protection check | yes (no admin access) | ghs-backlog-fix | 2026-02-28 |

## Blockers

| Blocker | Affected Items | Status | Notes |
|---------|---------------|--------|-------|
| No admin access | branch-protection, security-alerts | ACTIVE | Need org admin to grant access |
| Content filter on CoC | code-of-conduct | RESOLVED | Used download workaround |
```

The JSON in the HTML comment is the machine-readable source of truth. The markdown tables below are human-readable duplicates for visibility in the GitHub UI.

### Issue Comments (Session Entries)

Each session entry is appended as an issue comment:

```markdown
## {YYYY-MM-DD} — {skill-name} ({mode})

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
```

---

## Lifecycle

### Creation

The state issue is created the first time a mutation skill runs against a repo:

| Skill | Creates State Issue? | When |
|-------|-----------------------|------|
| ghs-repo-scan | No | Read-only — doesn't modify repo state |
| ghs-backlog-board | No | Read-only dashboard |
| ghs-backlog-fix | **Yes** | After first fix attempt (regardless of success) |
| ghs-issue-implement | **Yes** | After first implementation attempt |
| ghs-backlog-sync | No | Syncs to project, doesn't track session state |
| ghs-issue-triage | No | Labels only, no implementation state |
| ghs-action-fix | **Yes** | After first CI fix attempt |

### Creation Pattern

```bash
# Check if state issue exists
STATE_ISSUE=$(gh issue list --repo {owner}/{repo} --label "ghs:state" --state open \
  --json number --limit 1 --jq '.[0].number // empty')

if [ -z "$STATE_ISSUE" ]; then
  # Create label (idempotent)
  gh label create "ghs:state" --color "1d76db" --description "GHS session state tracking" \
    --repo {owner}/{repo} 2>&1 || true

  # Create state issue
  STATE_ISSUE=$(gh issue create --repo {owner}/{repo} \
    --title "[GHS State] {owner}/{repo}" \
    --label "ghs:state" \
    --body "{initial_body}" \
    --json number --jq '.number')
fi
```

### Updates

Each mutation skill appends a session comment and may update the issue body (for decisions/blockers). Skills should:

1. **Read the state issue** at the start (if it exists) to learn about previous attempts and active blockers
2. **Skip known-blocked items** unless the user explicitly asks to retry
3. **Append a session comment** after completing work
4. **Update issue body** when decisions or blockers change
5. **Record new decisions** when the user expresses a preference

### Pruning

Issue comments persist indefinitely — GitHub handles pagination. No manual pruning is needed unlike the old file-based approach.

---

## Reading State

### At Skill Start

When a mutation skill begins:

```bash
# 1. Find state issue
STATE_ISSUE=$(gh issue list --repo {owner}/{repo} --label "ghs:state" --state open \
  --json number,body --limit 1)

# 2. If found, parse the JSON from the HTML comment in the body
#    Extract decisions and blockers

# 3. For recent session history, read the latest comments:
gh issue view {state_number} --repo {owner}/{repo} \
  --json comments --jq '.comments | sort_by(.createdAt) | reverse | .[0:5]'
```

From the parsed state:
- **Active blockers** → skip blocked items in plan
- **Decisions** → apply user preferences (merge method, skip list)
- **Last session** → show "Last activity: {date} — {summary}"

### For Dashboard (ghs-backlog-board)

When displaying a repo on the dashboard, the state issue enriches the view:

| Field | Source |
|-------|--------|
| Last activity | Most recent comment date |
| Active blockers | Count of ACTIVE blockers from issue body JSON |
| Decisions | Any user preferences that affect display |

### For Next-Item (ghs-backlog-next)

When recommending the next item, the state issue helps avoid recommending:
- Items with ACTIVE blockers
- Items that failed in the last session (unless the user asks to retry)
- Items the user has explicitly decided to skip

---

## Writing State

### Session Comment Template

```bash
gh issue comment {state_number} --repo {owner}/{repo} --body "$(cat <<'EOF'
## {YYYY-MM-DD} — {skill-name} ({mode})

**Items attempted**: {N}
**Results**: {pass} PASS, {fail} FAILED, {human} NEEDS_HUMAN

| Item | Status | PR | Notes |
|------|--------|-----|-------|
| {slug} | {status} | {pr_url or —} | {brief note} |

**Score change**: {before}% → {after}% ({delta})
EOF
)"
```

### Updating Decisions/Blockers

When a decision or blocker changes, update the issue body:

```bash
# Read current body, update the JSON block, rebuild the body
gh issue edit {state_number} --repo {owner}/{repo} --body "{updated_body}"
```

Add a row to Decisions when:
- User explicitly states a preference ("always use squash merge for this repo")
- A skill discovers a constraint ("no admin access, skip branch protection")
- User overrides a default ("use GSD even for medium complexity issues")

Add a row to Blockers when:
- An item fails due to an external constraint (permissions, rate limits)
- A dependency is missing (CI must pass before certain checks work)
- A human decision is needed (architectural choice, license selection)

Update blocker status to RESOLVED when the blocker is cleared.

---

## Integration with GSD

When `ghs-issue-implement` uses the GSD path, the GSD framework maintains its own `.planning/STATE.md` inside the worktree. The ghs-skill's state issue captures the **outcome** — not the GSD internal state.

| GSD's STATE.md | ghs State Issue |
|----------------|-----------------|
| Inside worktree `.planning/` | GitHub Issue on the target repo |
| GSD planning decisions | Repo-level decisions and preferences |
| Phase progress and blockers | Session results and score changes |
| Ephemeral (cleaned with worktree) | Persistent on GitHub |

After GSD completes, the orchestrator extracts relevant outcomes (pass/fail, verification results, any blockers) and records them in the state issue comment.
