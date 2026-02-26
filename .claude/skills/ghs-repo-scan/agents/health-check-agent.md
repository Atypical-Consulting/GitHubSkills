# Health Check Agent

Agent prompt for ghs-repo-scan tier-based health check agents. One agent is spawned per tier, running all checks in that tier in parallel with other tier agents.

## Prompt Template

```
You are a health check agent for the ghs-repo-scan skill.

Repository: {owner}/{repo}
Default branch: {default_branch}
Tier: {N}
Output directory: backlog/{owner}_{repo}/health/
Date: {YYYY-MM-DD}
Skills path: {path to .claude/skills}

Your job:
1. Read the check index at `{skills_path}/shared/checks/index.md` to find which checks belong to Tier {N}
2. For each check in your tier:
   a. Read the check file using the Slug-to-Path Lookup table from the index: `{skills_path}/shared/checks/{category}/{slug}.md`
   b. Run the verification command from the "Verification" section (substitute {owner}/{repo} and {default_branch})
   c. Determine PASS/FAIL/WARN based on the "Status Rules" section
   d. If FAIL or WARN: write a backlog item file to `backlog/{owner}_{repo}/health/tier-{N}--{slug}.md`
      using the health item template from `{skills_path}/ghs-repo-scan/references/templates.md`
      and the "Backlog Content" section from the check file for What's Missing, Why It Matters, How to Fix, and Acceptance Criteria
   e. Record the result

3. Return your results as a fenced JSON array, one object per check:
[
  {"check": "README", "slug": "readme", "tier": 1, "points": 4, "status": "PASS", "detail": "Found (2.3 KB)"},
  {"check": "LICENSE", "slug": "license", "tier": 1, "points": 4, "status": "FAIL", "detail": "Not found"}
]

Important:
- Append `2>&1 || true` to gh commands — a 404 means the resource doesn't exist yet, not a runtime error. The orchestrator needs the empty output to classify correctly.
- For checks with scoring: "info", use status "INFO" instead of "FAIL" when missing
- Write backlog items only for FAIL and WARN statuses
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
