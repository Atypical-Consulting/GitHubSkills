---
name: Central Package Management
slug: dotnet-central-packages
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# Central Package Management

## Verification

```bash
gh api repos/{owner}/{repo}/contents/Directory.Packages.props --jq '.size' 2>&1 || true
```

### Pass Condition

`Directory.Packages.props` exists in the repository root.

### Status Rules

- **PASS**: API returns file size (HTTP 200)
- **FAIL**: API returns 404 (file not found)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

No `Directory.Packages.props` file exists in the repository root. Central Package Management (CPM) is not enabled.

### Why It Matters

Without CPM, each project independently declares package versions in its `.csproj` file. In multi-project solutions this leads to version drift — different projects depending on different versions of the same package. Diagnosing version conflicts, performing upgrades, and auditing dependencies all become harder. CPM provides a single source of truth for all NuGet package versions across the entire solution.

### Quick Fix

```bash
cat > Directory.Packages.props << 'EOF'
<Project>
  <PropertyGroup>
    <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
  </PropertyGroup>
  <ItemGroup>
    <!-- Add PackageVersion items here -->
    <!-- <PackageVersion Include="Newtonsoft.Json" Version="13.0.3" /> -->
  </ItemGroup>
</Project>
EOF
```

### Full Solution

1. Create `Directory.Packages.props` in the repository root with `<ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>`.
2. For each `<PackageReference>` across all `.csproj` files:
   - Add a `<PackageVersion Include="PackageName" Version="X.Y.Z" />` entry to `Directory.Packages.props`.
   - Remove the `Version` attribute from the `<PackageReference>` in the `.csproj` (keep only `Include`).
3. Build and run tests to verify all package versions resolve correctly.
4. For packages that need a project-specific override, use `VersionOverride` on the `<PackageReference>`.

### Acceptance Criteria

- [ ] `Directory.Packages.props` exists in the repository root
- [ ] File contains `<ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>`
- [ ] At least one `<PackageVersion>` entry is defined
- [ ] Solution builds successfully with centralized versions

### References

- https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management
- https://devblogs.microsoft.com/nuget/introducing-central-package-management/
