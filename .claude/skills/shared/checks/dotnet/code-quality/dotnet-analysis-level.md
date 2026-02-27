---
name: Analysis Level
slug: dotnet-analysis-level
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Analysis Level

## Verification

```bash
gh api repos/{owner}/{repo}/contents/Directory.Build.props --jq '.content' 2>/dev/null | base64 -d 2>/dev/null | grep -i '<AnalysisLevel>' || echo 'NOT_FOUND'
```

### Pass Condition

`<AnalysisLevel>` is explicitly set in `Directory.Build.props` (e.g., `latest`, `latest-recommended`, `9`, `9-recommended`).

### Status Rules

- **PASS**: `<AnalysisLevel>` is explicitly set to any value (e.g., `latest`, `latest-recommended`, `9`, `9-recommended`, `8-all`)
- **FAIL**: `<AnalysisLevel>` is not set (the project relies on the implicit SDK default, which changes between SDK versions)
- **WARN**: `Directory.Build.props` does not exist (HTTP 404) -- cannot verify analysis level setting

## Backlog Content

Use the content below when generating the backlog item file for a FAIL/WARN result.

### What's Missing

The `<AnalysisLevel>` property is not explicitly set in `Directory.Build.props`. The project relies on the implicit SDK default, which varies by target framework version.

### Why It Matters

The `AnalysisLevel` property controls which code analysis rules are active and at what severity. Without an explicit setting, the active rule set depends on the .NET SDK version and target framework, meaning builds may produce different warnings on different machines or after SDK upgrades. Setting it explicitly ensures consistent analysis behavior across environments and makes SDK upgrades intentional rather than surprising.

### Quick Fix

```bash
# Add <AnalysisLevel>latest-recommended</AnalysisLevel> to Directory.Build.props:
cat > Directory.Build.props << 'EOF'
<Project>
  <PropertyGroup>
    <AnalysisLevel>latest-recommended</AnalysisLevel>
  </PropertyGroup>
</Project>
EOF
```

### Full Solution

Set `<AnalysisLevel>` in `Directory.Build.props` to control the analysis rule set for all projects in the solution. Common values:

| Value | Behavior |
|-------|----------|
| `latest` | Uses the latest rules available in the installed SDK (default severity) |
| `latest-recommended` | Uses the latest rules with Microsoft-recommended severities |
| `latest-all` | Uses all latest rules enabled as warnings |
| `9` | Uses rules from .NET 9 (pinned, does not change with SDK updates) |
| `9-recommended` | Pinned to .NET 9 rules with recommended severities |

For most projects, `latest-recommended` is a good starting point: it enables the latest rules at sensible severities and will automatically pick up new rules when the SDK is updated.

For projects that need build reproducibility, pin to a specific version (e.g., `9-recommended`) so the rule set does not change until explicitly updated.

### Acceptance Criteria

- [ ] `Directory.Build.props` contains an explicit `<AnalysisLevel>` setting
- [ ] The chosen level matches the team's intent (latest vs pinned, default vs recommended vs all)
- [ ] The project builds successfully with the configured analysis level

### References

- https://learn.microsoft.com/en-us/dotnet/core/project-sdk/msbuild-props#analysislevel
- https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview#enabled-rules
