---
name: Version Pinning
slug: version-pinning
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Version Pinning

## Verification

```bash
echo "=== TECH STACK ===" && (gh api repos/{owner}/{repo}/languages --jq 'to_entries | sort_by(-.value) | .[0].key' 2>&1 || true)
echo "=== GLOBAL JSON ===" && (gh api repos/{owner}/{repo}/contents/global.json 2>&1 || true)
echo "=== NVMRC ===" && (gh api repos/{owner}/{repo}/contents/.nvmrc 2>&1 || true)
echo "=== NODE VERSION ===" && (gh api repos/{owner}/{repo}/contents/.node-version 2>&1 || true)
echo "=== TOOL VERSIONS ===" && (gh api repos/{owner}/{repo}/contents/.tool-versions 2>&1 || true)
echo "=== PYTHON VERSION ===" && (gh api repos/{owner}/{repo}/contents/.python-version 2>&1 || true)
echo "=== RUST TOOLCHAIN ===" && (gh api repos/{owner}/{repo}/contents/rust-toolchain.toml 2>&1 || true)
echo "=== GO MOD ===" && (gh api repos/{owner}/{repo}/contents/go.mod 2>&1 || true)
echo "=== PACKAGE JSON ===" && (gh api repos/{owner}/{repo}/contents/package.json 2>&1 || true)
```

### Pass Condition
A version pinning file appropriate for the detected tech stack exists. The check detects the primary language and looks for the corresponding version file.

### Status Rules
- **PASS**: A version pinning file exists for the detected stack
- **FAIL**: No version pinning file found for the detected stack
- **WARN**: Tech stack could not be detected

**Stack-to-file mapping:**

| Primary Language | Version File(s) |
|-----------------|----------------|
| C# | `global.json` |
| JavaScript/TypeScript | `.nvmrc`, `.node-version`, or `.tool-versions` (requires `package.json` to exist) |
| Python | `.python-version` or `.tool-versions` |
| Rust | `rust-toolchain.toml` |
| Go | `go.mod` (with go directive) |

**Important**: For JavaScript/TypeScript, only check if `package.json` exists at the root (indicating a Node.js project). For Go, `go.mod` with a `go` directive already pins the version. For Rust, `rust-toolchain.toml` is optional since `Cargo.toml` can specify edition.

## Backlog Content

### What's Missing
No SDK/runtime version pinning file exists for this project's tech stack.

### Why It Matters
Without version pinning, different developers and CI environments may use different SDK or runtime versions, leading to "works on my machine" bugs, inconsistent builds, and subtle compatibility issues. Version pinning ensures everyone builds with the same toolchain.

### Quick Fix

**.NET (global.json):**
```bash
dotnet new globaljson --sdk-version 9.0.200
```

**Node.js (.nvmrc):**
```bash
node -v > .nvmrc
```

**Python (.python-version):**
```bash
python --version | cut -d' ' -f2 > .python-version
```

### Full Solution

**.NET — global.json:**
```json
{
  "sdk": {
    "version": "9.0.200",
    "rollForward": "latestFeature"
  }
}
```

**Node.js — .nvmrc:**
```
22.14.0
```

**Python — .python-version:**
```
3.13.2
```

**Rust — rust-toolchain.toml:**
```toml
[toolchain]
channel = "stable"
```

### Acceptance Criteria
- [ ] A version pinning file appropriate for the detected tech stack exists

### Notes
This check is stack-aware — it only fails if the detected primary language has a standard version pinning mechanism and it's missing. Projects with no detectable stack or stacks without a standard pinning convention get WARN instead of FAIL.

### References
- https://learn.microsoft.com/en-us/dotnet/core/tools/global-json
- https://github.com/nvm-sh/nvm#nvmrc
- https://github.com/asdf-vm/asdf
