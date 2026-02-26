# Agent Result Contract

Universal response format for all GHS agents. Every agent must return a fenced JSON object (or array) conforming to this contract — the orchestrator parses structured JSON, never freeform text.

## Why a Standard Contract

Consistent result formats let the orchestrator handle success, failure, and human-escalation cases with a single code path. Without a contract, each agent returns a slightly different shape and the orchestrator needs custom parsing logic per agent type — a maintenance burden that grows with every new agent.

## Result Object

```json
{
  "source": "health|issue",
  "slug": "{identifier}",
  "status": "PASS|FAILED|NEEDS_HUMAN",
  "pr_url": "https://github.com/{owner}/{repo}/pull/N or null",
  "verification": ["List of verification checks performed"],
  "error": "Error message or null"
}
```

## Field Reference

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source` | string | Yes | Origin of the item: `"health"` for backlog health checks, `"issue"` for GitHub issues |
| `slug` | string | Yes | Short identifier (e.g., `license`, `42-login-bug`) — used to link results back to backlog files |
| `status` | string | Yes | `PASS` = fix applied, `FAILED` = fix failed, `NEEDS_HUMAN` = requires manual intervention |
| `pr_url` | string\|null | Yes | URL of created PR, or `null` for API-only fixes and failures |
| `verification` | string[] | Yes | Array of verification steps that passed — gives reviewers confidence the fix works |
| `error` | string\|null | Yes | Error description if status is `FAILED` or `NEEDS_HUMAN`, otherwise `null` |
| `github_issue` | number\|null | No | GitHub issue number if synced via `ghs-backlog-sync`, for cross-reference |

## Status Semantics

| Status | Meaning | Worktree | Backlog Update |
|--------|---------|----------|----------------|
| `PASS` | Fix applied and verified | Cleaned up | Status → PASS |
| `FAILED` | Fix attempted but failed | Cleaned up | Status stays FAIL |
| `NEEDS_HUMAN` | Requires human judgment | Left in place | Status stays FAIL |

## Array vs Object

- **Single-item agents** (Category B, CI, Implementation): return a single JSON object
- **Batch agents** (Category A handling multiple API-only items): return a JSON **array** of objects

## Health Check Agent Variant

Health check agents (used by `ghs-repo-scan`) return a slightly different shape for scan results:

```json
{
  "check": "README",
  "slug": "readme",
  "tier": 1,
  "points": 4,
  "status": "PASS|FAIL|WARN|INFO",
  "detail": "Human-readable detail (e.g., 'Found (2.3 KB)')"
}
```

Key differences:
- `status` uses `PASS/FAIL/WARN/INFO` (scan vocabulary) instead of `PASS/FAILED/NEEDS_HUMAN` (fix vocabulary)
- Includes `tier`, `points`, `detail` for the terminal report
- Always returned as an array (one object per check)
