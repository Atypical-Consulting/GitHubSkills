---
name: Target Framework
slug: dotnet-target-framework
tier: 3
tier_label: Nice to Have
points: 0
scoring: info
---

# Target Framework

## Verification

```bash
echo "=== BUILD PROPS ===" && (CONTENT=$(gh api repos/{owner}/{repo}/contents/Directory.Build.props --jq '.content' 2>&1 || true); if echo "$CONTENT" | grep -q "Not Found"; then echo "NO_BUILD_PROPS"; else echo "$CONTENT" | base64 --decode 2>/dev/null || true; fi)
echo "=== CSPROJ FILES ===" && (gh api repos/{owner}/{repo}/git/trees/HEAD?recursive=1 --jq '.tree[] | select(.path | endswith(".csproj")) | .path' 2>&1 | head -5 || true)
```

### Pass Condition

Reports which Target Framework Monikers (TFMs) are in use across the solution. Flags end-of-life frameworks.

### Status Rules

- **INFO**: Reports the TFMs found across `Directory.Build.props` and/or `.csproj` files
- **INFO** (with warning): Flags end-of-life TFMs: `net5.0`, `net7.0`, `netcoreapp3.0`, `netcoreapp3.1`, `netcoreapp2.x`, `netcoreapp1.x`

## Backlog Content

Use the content below when generating the backlog item for an INFO result that flags EOL frameworks.

### What's Missing

The repository targets one or more end-of-life .NET frameworks.

### Why It Matters

End-of-life (EOL) .NET versions no longer receive security patches or bug fixes. Running on EOL frameworks exposes the application to known vulnerabilities and blocks access to performance improvements and new language features. Microsoft's support policy provides Long-Term Support (LTS) for even-numbered releases (e.g., .NET 6, .NET 8) and Standard-Term Support (STS) for odd-numbered releases.

### Quick Fix

```bash
# Update TargetFramework in Directory.Build.props or individual .csproj files
# Example: Change net7.0 to net8.0 or net9.0
```

### Full Solution

1. Identify all TFMs in use by searching `Directory.Build.props` and all `.csproj` files for `<TargetFramework>` and `<TargetFrameworks>`.
2. Map each TFM to its support status:
   - **Supported LTS**: `net8.0` (until Nov 2026)
   - **Supported STS**: `net9.0` (until May 2026)
   - **EOL**: `net7.0`, `net6.0`, `net5.0`, `netcoreapp3.1`, and earlier
3. For EOL frameworks, plan a migration to the latest LTS release.
4. Use the [.NET Upgrade Assistant](https://learn.microsoft.com/en-us/dotnet/core/porting/upgrade-assistant-overview) for automated migration help.
5. Update CI pipelines to use the new SDK version.

### Acceptance Criteria

- [ ] All projects target a supported .NET version (LTS or current STS)
- [ ] No EOL framework references remain in any `.csproj` or `Directory.Build.props`

### Notes

This is an **INFO-only check**. It carries no points and no penalty. It reports which TFMs are in use and highlights any that are end-of-life. The information helps maintainers plan framework upgrades proactively.

### References

- https://learn.microsoft.com/en-us/dotnet/core/whats-new/dotnet-9/overview
- https://dotnet.microsoft.com/en-us/platform/support/policy/dotnet-core
- https://learn.microsoft.com/en-us/dotnet/core/porting/upgrade-assistant-overview
