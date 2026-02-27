---
name: SourceLink Configuration
slug: dotnet-sourcelink
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# SourceLink Configuration

## Verification

```bash
FOUND=false
# Check Directory.Build.props first
PROPS=$(gh api repos/{owner}/{repo}/contents/Directory.Build.props --jq '.content' 2>&1 | base64 -d 2>/dev/null)
if echo "$PROPS" | grep -qi 'Microsoft\.SourceLink'; then
  FOUND=true
fi
# Check .csproj files if not found in props
if [ "$FOUND" = false ]; then
  CSPROJS=$(gh api repos/{owner}/{repo}/git/trees/HEAD --jq '.tree[].path' 2>&1 | grep -iE '\.csproj$')
  for csproj in $CSPROJS; do
    CONTENT=$(gh api repos/{owner}/{repo}/contents/$csproj --jq '.content' 2>&1 | base64 -d 2>/dev/null)
    if echo "$CONTENT" | grep -qi 'Microsoft\.SourceLink'; then
      FOUND=true
      break
    fi
  done
fi
if [ "$FOUND" = true ]; then
  echo 'SOURCELINK_FOUND'
else
  echo 'NOT_FOUND'
fi
```

### Pass Condition

A SourceLink package (`Microsoft.SourceLink.GitHub`, `Microsoft.SourceLink.AzureRepos.Git`, or another SourceLink provider) is referenced in a `.csproj` or `Directory.Build.props`.

### Status Rules

- **PASS**: SourceLink package reference found (`SOURCELINK_FOUND`)
- **FAIL**: No SourceLink reference found in any project file or `Directory.Build.props` (`NOT_FOUND`)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

No SourceLink package is referenced in any project file or `Directory.Build.props`. Consumers of this NuGet package will not be able to step into the source code during debugging.

### Why It Matters

SourceLink embeds source control metadata into NuGet packages, enabling consumers to step directly into your library's source code from Visual Studio or Rider without downloading it manually. This dramatically improves the debugging experience for anyone using your package. It also enables deterministic builds and links debug symbols to the exact commit that produced the package.

### Quick Fix

```bash
# Add to Directory.Build.props:
cat << 'EOF'
<ItemGroup>
  <PackageReference Include="Microsoft.SourceLink.GitHub" Version="8.0.0" PrivateAssets="All" />
</ItemGroup>
EOF
```

### Full Solution

1. Add the appropriate SourceLink package to `Directory.Build.props` (recommended) or each `.csproj`:
   ```xml
   <ItemGroup>
     <PackageReference Include="Microsoft.SourceLink.GitHub" Version="8.0.0" PrivateAssets="All" />
   </ItemGroup>
   ```
   Use `Microsoft.SourceLink.AzureRepos.Git` for Azure DevOps, `Microsoft.SourceLink.GitLab` for GitLab, etc.
2. Enable deterministic builds and embed untracked sources:
   ```xml
   <PropertyGroup>
     <PublishRepositoryUrl>true</PublishRepositoryUrl>
     <EmbedUntrackedSources>true</EmbedUntrackedSources>
     <IncludeSymbols>true</IncludeSymbols>
     <SymbolPackageFormat>snupkg</SymbolPackageFormat>
   </PropertyGroup>
   ```
3. Verify by packing and inspecting the `.nupkg` metadata for source repository URLs.
4. Push symbol packages (`.snupkg`) to NuGet.org alongside the main package.

### Acceptance Criteria

- [ ] A SourceLink package is referenced in `Directory.Build.props` or each packable `.csproj`
- [ ] `PublishRepositoryUrl` and `EmbedUntrackedSources` are set to `true`
- [ ] Symbol packages (`.snupkg`) are generated alongside `.nupkg` files

### References

- https://learn.microsoft.com/en-us/dotnet/standard/library-guidance/sourcelink
- https://github.com/dotnet/sourcelink
- https://learn.microsoft.com/en-us/nuget/create-packages/symbol-packages-snupkg
