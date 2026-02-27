---
name: Directory.Build.props
slug: dotnet-build-props
tier: 1
tier_label: Required
points: 4
scoring: normal
---

# Directory.Build.props

## Verification

```bash
gh api repos/{owner}/{repo}/contents/Directory.Build.props --jq '.size' 2>&1 || true
```

### Pass Condition

`Directory.Build.props` exists in the repository root.

### Status Rules

- **PASS**: API returns file size (HTTP 200)
- **FAIL**: API returns 404 (file not found)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

No `Directory.Build.props` file exists in the repository root.

### Why It Matters

Without a `Directory.Build.props`, each `.csproj` file must independently declare common properties like `Nullable`, `ImplicitUsings`, `LangVersion`, `TreatWarningsAsErrors`, and package metadata. This leads to drift between projects, forgotten settings in new projects, and tedious multi-file edits when a property needs to change. A single `Directory.Build.props` at the repo root is automatically imported by every project in the tree, giving you one place to enforce standards.

### Quick Fix

```bash
cat > Directory.Build.props << 'EOF'
<Project>
  <PropertyGroup>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <LangVersion>latest</LangVersion>
  </PropertyGroup>
</Project>
EOF
```

### Full Solution

1. Create `Directory.Build.props` in the repository root.
2. Move common `<PropertyGroup>` settings from individual `.csproj` files into it:
   - `Nullable`, `ImplicitUsings`, `LangVersion`
   - `TreatWarningsAsErrors`, `WarningLevel`
   - Package metadata: `Authors`, `Company`, `Copyright`, `PackageLicenseExpression`
   - `TargetFramework` (if all projects share the same TFM)
3. Remove the duplicated properties from each `.csproj`.
4. Build and run tests to verify nothing broke.

### Acceptance Criteria

- [ ] `Directory.Build.props` exists in the repository root
- [ ] File contains at least one `<PropertyGroup>` with shared settings
- [ ] Solution builds successfully with the centralized properties

### References

- https://learn.microsoft.com/en-us/visualstudio/msbuild/customize-by-directory
- https://learn.microsoft.com/en-us/dotnet/core/project-sdk/overview
