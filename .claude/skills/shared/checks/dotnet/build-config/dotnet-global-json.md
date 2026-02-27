---
name: global.json
slug: dotnet-global-json
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# global.json

## Verification

```bash
gh api repos/{owner}/{repo}/contents/global.json --jq '.size' 2>&1 || true
```

### Pass Condition

`global.json` exists in the repository root.

### Status Rules

- **PASS**: API returns file size (HTTP 200)
- **FAIL**: API returns 404 (file not found)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

No `global.json` file exists in the repository root.

### Why It Matters

Without `global.json`, the .NET CLI uses whichever SDK version happens to be installed on the machine. Different developers and CI agents may have different SDK versions, leading to inconsistent builds, unexpected breaking changes, and "works on my machine" issues. Pinning the SDK version in `global.json` ensures reproducible builds across all environments.

### Quick Fix

```bash
dotnet new globaljson --sdk-version 9.0.200 --roll-forward latestFeature
```

### Full Solution

1. Determine the SDK version the project currently targets (check CI logs or local `dotnet --version`).
2. Create `global.json` with the appropriate version and roll-forward policy:
   ```json
   {
     "sdk": {
       "version": "9.0.200",
       "rollForward": "latestFeature"
     }
   }
   ```
3. The `rollForward` policy controls flexibility:
   - `latestFeature` — allows newer feature bands (e.g., 9.0.300) but not major/minor bumps
   - `latestPatch` — strictest, only allows patch updates
   - `latestMajor` — most permissive, allows any newer version
4. Commit and verify CI builds with the pinned version.

### Acceptance Criteria

- [ ] `global.json` exists in the repository root
- [ ] File specifies an `sdk.version` field
- [ ] File specifies a `rollForward` policy

### References

- https://learn.microsoft.com/en-us/dotnet/core/tools/global-json
- https://learn.microsoft.com/en-us/dotnet/core/tools/global-json#rollforward
