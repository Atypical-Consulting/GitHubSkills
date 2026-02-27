---
name: Multi-Target Framework
slug: dotnet-multi-target
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Multi-Target Framework

## Verification

```bash
# Find library .csproj files (exclude test/benchmark/sample projects)
CSPROJS=$(gh api repos/{owner}/{repo}/git/trees/HEAD --jq '.tree[].path' 2>&1 | grep -iE '\.csproj$' | grep -viE '(test|tests|benchmark|benchmarks|sample|samples|example|examples)\.')
if [ -z "$CSPROJS" ]; then
  echo 'NO_LIBRARY_PROJECTS'
else
  for csproj in $CSPROJS; do
    CONTENT=$(gh api repos/{owner}/{repo}/contents/$csproj --jq '.content' 2>&1 | base64 -d 2>/dev/null)
    # Check for plural TargetFrameworks with semicolon (multiple TFMs)
    if echo "$CONTENT" | grep -qiE '<TargetFrameworks>.*\;.*</TargetFrameworks>'; then
      echo 'MULTI_TARGET_FOUND'
      exit 0
    fi
  done
  # Also check Directory.Build.props
  PROPS=$(gh api repos/{owner}/{repo}/contents/Directory.Build.props --jq '.content' 2>&1 | base64 -d 2>/dev/null)
  if echo "$PROPS" | grep -qiE '<TargetFrameworks>.*\;.*</TargetFrameworks>'; then
    echo 'MULTI_TARGET_FOUND'
    exit 0
  fi
  echo 'SINGLE_TARGET_ONLY'
fi
```

### Pass Condition

At least one library project uses `<TargetFrameworks>` (plural) with multiple TFMs separated by semicolons.

### Status Rules

- **PASS**: Multi-targeting detected with `<TargetFrameworks>` containing multiple TFMs (`MULTI_TARGET_FOUND`)
- **FAIL**: All library projects use singular `<TargetFramework>` with a single TFM (`SINGLE_TARGET_ONLY`)
- **WARN**: No library projects found to check (`NO_LIBRARY_PROJECTS`)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

Library projects use `<TargetFramework>` (singular) targeting only a single .NET version. No multi-targeting via `<TargetFrameworks>` (plural) is configured.

### Why It Matters

Multi-targeting allows a single NuGet package to support consumers on different .NET versions (e.g., .NET 8, .NET 9, and .NET Standard 2.0). Without it, the package is limited to a single TFM, which may exclude users on older or newer runtimes. Multi-targeting also enables conditional compilation to take advantage of newer APIs where available while maintaining backward compatibility.

### Quick Fix

```bash
# In the library .csproj, change:
#   <TargetFramework>net8.0</TargetFramework>
# To:
cat << 'EOF'
  <TargetFrameworks>net8.0;net9.0;netstandard2.0</TargetFrameworks>
EOF
```

### Full Solution

1. In each library `.csproj`, replace `<TargetFramework>` (singular) with `<TargetFrameworks>` (plural):
   ```xml
   <PropertyGroup>
     <TargetFrameworks>net8.0;net9.0;netstandard2.0</TargetFrameworks>
   </PropertyGroup>
   ```
2. Choose TFMs based on your audience:
   - `netstandard2.0` -- broadest compatibility (.NET Framework 4.6.1+, .NET Core 2.0+)
   - `net8.0` -- current LTS, access to modern APIs
   - `net9.0` -- latest release, newest features
3. Use conditional compilation for APIs that differ across TFMs:
   ```csharp
   #if NET8_0_OR_GREATER
       // Use Span<T> or other modern APIs
   #else
       // Fallback for netstandard2.0
   #endif
   ```
4. Build and test against all targeted frameworks: `dotnet build` and `dotnet test` will run for each TFM.
5. Verify the `.nupkg` contains `lib/` folders for each target framework.

### Acceptance Criteria

- [ ] At least one library project uses `<TargetFrameworks>` (plural) with multiple TFMs
- [ ] The project builds successfully for all targeted frameworks
- [ ] Tests pass against all targeted frameworks
- [ ] The `.nupkg` contains libraries for each TFM

### References

- https://learn.microsoft.com/en-us/nuget/create-packages/multiple-target-frameworks-project-file
- https://learn.microsoft.com/en-us/dotnet/standard/frameworks
- https://learn.microsoft.com/en-us/dotnet/standard/library-guidance/cross-platform-targeting
