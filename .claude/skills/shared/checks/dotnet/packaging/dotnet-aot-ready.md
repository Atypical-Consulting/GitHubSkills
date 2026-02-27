---
name: AOT Compatibility
slug: dotnet-aot-ready
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# AOT Compatibility

## Verification

```bash
FOUND=false
# Check Directory.Build.props first
PROPS=$(gh api repos/{owner}/{repo}/contents/Directory.Build.props --jq '.content' 2>&1 | base64 -d 2>/dev/null)
if echo "$PROPS" | grep -qiE '<IsAotCompatible>true|<PublishAot>true'; then
  FOUND=true
fi
# Check .csproj files if not found in props
if [ "$FOUND" = false ]; then
  CSPROJS=$(gh api repos/{owner}/{repo}/git/trees/HEAD --jq '.tree[].path' 2>&1 | grep -iE '\.csproj$')
  for csproj in $CSPROJS; do
    CONTENT=$(gh api repos/{owner}/{repo}/contents/$csproj --jq '.content' 2>&1 | base64 -d 2>/dev/null)
    if echo "$CONTENT" | grep -qiE '<IsAotCompatible>true|<PublishAot>true'; then
      FOUND=true
      break
    fi
  done
fi
if [ "$FOUND" = true ]; then
  echo 'AOT_DECLARED'
else
  echo 'NOT_FOUND'
fi
```

### Pass Condition

At least one project declares AOT compatibility via `<IsAotCompatible>true</IsAotCompatible>` or `<PublishAot>true</PublishAot>` in a `.csproj` or `Directory.Build.props`.

### Status Rules

- **PASS**: AOT compatibility declared in at least one project (`AOT_DECLARED`)
- **FAIL**: No AOT compatibility declaration found (`NOT_FOUND`)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

No project declares `<IsAotCompatible>true</IsAotCompatible>` or `<PublishAot>true</PublishAot>`. The library has not been marked as AOT-compatible.

### Why It Matters

Native AOT compilation is a key feature of .NET 8+ that produces self-contained, ahead-of-time compiled binaries with faster startup times and smaller memory footprints. Libraries that declare `IsAotCompatible` enable the AOT analyzer during build, which catches reflection-based patterns and other constructs that break under AOT. Even if AOT is not the primary deployment target today, declaring compatibility is a forward-looking practice that ensures the library works for consumers who do use AOT.

### Quick Fix

```bash
# Add to the library .csproj or Directory.Build.props:
cat << 'EOF'
<PropertyGroup>
  <IsAotCompatible>true</IsAotCompatible>
</PropertyGroup>
EOF
```

### Full Solution

1. For library projects, add `<IsAotCompatible>true</IsAotCompatible>` to the `.csproj` or `Directory.Build.props`:
   ```xml
   <PropertyGroup>
     <IsAotCompatible>true</IsAotCompatible>
   </PropertyGroup>
   ```
2. For application projects targeting AOT deployment, use `<PublishAot>true</PublishAot>` instead.
3. Build the project and address any AOT analyzer warnings (e.g., `IL2026`, `IL3050`):
   - Replace reflection-based patterns with source generators where possible.
   - Use `[DynamicallyAccessedMembers]` and `[RequiresUnreferencedCode]` attributes to annotate unavoidable reflection.
4. Run `dotnet publish -r <rid>` to verify the AOT build succeeds without trimming warnings.
5. Ensure the project targets .NET 8 or later, as AOT support is most mature there.

### Acceptance Criteria

- [ ] `<IsAotCompatible>true</IsAotCompatible>` is set in library projects (or `<PublishAot>true</PublishAot>` for apps)
- [ ] The project builds without AOT analyzer warnings
- [ ] The project targets .NET 8 or later

### References

- https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/
- https://learn.microsoft.com/en-us/dotnet/core/deploying/native-aot/preparing-libraries
- https://learn.microsoft.com/en-us/dotnet/core/deploying/trimming/prepare-libraries-for-trimming
