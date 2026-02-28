<!-- Template: state-issue-body | Used by: ghs-backlog-fix, ghs-orchestrate, ghs-dev-loop -->

<!-- ghs:state
{
  "decisions": [
    {"decision": "{decision_name}", "value": "{decision_value}", "set_by": "{skill_name}", "date": "{YYYY-MM-DD}"}
  ],
  "blockers": [
    {"blocker": "{blocker_description}", "affected_items": ["{slug1}", "{slug2}"], "status": "ACTIVE|RESOLVED", "notes": "{notes}"}
  ]
}
-->

# State: {owner}/{repo}

## Decisions

| Decision | Value | Set By | Date |
|----------|-------|--------|------|
| {decision_name} | {decision_value} | {skill_name} | {YYYY-MM-DD} |

## Blockers

| Blocker | Affected Items | Status | Notes |
|---------|---------------|--------|-------|
| {blocker_description} | {affected_items} | ACTIVE | {notes} |
