# Check File Format

Each health check is defined in a markdown file at `.claude/skills/shared/checks/{category}/{slug}.md`.

## Frontmatter

```yaml
---
check: Human-Readable Check Name
slug: kebab-case-slug
tier: 1|2|3
category: documentation|repo-settings|dev-config|ci-cd|community|security|maintenance
points: 4|2|1
scoring: Normal|INFO only
---
```

## Sections

### What to Check
The verification logic --- what command to run or what to look for.

### Status Rules
When the check should return each status:
- **PASS** --- condition met
- **FAIL** --- condition not met
- **WARN** --- cannot verify (e.g., insufficient permissions, API unavailable)

### Backlog Content
What to write to the backlog if the check fails:
- **Title** --- concise description of the issue
- **Description** --- what's wrong and why it matters
- **Acceptance Criteria** --- what "fixed" looks like

## Example

```markdown
---
check: README
slug: readme
tier: 1
category: documentation
points: 4
scoring: Normal
---

### What to Check
Verify README.md or README exists in the repository root.

### Status Rules
- PASS: README.md or README exists
- FAIL: No README found
- WARN: Cannot access repository contents

### Backlog Content
Title: Add README.md
Description: The repository has no README file...
Acceptance Criteria: README.md exists in repo root with project description
```
