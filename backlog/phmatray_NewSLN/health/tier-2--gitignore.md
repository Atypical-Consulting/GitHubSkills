# .gitignore

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/NewSLN` |
| **Source** | Health Check |
| **Tier** | 2 — Recommended |
| **Points** | 2 |
| **Status** | FAIL |
| **Detected** | 2026-02-26 |

## What's Missing

No .gitignore file exists in the repository.

## Why It Matters

Without a .gitignore, build artifacts, IDE settings, user secrets, and other generated files can be accidentally committed. This bloats the repository and can leak sensitive information. For a .NET project, this is especially important as build output (bin/, obj/) can be substantial.

## How to Fix

### Quick Fix

```bash
curl -o .gitignore https://raw.githubusercontent.com/github/gitignore/main/VisualStudio.gitignore && git add .gitignore && git commit -m "Add .gitignore for .NET" && git push
```

### Full Solution

Use GitHub's VisualStudio.gitignore template which covers .NET build output, IDE files, NuGet packages, and user-specific files. Review and customize as needed for your project.

## Acceptance Criteria

- [ ] .gitignore file exists in the repository root

## References

- https://github.com/github/gitignore/blob/main/VisualStudio.gitignore
