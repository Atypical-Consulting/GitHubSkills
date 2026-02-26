---
name: Workflow Permissions
slug: workflow-permissions
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# Workflow Permissions

## Verification

```bash
# List workflow files
WORKFLOWS=$(gh api repos/{owner}/{repo}/contents/.github/workflows --jq '.[].name' 2>/dev/null || true)
if [ -z "$WORKFLOWS" ]; then
  echo "NO_WORKFLOWS"
  exit 0
fi
# Check each workflow for a top-level permissions block
MISSING=""
for f in $WORKFLOWS; do
  CONTENT=$(gh api repos/{owner}/{repo}/contents/.github/workflows/$f --jq '.content' 2>/dev/null | base64 -d 2>/dev/null || true)
  HAS_PERMS=$(echo "$CONTENT" | grep -cE '^permissions:' || true)
  if [ "$HAS_PERMS" -eq 0 ]; then
    MISSING="$MISSING $f"
  fi
done
if [ -z "$MISSING" ]; then
  echo "ALL_HAVE_PERMISSIONS"
else
  echo "MISSING_PERMISSIONS:$MISSING"
fi
```

### Pass Condition
Every workflow file declares an explicit top-level `permissions:` block. This enforces the principle of least privilege — workflows only get the token scopes they actually need.

### Status Rules
- **PASS**: All workflow files contain a top-level `permissions:` block
- **FAIL**: At least one workflow file is missing a top-level `permissions:` block
- **INFO**: No workflow files exist (the separate `ci-cd-workflows` check covers existence)

## Backlog Content

### What's Missing
One or more GitHub Actions workflows do not declare an explicit `permissions:` block, meaning they run with the default token permissions (which may be overly broad).

### Why It Matters
Without explicit permissions, workflows inherit the repository's default token permissions — often `contents: write` plus other broad scopes. If a workflow is compromised (e.g., via a malicious PR or dependency), the attacker gets all those permissions. Declaring `permissions:` explicitly limits the blast radius.

### Quick Fix
```yaml
# Add at the top level of each workflow file (after on:)
permissions:
  contents: read
```

### Full Solution
1. List all workflow files: `gh api repos/{owner}/{repo}/contents/.github/workflows --jq '.[].name'`
2. For each file without `permissions:`, determine what scopes the workflow actually needs:
   - **Read-only builds/tests**: `contents: read`
   - **Push commits**: `contents: write`
   - **Create PRs**: `contents: write`, `pull-requests: write`
   - **Publish packages**: `packages: write`
   - **Deploy to Pages**: `pages: write`, `id-token: write`
   - **Comment on issues/PRs**: `issues: write` or `pull-requests: write`
3. Add the minimal `permissions:` block at the top level of each workflow
4. Alternatively, set repository-level default to read-only: Settings → Actions → General → Workflow permissions → "Read repository contents and packages permissions"

### Acceptance Criteria
- [ ] Every workflow file has a top-level `permissions:` block
- [ ] Permissions follow the principle of least privilege (no unnecessary `write` scopes)
- [ ] Workflow files remain valid YAML after changes

### References
- https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication#modifying-the-permissions-for-the-github_token
- https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/controlling-permissions-for-github_token
