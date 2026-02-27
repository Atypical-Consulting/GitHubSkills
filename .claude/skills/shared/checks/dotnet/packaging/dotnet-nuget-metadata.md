---
name: NuGet Package Metadata
slug: dotnet-nuget-metadata
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# NuGet Package Metadata

## Verification

```bash
# Find library .csproj files (exclude test/benchmark projects)
CSPROJS=$(gh api repos/{owner}/{repo}/git/trees/HEAD --jq '.tree[].path' 2>&1 | grep -iE '\.csproj$' | grep -viE '(test|tests|benchmark|benchmarks|sample|samples|example|examples)\.')
if [ -z "$CSPROJS" ]; then
  echo 'NO_LIBRARY_PROJECTS'
else
  for csproj in $CSPROJS; do
    CONTENT=$(gh api repos/{owner}/{repo}/contents/$csproj --jq '.content' 2>&1 | base64 -d 2>/dev/null)
    # Skip if explicitly not packable
    if echo "$CONTENT" | grep -qi '<IsPackable>false</IsPackable>'; then
      continue
    fi
    HAS_AUTHORS=$(echo "$CONTENT" | grep -ci '<Authors>')
    HAS_DESC=$(echo "$CONTENT" | grep -ci '<Description>')
    HAS_LICENSE=$(echo "$CONTENT" | grep -ciE '<PackageLicenseExpression>|<PackageLicenseFile>')
    HAS_ID=$(echo "$CONTENT" | grep -ciE '<PackageId>|<AssemblyName>')
    if [ "$HAS_AUTHORS" -gt 0 ] && [ "$HAS_DESC" -gt 0 ] && [ "$HAS_LICENSE" -gt 0 ]; then
      echo 'METADATA_FOUND'
      exit 0
    fi
  done
  # Also check Directory.Build.props for centralized metadata
  PROPS=$(gh api repos/{owner}/{repo}/contents/Directory.Build.props --jq '.content' 2>&1 | base64 -d 2>/dev/null)
  if [ -n "$PROPS" ]; then
    HAS_AUTHORS=$(echo "$PROPS" | grep -ci '<Authors>')
    HAS_DESC=$(echo "$PROPS" | grep -ci '<Description>')
    HAS_LICENSE=$(echo "$PROPS" | grep -ciE '<PackageLicenseExpression>|<PackageLicenseFile>')
    if [ "$HAS_AUTHORS" -gt 0 ] && [ "$HAS_DESC" -gt 0 ] && [ "$HAS_LICENSE" -gt 0 ]; then
      echo 'METADATA_FOUND'
      exit 0
    fi
  fi
  echo 'METADATA_MISSING'
fi
```

### Pass Condition

Library projects (or `Directory.Build.props`) include essential NuGet metadata: `Authors`, `Description`, and license information (`PackageLicenseExpression` or `PackageLicenseFile`).

### Status Rules

- **PASS**: All essential NuGet metadata fields found in a library project or `Directory.Build.props` (`METADATA_FOUND`)
- **FAIL**: Library projects exist but are missing essential metadata fields (`METADATA_MISSING`)
- **WARN**: No packable library projects detected -- all projects are tests, samples, or marked `IsPackable=false` (`NO_LIBRARY_PROJECTS`)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

Library projects are missing essential NuGet package metadata. One or more of the following fields are absent: `Authors`, `Description`, `PackageLicenseExpression` (or `PackageLicenseFile`).

### Why It Matters

NuGet metadata directly affects package discoverability, trust, and compliance. Packages without authors, descriptions, or license information appear incomplete on NuGet.org, are harder for consumers to evaluate, and may be rejected by organizations that require license compliance. Setting metadata centrally in `Directory.Build.props` ensures consistency across all packages in a solution.

### Quick Fix

```bash
# Add to Directory.Build.props or individual .csproj files:
cat << 'EOF'
<PropertyGroup>
  <Authors>YourName</Authors>
  <Description>A brief description of the package.</Description>
  <PackageLicenseExpression>MIT</PackageLicenseExpression>
  <PackageProjectUrl>https://github.com/{owner}/{repo}</PackageProjectUrl>
  <RepositoryUrl>https://github.com/{owner}/{repo}</RepositoryUrl>
</PropertyGroup>
EOF
```

### Full Solution

1. Add essential NuGet metadata to `Directory.Build.props` (recommended for multi-project repos):
   ```xml
   <PropertyGroup>
     <Authors>Your Name or Organization</Authors>
     <Description>Brief description of what the package does.</Description>
     <PackageLicenseExpression>MIT</PackageLicenseExpression>
     <PackageProjectUrl>https://github.com/{owner}/{repo}</PackageProjectUrl>
     <RepositoryUrl>https://github.com/{owner}/{repo}</RepositoryUrl>
     <RepositoryType>git</RepositoryType>
     <PackageTags>relevant;tags;here</PackageTags>
     <PackageReadmeFile>README.md</PackageReadmeFile>
   </PropertyGroup>
   ```
2. For per-project overrides, set `<Description>` in individual `.csproj` files.
3. Include a `README.md` in the package by adding:
   ```xml
   <ItemGroup>
     <None Include="../../README.md" Pack="true" PackagePath="\" />
   </ItemGroup>
   ```
4. Verify metadata with `dotnet pack` and inspect the generated `.nupkg` file.

### Acceptance Criteria

- [ ] `Authors` is set in `Directory.Build.props` or each packable `.csproj`
- [ ] `Description` is set for each packable project
- [ ] `PackageLicenseExpression` or `PackageLicenseFile` is configured
- [ ] `dotnet pack` produces a valid `.nupkg` with populated metadata

### References

- https://learn.microsoft.com/en-us/nuget/reference/msbuild-targets#pack-target
- https://learn.microsoft.com/en-us/nuget/create-packages/package-authoring-best-practices
- https://learn.microsoft.com/en-us/dotnet/core/project-sdk/msbuild-props#nuget-metadata-properties
