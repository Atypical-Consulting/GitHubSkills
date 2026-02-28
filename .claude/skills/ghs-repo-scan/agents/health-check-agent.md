# Health Check Agent

Agent prompt for ghs-repo-scan tier-based health check agents. One agent is spawned per tier, running all checks in that tier in parallel with other tier agents.

## Prompt Template

```
You are a health check agent for the ghs-repo-scan skill.

Repository: {owner}/{repo}
Default branch: {default_branch}
Tier: {N}
Date: {YYYY-MM-DD}
Skills path: {path to .claude/skills}

<task type="auto">
  <name>Run all Tier {N} health checks and return structured JSON results</name>
  <files>
    - Read: {skills_path}/shared/checks/index.md (check index)
    - Read: {skills_path}/shared/checks/{category}/{slug}.md (per check)
    - Return: structured JSON results per agent-result-contract
  </files>
  <action>
    1. Read the check index at `{skills_path}/shared/checks/index.md` to find which checks belong to Tier {N}
    2. For each check in your tier:
       a. Read the check file using the Slug-to-Path Lookup table from the index: `{skills_path}/shared/checks/{category}/{slug}.md`
       b. Run the verification command from the "Verification" section (substitute {owner}/{repo} and {default_branch})
       c. Determine PASS/FAIL/WARN based on the "Status Rules" section
       d. If FAIL or WARN: include the "Backlog Content" section data (What's Missing, Why It Matters, How to Fix, Acceptance Criteria)
          in the structured result so the orchestrator can create the corresponding project item
       e. Record the result
  </action>
  <verify>
    - Every check in Tier {N} has a result entry (no checks silently skipped)
    - Each result has all required fields: check, slug, tier, points, status, detail
    - FAIL and WARN results include backlog content fields for project item creation
    - PASS and INFO results do not include backlog content fields
  </verify>
  <done>
    All Tier {N} checks executed, and results returned as a fenced JSON array.
  </done>
</task>

Result format: return a fenced JSON array per the Health Check Agent Variant in `{skills_path}/shared/agent-result-contract.md`.
One object per check:
[
  {"check": "README", "slug": "readme", "tier": 1, "points": 4, "status": "PASS", "detail": "Found (2.3 KB)"},
  {"check": "LICENSE", "slug": "license", "tier": 1, "points": 4, "status": "FAIL", "detail": "Not found"}
]

Important:
- Append `2>&1 || true` to gh commands — a 404 means the resource doesn't exist yet, not a runtime error. Without this, the agent crashes on missing resources instead of correctly classifying them as FAIL.
- For checks with scoring: "info", use status "INFO" instead of "FAIL" when missing — INFO items are advisory and don't penalize the health score.
- Write backlog items only for FAIL and WARN statuses — PASS and INFO don't need remediation.
```

## Anti-Examples

Do NOT return results like these:

```json
// BAD: Missing detail field — the orchestrator needs it for the terminal report
{"check": "README", "slug": "readme", "tier": 1, "points": 4, "status": "PASS"}

// BAD: Using "ERROR" instead of "WARN" for permission issues — 403 means WARN, not ERROR
{"check": "Branch Protection", "slug": "branch-protection", "tier": 1, "points": 4, "status": "ERROR", "detail": "403 Forbidden"}

// BAD: Omitting the slug — the orchestrator uses it to link to backlog files
{"check": "README", "tier": 1, "points": 4, "status": "FAIL", "detail": "Not found"}
```
