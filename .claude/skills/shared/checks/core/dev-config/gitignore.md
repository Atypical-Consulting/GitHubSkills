---
name: .gitignore
slug: gitignore
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# .gitignore

## Verification

```bash
gh api repos/{owner}/{repo}/contents/.gitignore 2>&1 || true
```

### Pass Condition
The `.gitignore` file exists in the repository root.

### Status Rules
- **PASS**: API returns file metadata (HTTP 200)
- **FAIL**: API returns 404 (file not found)

## Backlog Content

### What's Missing
No .gitignore file exists in the repository.

### Why It Matters
Without a .gitignore, build artifacts, IDE settings, OS files, and other generated content end up tracked in version control. This bloats the repo, creates noisy diffs, and can accidentally expose sensitive files.

### Quick Fix
```bash
curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/{Template}.gitignore
```

### Full Solution
Select the template based on detected tech stack:

| Tech Stack | Template |
|-----------|----------|
| .NET | `VisualStudio.gitignore` |
| Node.js | `Node.gitignore` |
| Python | `Python.gitignore` |
| Rust | `Rust.gitignore` |
| Go | `Go.gitignore` |
| Java (Maven) | `Maven.gitignore` |
| Java (Gradle) | `Gradle.gitignore` |
| Ruby | `Ruby.gitignore` |
| PHP | `Composer.gitignore` |

For multi-stack repos, concatenate relevant templates with section headers. If no tech stack detected, use a minimal .gitignore covering OS and editor files (.DS_Store, Thumbs.db, .vscode/, .idea/, *.swp).

### Acceptance Criteria
- [ ] `.gitignore` file exists in the repository root

### Notes
Always inspect the repo for build artifacts or generated files that should be ignored beyond the standard template.

### References
- https://docs.github.com/en/get-started/getting-started-with-git/ignoring-files
