# Agent Result Contract

When GHS spawns sub-agents (via the Task tool), agents return structured results following this contract.

## Fix Agent Result

```json
{
  "source": "health",
  "slug": "contributing-md",
  "status": "PASS",
  "pr_url": "https://github.com/owner/repo/pull/42",
  "verification": "File exists and has required sections",
  "error": null
}
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| `source` | string | `"health"` or `"issue"` |
| `slug` | string | Check slug or issue identifier |
| `status` | string | `"PASS"`, `"FAILED"`, or `"NEEDS_HUMAN"` |
| `pr_url` | string or null | PR URL if created |
| `verification` | string | How the fix was verified |
| `error` | string or null | Error message if failed |

### Status Semantics

- **PASS** --- fix applied, verified, PR created
- **FAILED** --- fix attempted but failed (will be retried with bounded retry logic)
- **NEEDS_HUMAN** --- requires manual intervention (e.g., content decisions, complex refactoring)

## Health Check Agent Result

```json
{
  "check": "README",
  "slug": "readme",
  "tier": 1,
  "points": 4,
  "status": "PASS",
  "detail": "README.md exists (2847 bytes)"
}
```

## Batch Results

Agents processing multiple items return an array of result objects.

## Bounded Retry Logic

- 0 prior failures: retry with additional context
- 1 prior failure: retry with stricter constraints
- 2+ prior failures: mark as NEEDS_HUMAN
