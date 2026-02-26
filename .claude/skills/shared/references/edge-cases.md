# Common Edge Cases

Shared edge case handling patterns referenced by multiple skills. Centralizing these avoids drift between skills that face the same situations.

## Rate Limiting

GitHub's API has rate limits (5,000 requests/hour for authenticated users). When hit:

1. The `gh` CLI will return a 403 with a `rate limit exceeded` message
2. Report the error to the user with the reset time if available
3. Do not retry in a loop — this wastes tokens and won't resolve until the window resets
4. Suggest the user wait and re-run the skill

## Content Filter Workaround

Some files (notably Code of Conduct) contain text that triggers API content filters when generated inline. This is a platform limitation, not a content problem.

**Detection:** Agent fails with "Output blocked by content filtering policy"

**Handling:**
1. Download the canonical version from an official URL instead of generating inline
2. Customize placeholders after download

```bash
# Example: Code of Conduct
curl -sL "https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md" \
  -o CODE_OF_CONDUCT.md
sed -i '' 's/\[INSERT CONTACT METHOD\]/via GitHub issues/' CODE_OF_CONDUCT.md
```

The orchestrator should detect content filter failures and retry the item with this download-based approach rather than marking it as FAILED.

## Permission Errors (403)

| Context | Meaning | Action |
|---------|---------|--------|
| Branch protection check | Requires admin access | Report as WARN — not a real failure |
| Security alerts | May require security admin role | Report as WARN |
| Push to repo | User lacks write access | Report as FAILED with clear message |
| Label creation | May require maintainer role | Skip label, continue with existing ones |
| Org-level settings | Setting managed at org level, not repo | Note the possibility in the report |

## gh CLI Error Handling

Append `2>&1 || true` to `gh` commands that may return non-zero for expected conditions — a 404 on a resource check means "doesn't exist yet" (which is useful information), not a runtime error. Without this, the agent treats every non-zero exit as a crash.

## Bounded Agent Retries

When an agent fails verification:

| Retry Count | Action |
|-------------|--------|
| 0 (first failure) | Re-run with error context appended to prompt |
| 1 (second failure) | Re-run with error context + stricter constraints |
| 2+ (third failure) | Mark as `NEEDS_HUMAN`, report to user, preserve worktree |

This prevents infinite retry loops that waste tokens without making progress. Two retries is enough to catch transient issues; persistent failures need human judgment.
