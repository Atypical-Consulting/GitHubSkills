---
name: XML Documentation Generation
slug: dotnet-xml-docs
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# XML Documentation Generation

## Verification

```bash
gh api repos/{owner}/{repo}/contents/Directory.Build.props --jq '.content' 2>/dev/null | base64 -d 2>/dev/null | grep -i '<GenerateDocumentationFile>' || echo 'NOT_FOUND'
```

### Pass Condition

`<GenerateDocumentationFile>true</GenerateDocumentationFile>` is present in `Directory.Build.props` or in a library project `.csproj` file.

### Status Rules

- **PASS**: `<GenerateDocumentationFile>true</GenerateDocumentationFile>` found
- **FAIL**: `<GenerateDocumentationFile>` is not found or set to `false`
- **WARN**: No library projects detected (all projects are applications/test projects) -- XML docs are less critical for non-library code

## Backlog Content

Use the content below when generating the backlog item file for a FAIL/WARN result.

### What's Missing

XML documentation generation is not enabled. The `<GenerateDocumentationFile>true</GenerateDocumentationFile>` property is not set in `Directory.Build.props` or individual library `.csproj` files.

### Why It Matters

XML documentation files are the foundation for IntelliSense tooltips in IDEs, NuGet package documentation, and generated API reference sites. Without them, consumers of your library get no parameter descriptions, return value explanations, or usage examples in their editor. For public NuGet packages, this is especially critical -- users expect rich IntelliSense when working with your API.

### Quick Fix

```bash
# If Directory.Build.props exists, add <GenerateDocumentationFile>true</GenerateDocumentationFile> inside the first <PropertyGroup>
# If Directory.Build.props does not exist, create it:
cat > Directory.Build.props << 'EOF'
<Project>
  <PropertyGroup>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
  </PropertyGroup>
</Project>
EOF
```

### Full Solution

Enable XML documentation generation globally via `Directory.Build.props`. If only library projects should generate docs (not test or app projects), use a conditional:

```xml
<Project>
  <PropertyGroup>
    <GenerateDocumentationFile>true</GenerateDocumentationFile>
  </PropertyGroup>
</Project>
```

Alternatively, to limit it to specific projects, add the property only to library `.csproj` files or use MSBuild conditions based on the output type.

After enabling, address `CS1591` warnings for missing XML comments on public types and members. Consider suppressing `CS1591` initially and adding documentation incrementally, starting with the public API surface.

### Acceptance Criteria

- [ ] `<GenerateDocumentationFile>true</GenerateDocumentationFile>` is set in `Directory.Build.props` or library `.csproj` files
- [ ] The project builds successfully with documentation generation enabled
- [ ] Public API types and members have XML documentation comments (or `CS1591` is tracked for follow-up)

### References

- https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/xmldoc/
- https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/compiler-options/output#generatedocumentationfile
