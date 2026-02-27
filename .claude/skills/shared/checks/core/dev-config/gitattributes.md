---
name: .gitattributes
slug: gitattributes
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# .gitattributes

## Verification

```bash
gh api repos/{owner}/{repo}/contents/.gitattributes 2>&1 || true
```

### Pass Condition
A .gitattributes file exists in the repository root.

### Status Rules
- **PASS**: .gitattributes file exists
- **FAIL**: .gitattributes file is missing

## Backlog Content

### What's Missing
No .gitattributes file exists in the repository.

### Why It Matters
Without .gitattributes, line endings are handled inconsistently across platforms. Windows contributors may commit CRLF files, causing noisy diffs and merge conflicts with Linux/macOS contributors. The file also controls GitHub's language statistics and diff behavior for binary files.

### Quick Fix
```bash
echo "* text=auto" > .gitattributes
```

### Full Solution
Create a .gitattributes file tailored to the tech stack:

**.NET / C# projects:**
```gitattributes
# Auto-detect text files and normalize line endings
* text=auto

# Source code
*.cs text diff=csharp
*.csproj text
*.sln text eol=crlf
*.props text
*.targets text

# Config
*.json text
*.xml text
*.yml text
*.yaml text
*.md text

# Binary
*.png binary
*.jpg binary
*.ico binary
*.dll binary
*.exe binary
```

**Node.js / TypeScript projects:**
```gitattributes
* text=auto

*.js text
*.ts text
*.tsx text
*.json text
*.md text
*.yml text
*.yaml text
*.css text
*.html text

*.png binary
*.jpg binary
*.woff binary
*.woff2 binary
```

**Minimal (any project):**
```gitattributes
* text=auto
```

### Acceptance Criteria
- [ ] .gitattributes file exists in the repository root

### Notes
The minimal `* text=auto` line is sufficient for most projects — it normalizes line endings in the repository while letting Git auto-detect text vs binary files. Stack-specific patterns improve diff quality and GitHub language stats.

### References
- https://docs.github.com/en/get-started/getting-started-with-git/configuring-git-to-handle-line-endings
- https://git-scm.com/docs/gitattributes
