---
name: Code Analyzers
slug: dotnet-analyzers
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Code Analyzers

## Verification

```bash
PROPS=$(gh api repos/{owner}/{repo}/contents/Directory.Build.props --jq '.content' 2>/dev/null | base64 -d 2>/dev/null)
if echo "$PROPS" | grep -qi '<EnableNETAnalyzers>true</EnableNETAnalyzers>'; then
  echo 'ANALYZERS_ENABLED'
elif echo "$PROPS" | grep -qi 'StyleCop.Analyzers\|SonarAnalyzer.CSharp\|Microsoft.CodeAnalysis.NetAnalyzers\|Roslynator.Analyzers'; then
  echo 'ANALYZER_PACKAGE_FOUND'
else
  echo 'NOT_FOUND'
fi
```

### Pass Condition

Either `<EnableNETAnalyzers>true</EnableNETAnalyzers>` is set, or an analyzer NuGet package is referenced in `Directory.Build.props` or project files.

### Status Rules

- **PASS**: `<EnableNETAnalyzers>true</EnableNETAnalyzers>` is found, or at least one known analyzer package is referenced (StyleCop.Analyzers, SonarAnalyzer.CSharp, Microsoft.CodeAnalysis.NetAnalyzers, Roslynator.Analyzers)
- **FAIL**: No analyzers are enabled and no analyzer packages are detected

## Backlog Content

Use the content below when generating the backlog item file for a FAIL/WARN result.

### What's Missing

No code analyzers are configured for the project. Neither `<EnableNETAnalyzers>true</EnableNETAnalyzers>` nor any known analyzer NuGet packages were detected.

### Why It Matters

Static code analyzers catch bugs, security vulnerabilities, performance issues, and style violations at compile time -- before code reaches review or production. They enforce consistency across the team and surface issues that are easy to miss in manual review. The .NET SDK includes built-in analyzers, and additional packages provide deeper coverage for specific concerns (style, security, API design).

### Quick Fix

```bash
# Enable the built-in .NET analyzers in Directory.Build.props:
cat > Directory.Build.props << 'EOF'
<Project>
  <PropertyGroup>
    <EnableNETAnalyzers>true</EnableNETAnalyzers>
  </PropertyGroup>
</Project>
EOF
```

### Full Solution

For .NET 5+ projects, the built-in .NET analyzers are enabled by default. For older target frameworks or explicit configuration, add `<EnableNETAnalyzers>true</EnableNETAnalyzers>` to `Directory.Build.props`.

For deeper analysis, add one or more analyzer packages:

| Package | Focus Area |
|---------|-----------|
| `Microsoft.CodeAnalysis.NetAnalyzers` | General code quality, API design, globalization, performance, security |
| `StyleCop.Analyzers` | Code style and formatting conventions |
| `SonarAnalyzer.CSharp` | Bug detection, security hotspots, code smells |
| `Roslynator.Analyzers` | 500+ refactoring and code analysis rules |

Add the chosen package(s) to `Directory.Build.props` or `Directory.Packages.props` (if using Central Package Management):

```xml
<ItemGroup>
  <PackageReference Include="Microsoft.CodeAnalysis.NetAnalyzers" Version="9.0.0">
    <PrivateAssets>all</PrivateAssets>
    <IncludeAssets>runtime; build; native; contentfiles; analyzers</IncludeAssets>
  </PackageReference>
</ItemGroup>
```

Configure rule severity in an `.editorconfig` or `.globalconfig` file to match team preferences.

### Acceptance Criteria

- [ ] `<EnableNETAnalyzers>true</EnableNETAnalyzers>` is set, or at least one analyzer package is referenced
- [ ] The project builds successfully with analyzers active
- [ ] Analyzer rules are configured (via `.editorconfig` or `.globalconfig`) to match team conventions

### References

- https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/overview
- https://learn.microsoft.com/en-us/dotnet/fundamentals/code-analysis/configuration-options
