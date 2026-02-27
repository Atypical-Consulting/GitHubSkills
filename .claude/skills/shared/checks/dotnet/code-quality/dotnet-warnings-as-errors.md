---
name: Warnings as Errors
slug: dotnet-warnings-as-errors
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Warnings as Errors

## Verification

```bash
gh api repos/{owner}/{repo}/contents/Directory.Build.props --jq '.content' 2>/dev/null | base64 -d 2>/dev/null | grep -i '<TreatWarningsAsErrors>' || echo 'NOT_FOUND'
```

### Pass Condition

`<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` is present in `Directory.Build.props`.

### Status Rules

- **PASS**: `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` found
- **FAIL**: `<TreatWarningsAsErrors>` is not found or set to `false`
- **WARN**: `Directory.Build.props` does not exist (HTTP 404) -- cannot verify warnings-as-errors setting

## Backlog Content

Use the content below when generating the backlog item file for a FAIL/WARN result.

### What's Missing

Warnings are not promoted to errors. The `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` property is not set in `Directory.Build.props`.

### Why It Matters

Compiler warnings that are ignored accumulate as technical debt. Over time, developers stop paying attention to the warnings list, and real issues hide among hundreds of ignored warnings. Treating warnings as errors enforces a zero-warning policy: every warning must be explicitly addressed (fixed or suppressed with justification). This prevents gradual code quality degradation and ensures that new warnings from compiler or analyzer updates are immediately visible.

### Quick Fix

```bash
# If Directory.Build.props exists, add <TreatWarningsAsErrors>true</TreatWarningsAsErrors> inside the first <PropertyGroup>
# If Directory.Build.props does not exist, create it:
cat > Directory.Build.props << 'EOF'
<Project>
  <PropertyGroup>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
</Project>
EOF
```

### Full Solution

Enable warnings-as-errors globally via `Directory.Build.props`. If the codebase currently has many warnings, adopt a phased approach:

1. Fix or suppress all existing warnings first.
2. Enable `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>` in `Directory.Build.props`.
3. For specific warnings that cannot be immediately fixed, suppress them explicitly using `<NoWarn>` with a comment explaining why.

Alternatively, use `<WarningsAsErrors>` with specific warning codes to promote only selected warnings to errors, then expand the list over time until you can switch to `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>`.

### Acceptance Criteria

- [ ] `Directory.Build.props` contains `<TreatWarningsAsErrors>true</TreatWarningsAsErrors>`
- [ ] The project builds with zero warnings (all warnings are either fixed or explicitly suppressed)
- [ ] Any `<NoWarn>` suppressions include a comment explaining the justification

### References

- https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/compiler-options/errors-warnings#treatwarningsaserrors
- https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/compiler-options/errors-warnings#warningsaserrors-and-warningsnotaserrors
