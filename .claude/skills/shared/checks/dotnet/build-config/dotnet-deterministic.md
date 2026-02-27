---
name: Deterministic Builds
slug: dotnet-deterministic
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Deterministic Builds

## Verification

```bash
CONTENT=$(gh api repos/{owner}/{repo}/contents/Directory.Build.props --jq '.content' 2>&1 || true)
if echo "$CONTENT" | grep -q "Not Found"; then
  echo "NO_BUILD_PROPS"
else
  echo "$CONTENT" | base64 --decode 2>/dev/null || true
fi
```

### Pass Condition

`<Deterministic>` is not explicitly set to `false` in `Directory.Build.props`. SDK-style projects default to `true`, so the absence of the property is a pass.

### Status Rules

- **PASS**: `Directory.Build.props` exists and does not contain `<Deterministic>false</Deterministic>`
- **PASS**: `Directory.Build.props` exists and explicitly sets `<Deterministic>true</Deterministic>`
- **FAIL**: `Directory.Build.props` contains `<Deterministic>false</Deterministic>`
- **WARN**: `Directory.Build.props` does not exist (cannot verify; depends on dotnet-build-props check)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

Deterministic builds are explicitly disabled via `<Deterministic>false</Deterministic>` in `Directory.Build.props`.

### Why It Matters

Deterministic builds ensure that the same source code always produces byte-for-byte identical binaries. This is critical for supply chain security (verifiable builds), cache efficiency in CI, and debugging with SourceLink. SDK-style projects enable deterministic builds by default, so explicitly disabling it removes a valuable safety property without clear benefit.

### Quick Fix

```bash
# Remove or change <Deterministic>false</Deterministic> to true in Directory.Build.props
# In most cases, simply removing the line is sufficient since the default is true
```

### Full Solution

1. Open `Directory.Build.props` and locate `<Deterministic>false</Deterministic>`.
2. Either remove the line entirely (the SDK default is `true`) or change it to `<Deterministic>true</Deterministic>`.
3. If deterministic builds were disabled to work around a specific issue, investigate the root cause:
   - Embedded timestamps: Use `<EmbedUntrackedSources>true</EmbedUntrackedSources>` with SourceLink instead.
   - Path-dependent outputs: Enable `<PathMap>` to normalize source paths.
4. Build the solution and verify that all projects compile successfully.

### Acceptance Criteria

- [ ] `Directory.Build.props` does not contain `<Deterministic>false</Deterministic>`
- [ ] Solution builds successfully with deterministic builds enabled

### References

- https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/compiler-options/code-generation#deterministic
- https://github.com/dotnet/sourcelink
- https://reproducible-builds.org/
