---
name: Package Reference Count
slug: dotnet-package-count
tier: 3
tier_label: Nice to Have
points: 0
scoring: info
---

# Package Reference Count

## Verification

```bash
CSPROJS=$(gh api repos/{owner}/{repo}/git/trees/HEAD --jq '.tree[].path' 2>&1 | grep -iE '\.csproj$')
if [ -z "$CSPROJS" ]; then
  echo 'NO_CSPROJ_FILES'
else
  TOTAL=0
  for csproj in $CSPROJS; do
    CONTENT=$(gh api repos/{owner}/{repo}/contents/$csproj --jq '.content' 2>&1 | base64 -d 2>/dev/null)
    COUNT=$(echo "$CONTENT" | grep -c '<PackageReference' 2>/dev/null || echo 0)
    TOTAL=$((TOTAL + COUNT))
  done
  # Also check Directory.Packages.props for central package management
  CPM=$(gh api repos/{owner}/{repo}/contents/Directory.Packages.props --jq '.content' 2>&1 | base64 -d 2>/dev/null)
  if [ -n "$CPM" ]; then
    CPM_COUNT=$(echo "$CPM" | grep -c '<PackageVersion' 2>/dev/null || echo 0)
    echo "PACKAGE_COUNT:${CPM_COUNT} (central package management)"
  else
    echo "PACKAGE_COUNT:${TOTAL}"
  fi
fi
```

### Pass Condition

This is an informational check. It reports the total number of `PackageReference` entries across all `.csproj` files (or `PackageVersion` entries in `Directory.Packages.props` if central package management is used).

### Status Rules

- **INFO**: Reports the total package count. Flags if count exceeds 50 direct dependencies as potential dependency bloat.

## Backlog Content

Use the content below when generating the backlog item file for an INFO result.

### What's Missing

This check does not indicate a failure. It reports the total number of NuGet package dependencies across the solution for awareness.

### Why It Matters

A high number of direct package dependencies (over 50) can indicate dependency bloat, which increases build times, enlarges deployment artifacts, expands the attack surface for supply-chain vulnerabilities, and makes version conflict resolution harder. Monitoring package count helps teams stay aware of their dependency footprint and identify opportunities to consolidate or remove unused packages.

### Quick Fix

```bash
# List all PackageReference entries across the solution:
find . -name '*.csproj' -exec grep -h '<PackageReference' {} \; | sort | uniq -c | sort -rn
# Remove unused packages:
dotnet remove package <PackageName>
```

### Full Solution

1. Audit the current dependency list:
   ```bash
   dotnet list package
   ```
2. Identify unused packages using tools like `dotnet-unused`:
   ```bash
   dotnet tool install -g dotnet-unused
   dotnet unused
   ```
3. Remove packages that are no longer referenced in code.
4. Consider consolidating packages that serve overlapping purposes.
5. If using many packages, adopt Central Package Management (`Directory.Packages.props`) to manage versions in one place:
   ```xml
   <Project>
     <PropertyGroup>
       <ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>
     </PropertyGroup>
     <ItemGroup>
       <PackageVersion Include="Newtonsoft.Json" Version="13.0.3" />
     </ItemGroup>
   </Project>
   ```
6. Run `dotnet build` and `dotnet test` to verify no regressions after cleanup.

### Acceptance Criteria

- [ ] Total package count is documented and reviewed
- [ ] Unused packages are identified and removed
- [ ] If count exceeds 50, a dependency audit has been performed

### References

- https://learn.microsoft.com/en-us/nuget/consume-packages/central-package-management
- https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-list-package
- https://learn.microsoft.com/en-us/nuget/concepts/dependency-resolution
