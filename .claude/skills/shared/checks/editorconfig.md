---
name: EditorConfig
slug: editorconfig
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# EditorConfig

## Verification

```bash
gh api repos/{owner}/{repo}/contents/.editorconfig 2>&1 || true
```

### Pass Condition
The `.editorconfig` file exists in the repository root.

### Status Rules
- **PASS**: API returns file metadata (HTTP 200)
- **FAIL**: API returns 404 (file not found)

## Backlog Content

### What's Missing
No .editorconfig file exists in the repository.

### Why It Matters
Without an .editorconfig, different editors use different defaults for indentation, line endings, and trailing whitespace. This creates noisy diffs, inconsistent formatting, and unnecessary merge conflicts across contributors.

### Quick Fix
```bash
# For .NET: cp {skills-path}/shared/editorconfigs/dotnet.editorconfig .editorconfig
# For JS/TS: cp {skills-path}/shared/editorconfigs/javascript.editorconfig .editorconfig
# For Python: cp {skills-path}/shared/editorconfigs/python.editorconfig .editorconfig
# For Rust: cp {skills-path}/shared/editorconfigs/rust.editorconfig .editorconfig
# For Go: cp {skills-path}/shared/editorconfigs/go.editorconfig .editorconfig
```

### Full Solution
Select shared reference by tech stack:

| Tech Stack | Shared Reference |
|-----------|-----------------|
| .NET (.csproj, .sln) | `shared/editorconfigs/dotnet.editorconfig` |
| JavaScript/TypeScript (package.json, tsconfig.json) | `shared/editorconfigs/javascript.editorconfig` |
| Python (pyproject.toml, setup.py) | `shared/editorconfigs/python.editorconfig` |
| Rust (Cargo.toml) | `shared/editorconfigs/rust.editorconfig` |
| Go (go.mod) | `shared/editorconfigs/go.editorconfig` |

When generating the backlog item, detect the tech stack and suggest the matching shared `.editorconfig` from `../editorconfigs/`.

For multi-stack repos, start with the primary language's template and merge sections. If no match, use a minimal config with `root = true`, space indent, LF line endings, UTF-8, trim trailing whitespace, insert final newline.

### Acceptance Criteria
- [ ] `.editorconfig` file exists in the repository root
- [ ] The file contains `root = true`

### Notes
EditorConfig standardizes formatting across editors (VS Code, Rider, vim, etc.), reducing noise in diffs. Most editors have built-in or plugin support. Shared references are in `.claude/skills/shared/editorconfigs/`.

### References
- https://editorconfig.org
