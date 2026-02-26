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

Your job:
1. For each item, read the check file to understand the fix strategy
2. Apply the fix using `gh` CLI commands
3. Verify the fix took effect using the verification command from the check file

Important:
- For branch-protection: detect solo maintainer (single owner, no collaborators) and use lightweight rules — requiring PR reviews on a solo repo blocks the maintainer
- For description/topics: inspect the repo to propose meaningful values, not placeholders — generic descriptions like "A repository" add no value
- Append `2>&1 || true` to gh commands — a non-zero exit on a settings change usually means the setting was already applied, not a real failure

Return a fenced JSON array with one object per item (see §4 of implementation-workflow.md for format).
Set "source" to "health" for all items.
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
