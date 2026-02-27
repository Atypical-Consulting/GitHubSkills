---
name: Action Version Pinning
slug: action-version-pinning
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# Action Version Pinning

## Verification

```bash
# List workflow files
WORKFLOWS=$(gh api repos/{owner}/{repo}/contents/.github/workflows --jq '.[].name' 2>/dev/null || true)
if [ -z "$WORKFLOWS" ]; then
  echo "NO_WORKFLOWS"
  exit 0
fi
# Check each workflow for unpinned actions (@main, @master, @latest)
UNPINNED=""
for f in $WORKFLOWS; do
  CONTENT=$(gh api repos/{owner}/{repo}/contents/.github/workflows/$f --jq '.content' 2>/dev/null | base64 -d 2>/dev/null || true)
  HITS=$(echo "$CONTENT" | grep -nE 'uses:\s+[^#]+@(main|master|latest)\b' || true)
  if [ -n "$HITS" ]; then
    UNPINNED="$UNPINNED\n$f:\n$HITS"
  fi
done
if [ -z "$UNPINNED" ]; then
  echo "ALL_PINNED"
else
  echo "UNPINNED_FOUND"
  echo -e "$UNPINNED"
fi
```

### Pass Condition
All third-party `uses:` references in workflow files use SHA pins (e.g., `@a5ac7e51b41094c92402da3b24376905380afc29`) or version tags (e.g., `@v4`). No action uses `@main`, `@master`, or `@latest`.

### Status Rules
- **PASS**: No workflow files contain `uses: ...@main`, `@master`, or `@latest`
- **FAIL**: At least one workflow file references an action with `@main`, `@master`, or `@latest`
- **INFO**: No workflow files exist (the separate `ci-cd-workflows` check covers existence)

## Backlog Content

### What's Missing
One or more GitHub Actions workflows reference third-party actions using mutable tags (`@main`, `@master`, `@latest`) instead of pinned SHA hashes or version tags.

### Why It Matters
Unpinned actions are a supply-chain security risk. If a third-party action's `main` branch is compromised, your workflow will automatically pull the malicious code. Pinning to a SHA or a specific version tag ensures reproducible builds and protects against upstream tampering.

### Quick Fix
```bash
# Find unpinned actions
for f in $(gh api repos/{owner}/{repo}/contents/.github/workflows --jq '.[].name'); do
  gh api repos/{owner}/{repo}/contents/.github/workflows/$f --jq '.content' | base64 -d | grep -nE 'uses:\s+[^#]+@(main|master|latest)\b'
done
```

### Full Solution
1. List all workflow files: `gh api repos/{owner}/{repo}/contents/.github/workflows --jq '.[].name'`
2. For each file, decode and search for unpinned references: `@main`, `@master`, `@latest`
3. Replace with SHA pins or version tags:
   - **SHA pin** (most secure): `uses: actions/checkout@a5ac7e51b41094c92402da3b24376905380afc29 # v4`
   - **Version tag** (acceptable): `uses: actions/checkout@v4`
4. Use [StepSecurity/secure-repo](https://github.com/step-security/secure-repo) or `pinact` to automate pinning
5. Consider adding a comment with the version after the SHA for readability: `@<sha> # v4.1.7`

### Acceptance Criteria
- [ ] No workflow file contains `uses: ...@main`, `@master`, or `@latest`
- [ ] All third-party actions use SHA pins or version tags
- [ ] Workflow files remain valid YAML after changes

### References
- https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions#using-third-party-actions
- https://github.com/step-security/secure-repo
