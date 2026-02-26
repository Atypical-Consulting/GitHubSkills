---
name: README
slug: readme
tier: 1
tier_label: Required
points: 4
scoring: normal
---

# README

## Verification

```bash
gh api repos/{owner}/{repo}/readme --jq '.size' 2>&1 || true
```

### Pass Condition

Exists AND response size > 500 bytes (not just a title).

### Status Rules

- **PASS**: README exists and is greater than 500 bytes
- **FAIL**: README is missing or <= 500 bytes

## Backlog Content

Use the content below when generating the backlog item file for a FAIL/WARN result.

### What's Missing

No README.md file exists in the repository (or it's too small to be useful).

### Why It Matters

Without a README, visitors have no context about what the project does, how to use it, or how to contribute. It's the first thing people see on the repository page and serves as the project's front door.

### Quick Fix

```bash
echo "# {repo}\n\nDescription of the project." > README.md
```

### Full Solution

Generate a substantive README tailored to the repository. Use the detected tech stack, project structure, and license to produce real content -- not a generic stub. A good README includes:
- **Project title and description**: What the project does and why it exists.
- **Getting Started**: Prerequisites, installation, and first-run instructions matching the tech stack.
- **Usage**: Key commands, API examples, or screenshots.
- **Contributing**: Link to CONTRIBUTING.md if it exists, or a brief note.
- **License**: State the license type and link to the LICENSE file.

For .NET projects, include `dotnet build` / `dotnet run` instructions. For Node.js, include `npm install` / `npm start`. Match the tech stack.

### Acceptance Criteria

- [ ] `README.md` exists in the repository root
- [ ] File size is greater than 500 bytes

### Notes

- The quick fix is only for unblocking -- always prefer the full solution for real projects.
- Inspect existing files (source code, configs, other docs) to infer the project's purpose. Do not use placeholder text.

### References

- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
