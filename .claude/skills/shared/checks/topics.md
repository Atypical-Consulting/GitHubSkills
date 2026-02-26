---
name: Topics
slug: topics
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# Topics

## Verification

```bash
gh repo view {owner}/{repo} --json repositoryTopics -q '.repositoryTopics[].name' 2>&1 || true
```

### Pass Condition
At least one topic is set on the repository.

### Status Rules
- **PASS**: At least 1 topic is set
- **FAIL**: No topics are set

## Backlog Content

### What's Missing
No topics are set on the repository.

### Why It Matters
Topics improve discoverability on GitHub. They appear on the repo page and in GitHub search. Without them, the project is harder to find for users searching by technology or domain.

### Quick Fix
```bash
gh repo edit {owner}/{repo} --add-topic {topic1} --add-topic {topic2}
```

### Full Solution
Suggest topics by tech stack:

| Tech Stack | Suggested Topics |
|-----------|-----------------|
| .NET | `dotnet`, `csharp`, `netcore` |
| Node.js | `nodejs`, `javascript`, `typescript` (if tsconfig exists) |
| Python | `python`, `python3` |
| Rust | `rust`, `cargo` |
| Go | `golang`, `go` |

Also consider: project type (`cli`, `library`, `api`, `web-app`, `tool`, `framework`), domain (`devtools`, `data`, `security`, `automation`), license (`open-source`, `mit-license`). Aim for 3-5 relevant topics. Avoid overly generic topics like `code` or `project`.

### Acceptance Criteria
- [ ] At least one topic is set on the repository

### Notes
This is an **API-only fix** -- no file changes or PR needed. Topics improve discoverability.

### References
- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/classifying-your-repository-with-topics
