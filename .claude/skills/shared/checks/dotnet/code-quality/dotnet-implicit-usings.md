---
name: Implicit Usings
slug: dotnet-implicit-usings
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# Implicit Usings

## Verification

```bash
gh api repos/{owner}/{repo}/contents/Directory.Build.props --jq '.content' 2>/dev/null | base64 -d 2>/dev/null | grep -i '<ImplicitUsings>' || echo 'NOT_FOUND'
```

### Pass Condition

`<ImplicitUsings>enable</ImplicitUsings>` is present in `Directory.Build.props`.

### Status Rules

- **PASS**: `<ImplicitUsings>enable</ImplicitUsings>` found (case-insensitive match)
- **FAIL**: `<ImplicitUsings>` is set to `disable` or no `<ImplicitUsings>` element found in the file
- **WARN**: `Directory.Build.props` does not exist (HTTP 404) -- cannot verify implicit usings settings

## Backlog Content

Use the content below when generating the backlog item file for a FAIL/WARN result.

### What's Missing

Implicit usings are not enabled project-wide. The `<ImplicitUsings>enable</ImplicitUsings>` property is either absent or set to `disable` in `Directory.Build.props`.

### Why It Matters

Implicit usings automatically import the most common namespaces for your project type (e.g., `System`, `System.Collections.Generic`, `System.Linq`, `System.Threading.Tasks`). This eliminates repetitive `using` statements at the top of every file, reducing boilerplate and keeping source files focused on actual logic. It is the default for new .NET 6+ projects and is considered a modern .NET best practice.

### Quick Fix

```bash
# If Directory.Build.props exists, add <ImplicitUsings>enable</ImplicitUsings> inside the first <PropertyGroup>
# If Directory.Build.props does not exist, create it:
cat > Directory.Build.props << 'EOF'
<Project>
  <PropertyGroup>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
</Project>
EOF
```

### Full Solution

Enable implicit usings globally via `Directory.Build.props` so every project in the solution inherits the setting. After enabling, remove the now-redundant `using` directives from source files.

Steps:
1. Add `<ImplicitUsings>enable</ImplicitUsings>` to `Directory.Build.props`.
2. Build the solution to confirm no compile errors.
3. Use `dotnet format` or an IDE refactoring to remove unnecessary `using` statements.
4. For project-specific additional implicit usings, add a `GlobalUsings.cs` file or use `<Using Include="..." />` items in the `.csproj`.

### Acceptance Criteria

- [ ] `Directory.Build.props` contains `<ImplicitUsings>enable</ImplicitUsings>`
- [ ] The setting applies to all projects in the solution
- [ ] The project builds successfully with implicit usings enabled

### References

- https://learn.microsoft.com/en-us/dotnet/core/project-sdk/overview#implicit-using-directives
- https://learn.microsoft.com/en-us/dotnet/core/project-sdk/msbuild-props#implicitusings
