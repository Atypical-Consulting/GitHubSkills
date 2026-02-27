---
name: Nullable Reference Types
slug: dotnet-nullable
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# Nullable Reference Types

## Verification

```bash
gh api repos/{owner}/{repo}/contents/Directory.Build.props --jq '.content' 2>/dev/null | base64 -d 2>/dev/null | grep -i '<Nullable>' || echo 'NOT_FOUND'
```

### Pass Condition

`<Nullable>enable</Nullable>` is present in `Directory.Build.props`.

### Status Rules

- **PASS**: `<Nullable>enable</Nullable>` found (case-insensitive match)
- **FAIL**: `<Nullable>` is set to `disable` or `warnings`, or no `<Nullable>` element found in the file
- **WARN**: `Directory.Build.props` does not exist (HTTP 404) -- cannot verify nullable settings

## Backlog Content

Use the content below when generating the backlog item file for a FAIL/WARN result.

### What's Missing

Nullable reference types (NRTs) are not enabled project-wide. The `<Nullable>enable</Nullable>` property is either absent, set to `disable`, or set to `warnings` in `Directory.Build.props`.

### Why It Matters

Nullable reference types make null-safety part of the type system. When enabled, the compiler distinguishes between nullable (`string?`) and non-nullable (`string`) references, catching potential `NullReferenceException` bugs at compile time instead of at runtime. This is one of the highest-impact compiler features for reducing production bugs in .NET codebases.

### Quick Fix

```bash
# If Directory.Build.props exists, add <Nullable>enable</Nullable> inside the first <PropertyGroup>
# If Directory.Build.props does not exist, create it:
cat > Directory.Build.props << 'EOF'
<Project>
  <PropertyGroup>
    <Nullable>enable</Nullable>
  </PropertyGroup>
</Project>
EOF
```

### Full Solution

Enable NRTs globally via `Directory.Build.props` so every project in the solution inherits the setting. This avoids having to add `<Nullable>enable</Nullable>` to each individual `.csproj` file.

If the codebase has many existing nullable warnings, consider a phased approach:
1. Start with `<Nullable>warnings</Nullable>` to see warnings without enforcement.
2. Fix warnings incrementally, focusing on public API surfaces first.
3. Switch to `<Nullable>enable</Nullable>` once warnings are resolved.

For large codebases, use `#nullable disable` at the top of files that are not yet migrated, then remove those pragmas over time.

### Acceptance Criteria

- [ ] `Directory.Build.props` contains `<Nullable>enable</Nullable>`
- [ ] The setting applies to all projects in the solution (not overridden by individual `.csproj` files)
- [ ] The project builds without new nullable-related errors (warnings are acceptable during migration)

### References

- https://learn.microsoft.com/en-us/dotnet/csharp/nullable-references
- https://learn.microsoft.com/en-us/dotnet/csharp/nullable-migration-strategies
