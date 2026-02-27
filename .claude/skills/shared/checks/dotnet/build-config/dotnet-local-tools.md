---
name: Local Tool Manifest
slug: dotnet-local-tools
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Local Tool Manifest

## Verification

```bash
gh api repos/{owner}/{repo}/contents/.config/dotnet-tools.json --jq '.size' 2>&1 || true
```

### Pass Condition

`.config/dotnet-tools.json` exists in the repository.

### Status Rules

- **PASS**: API returns file size (HTTP 200)
- **FAIL**: API returns 404 (file not found)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

No `.config/dotnet-tools.json` local tool manifest exists in the repository.

### Why It Matters

Without a local tool manifest, .NET CLI tools (formatters, linters, code generators, etc.) must be installed globally on each developer's machine and CI agent. This leads to version mismatches, missing tools, and onboarding friction. A local tool manifest pins exact tool versions and lets any developer restore them with a single `dotnet tool restore` command.

### Quick Fix

```bash
dotnet new tool-manifest
# Then install commonly needed tools, e.g.:
# dotnet tool install dotnet-format
# dotnet tool install dotnet-reportgenerator-globaltool
```

### Full Solution

1. Create the tool manifest:
   ```bash
   dotnet new tool-manifest
   ```
2. Install project-specific tools:
   ```bash
   dotnet tool install dotnet-format
   dotnet tool install dotnet-outdated-tool
   dotnet tool install dotnet-reportgenerator-globaltool
   ```
3. The manifest at `.config/dotnet-tools.json` now tracks each tool and its version.
4. Add `dotnet tool restore` to your CI pipeline and onboarding docs.
5. Developers run `dotnet tool restore` after cloning to get all tools at the correct versions.

### Acceptance Criteria

- [ ] `.config/dotnet-tools.json` exists in the repository
- [ ] Manifest contains at least one tool entry
- [ ] `dotnet tool restore` succeeds without errors

### References

- https://learn.microsoft.com/en-us/dotnet/core/tools/local-tools-how-to-use
- https://learn.microsoft.com/en-us/dotnet/core/tools/dotnet-tool-install
