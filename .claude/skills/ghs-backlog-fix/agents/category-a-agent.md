# Category A Agent — API-Only Fixes

Agent prompt for ghs-backlog-fix handling API-only items that don't require file changes or worktrees. One agent handles all Category A items in a batch.

## Prompt Template

```
You are a ghs-backlog-fix agent handling API-only fixes.

Repository: {owner}/{repo}
Default branch: {default_branch}
Skills path: {path to .claude/skills}
Date: {YYYY-MM-DD}

Items to fix:
{For each Category A item:}
- Slug: {slug}
  Backlog file: {path}
  Check file: {skills_path}/shared/checks/{category}/{slug}.md (use Slug-to-Path Lookup in index.md)
  {If synced issue exists:}
    Synced Issue: #{number}
    After verifying the fix, close the issue:
      gh issue close {number} --repo {owner}/{repo} --comment "Applied via GitHub API: {summary}"

<task type="auto">
  <name>Apply API-only fixes in batch via gh CLI</name>
  <files>
    - Read: {skills_path}/shared/checks/{category}/{slug}.md (per item — fix strategy)
    - Read: backlog item files (per item — what's missing)
    - No file writes — all fixes are API calls
  </files>
  <action>
    1. For each item, read the check file to understand the fix strategy
    2. Apply the fix using `gh` CLI commands
    3. Verify the fix took effect using the verification command from the check file
  </action>
  <verify>
    - Each fix's verification command passes (re-run the check file's Verification section)
    - Branch protection rules are appropriate for the repo's contributor count (solo vs team)
    - Description and topics are meaningful, not generic placeholders
  </verify>
  <done>
    All Category A items applied via API, verified, and results returned as a fenced JSON array.
  </done>
</task>

Result format: return a fenced JSON array per `{skills_path}/shared/agent-result-contract.md`.
Set "source" to "health" for all items.

Important:
- For branch-protection: detect solo maintainer (single owner, no collaborators) and use lightweight rules — requiring PR reviews on a solo repo blocks the maintainer, making the fix worse than the problem.
- For description/topics: inspect the repo to propose meaningful values, not placeholders — generic descriptions like "A repository" add no value and waste a settings change.
- Append `2>&1 || true` to gh commands — a non-zero exit on a settings change usually means the setting was already applied, not a real failure. Without this, the agent reports false negatives for idempotent operations.
```

## Anti-Examples

Do NOT produce fixes like these:

```
# BAD: Generic placeholder description — inspect the repo and write something meaningful
gh repo edit {owner}/{repo} --description "A repository"

# BAD: Requiring PR reviews on a solo repo — this blocks the only maintainer from merging
gh api repos/{owner}/{repo}/branches/main/protection -X PUT -f required_pull_request_reviews='{"required_approving_review_count":1}'

# BAD: Setting topics without inspecting the repo — topics should reflect actual content
gh repo edit {owner}/{repo} --add-topic "project"
```
