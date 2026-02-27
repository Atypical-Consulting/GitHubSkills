---
name: InternalsVisibleTo Configuration
slug: dotnet-internals-visible
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# InternalsVisibleTo Configuration

## Verification

```bash
FOUND=false
# Check .csproj files for InternalsVisibleTo
CSPROJS=$(gh api repos/{owner}/{repo}/git/trees/HEAD --jq '.tree[].path' 2>&1 | grep -iE '\.csproj$')
for csproj in $CSPROJS; do
  CONTENT=$(gh api repos/{owner}/{repo}/contents/$csproj --jq '.content' 2>&1 | base64 -d 2>/dev/null)
  if echo "$CONTENT" | grep -qi 'InternalsVisibleTo'; then
    FOUND=true
    break
  fi
done
# Check AssemblyInfo.cs files
if [ "$FOUND" = false ]; then
  ASMINFOS=$(gh api repos/{owner}/{repo}/git/trees/HEAD --jq '.tree[].path' 2>&1 | grep -iE 'AssemblyInfo\.cs$')
  for asm in $ASMINFOS; do
    CONTENT=$(gh api repos/{owner}/{repo}/contents/$asm --jq '.content' 2>&1 | base64 -d 2>/dev/null)
    if echo "$CONTENT" | grep -qi 'InternalsVisibleTo'; then
      FOUND=true
      break
    fi
  done
fi
if [ "$FOUND" = true ]; then
  echo 'INTERNALS_VISIBLE_FOUND'
else
  echo 'NOT_FOUND'
fi
```

### Pass Condition

`InternalsVisibleTo` attribute is configured in at least one `.csproj` file or `AssemblyInfo.cs`, pointing to a test assembly.

### Status Rules

- **PASS**: `InternalsVisibleTo` found in a `.csproj` or `AssemblyInfo.cs` file (`INTERNALS_VISIBLE_FOUND`)
- **FAIL**: No `InternalsVisibleTo` declaration found anywhere (`NOT_FOUND`)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

No `InternalsVisibleTo` attribute is configured in any project file or `AssemblyInfo.cs`. Test projects cannot access `internal` types and methods from the main project.

### Why It Matters

Without `InternalsVisibleTo`, test projects can only test `public` members. This forces developers to either make types `public` just for testability (leaking implementation details into the public API) or skip testing internal logic entirely. Configuring `InternalsVisibleTo` allows test assemblies to access `internal` members while keeping the public API surface clean and intentional.

### Quick Fix

```bash
# Add to the source project's .csproj (modern SDK-style approach):
# Inside the <Project> element, add:
cat << 'EOF'
  <ItemGroup>
    <InternalsVisibleTo Include="MyProject.Tests" />
  </ItemGroup>
EOF
```

### Full Solution

1. In the source project's `.csproj` file, add an `InternalsVisibleTo` item targeting the test assembly:
   ```xml
   <ItemGroup>
     <InternalsVisibleTo Include="MyProject.Tests" />
   </ItemGroup>
   ```
2. Alternatively, for older project styles or when you need more control, add the attribute in an `AssemblyInfo.cs` file:
   ```csharp
   [assembly: InternalsVisibleTo("MyProject.Tests")]
   ```
3. If you use strong-named assemblies, include the public key in the attribute value.
4. Repeat for each source project that has a corresponding test project.
5. Verify by writing a test that accesses an `internal` class or method.

### Acceptance Criteria

- [ ] At least one source project declares `InternalsVisibleTo` pointing to its test assembly
- [ ] The declaration is in a `.csproj` `<ItemGroup>` or an `AssemblyInfo.cs` file
- [ ] Test projects can access `internal` types from the source project

### References

- https://learn.microsoft.com/en-us/dotnet/api/system.runtime.compilerservices.internalsvisibletoattribute
- https://learn.microsoft.com/en-us/dotnet/core/project-sdk/msbuild-props#internalsvisibleto
