---
name: Merge Strategy
slug: merge-strategy
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# Merge Strategy

## Verification

```bash
gh api repos/{owner}/{repo} --jq '{allow_merge_commit: .allow_merge_commit, allow_squash_merge: .allow_squash_merge, allow_rebase_merge: .allow_rebase_merge, squash_merge_commit_title: .squash_merge_commit_title}' 2>&1 || true
```

### Pass Condition
The repository has a deliberate merge strategy — not all three merge methods enabled at once with default settings. At least one method should be disabled, OR if squash merge is enabled, it should use PR title as the default commit title.

### Status Rules
- **PASS**: Fewer than 3 merge methods are enabled, OR `squash_merge_commit_title` is `PR_TITLE`
- **FAIL**: All 3 methods enabled with default squash settings (no deliberate choice made)

## Backlog Content

### What's Missing
All three merge strategies (merge commit, squash, rebase) are enabled with default settings. This means contributors can use any method, leading to an inconsistent commit history.

### Why It Matters
When all merge methods are available with no preference set, the commit history becomes a mix of merge commits, squashed commits, and rebased commits. This makes `git log` harder to read, `git bisect` less reliable, and automated changelog generation inconsistent. Choosing a primary strategy signals intentional project governance.

### Quick Fix
```bash
# Recommended: Enable only squash merge with PR title
gh api repos/{owner}/{repo} -X PATCH \
  -f allow_merge_commit=false \
  -f allow_squash_merge=true \
  -f allow_rebase_merge=false \
  -f squash_merge_commit_title=PR_TITLE
```

### Full Solution
Choose one of these common strategies:

**Squash-only (recommended for most projects):**
```bash
gh api repos/{owner}/{repo} -X PATCH \
  -f allow_merge_commit=false \
  -f allow_squash_merge=true \
  -f allow_rebase_merge=false \
  -f squash_merge_commit_title=PR_TITLE
```
Best for: Clean linear history, one commit per PR, automated changelogs.

**Rebase-only:**
```bash
gh api repos/{owner}/{repo} -X PATCH \
  -f allow_merge_commit=false \
  -f allow_squash_merge=false \
  -f allow_rebase_merge=true
```
Best for: Preserving individual commits while keeping linear history.

**Merge-only (for projects that value full branch history):**
```bash
gh api repos/{owner}/{repo} -X PATCH \
  -f allow_merge_commit=true \
  -f allow_squash_merge=false \
  -f allow_rebase_merge=false
```
Best for: Large teams, audit trails, complex multi-commit PRs.

### Acceptance Criteria
- [ ] Fewer than 3 merge methods are enabled, OR squash merge uses PR title as default

### Notes
This is an **API-only fix** — no file changes or PR needed. The "squash with PR title" exception exists because teams that enable all methods but set squash_merge_commit_title=PR_TITLE have made a deliberate configuration choice.

### References
- https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/configuring-pull-request-merges/about-merge-methods-on-github
