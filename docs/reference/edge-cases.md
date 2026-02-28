# Edge Cases

Common edge case handling patterns shared across all GHS skills. Centralizing these avoids drift between skills that face the same situations.

## Rate Limiting

GitHub's API allows 5,000 requests/hour for authenticated users. When rate-limited:

1. The `gh` CLI returns a 403 with "rate limit exceeded"
2. Report the error to the user with the reset time
3. Do not retry in a loop --- this wastes tokens and won't resolve until the window resets
4. Suggest the user wait and re-run the skill

## Content Filter Workaround

Some files (notably Code of Conduct) trigger API content filters when generated inline.

**Detection:** Agent fails with "Output blocked by content filtering policy"

**Handling:** Download the canonical version from an official URL instead of generating inline, then customize placeholders:

```bash
curl -sL "https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md" \
  -o CODE_OF_CONDUCT.md
sed -i '' 's/\[INSERT CONTACT METHOD\]/via GitHub issues/' CODE_OF_CONDUCT.md
```

The orchestrator detects content filter failures and retries with the download-based approach automatically.

## Permission Errors (403)

| Context | Meaning | Action |
|---------|---------|--------|
| Branch protection check | Requires admin access | Report as WARN |
| Security alerts | May require security admin role | Report as WARN |
| Push to repo | User lacks write access | Report as FAILED |
| Label creation | May require maintainer role | Skip label, continue |
| Org-level settings | Managed at org level | Note the possibility |

## gh CLI Error Handling

Append `2>&1 || true` to `gh` commands that may return non-zero for expected conditions. A 404 on a resource check means "doesn't exist yet" (useful information), not a runtime error.

## Bounded Agent Retries

| Retry Count | Action |
|-------------|--------|
| 0 (first failure) | Re-run with error context appended |
| 1 (second failure) | Re-run with error + stricter constraints |
| 2+ (third failure) | Mark as `NEEDS_HUMAN`, preserve worktree |

Two retries catches transient issues; persistent failures need human judgment.

## Special Repository Situations

| Situation | Handling |
|-----------|----------|
| **Private repos** | All `gh` checks work if the user has access. Note visibility in reports. |
| **Org-level settings** | Branch protection and security may be org-managed. Report 403s as WARN. |
| **Forks** | Inherit settings from upstream. Note in reports; some checks may not apply. |
| **Empty/new repos** | Many checks naturally fail. Add a note to focus on Tier 1 first. |
| **Archived repos** | Warn that changes cannot be pushed. Scanning still works for information. |
| **Repos with many issues** | Cap terminal display at 20 issues. Note overflow count. |
| **Long issue bodies** | Truncate to 500 chars with "..." and a link to the full issue. |
