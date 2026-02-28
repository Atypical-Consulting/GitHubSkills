# Check File Format

Each health check is defined in a markdown file within its module's directory:

- Core checks: `.claude/skills/shared/checks/core/{category}/{slug}.md`
- .NET checks: `.claude/skills/shared/checks/dotnet/{category}/{slug}.md`

## Frontmatter

```yaml
---
check: Human-Readable Check Name
slug: kebab-case-slug
tier: 1|2|3
category: category-within-module
points: 4|2|1
scoring: Normal|INFO only
---
```

The `category` field depends on the module:

| Module | Valid Categories |
|--------|-----------------|
| Core | `documentation`, `repo-settings`, `dev-config`, `ci-cd`, `community`, `security`, `maintenance` |
| .NET | `build-config`, `code-quality`, `testing`, `packaging` |

## Sections

### What to Check
The verification logic --- what command to run or what to look for.

### Status Rules
When the check should return each status:
- **PASS** --- condition met
- **FAIL** --- condition not met
- **WARN** --- cannot verify (e.g., insufficient permissions, API unavailable)

### Project Item Content
What to create as a GitHub Project item if the check fails:
- **Title** --- concise description of the issue
- **Description** --- what's wrong and why it matters
- **Acceptance Criteria** --- what "fixed" looks like

## Example (Core Check)

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

### Project Item Content
Title: Add README.md
Description: The repository has no README file...
Acceptance Criteria: README.md exists in repo root with project description
```

## Example (.NET Check)

```markdown
---
check: Directory.Build.props
slug: dotnet-build-props
tier: 1
category: build-config
points: 4
scoring: Normal
---

### What to Check
Verify Directory.Build.props exists in the repository root via `gh api`.

### Status Rules
- PASS: Directory.Build.props exists
- FAIL: Directory.Build.props not found
- WARN: Cannot access repository contents (403)

### Project Item Content
Title: Add Directory.Build.props
Description: No centralized MSBuild properties file found...
Acceptance Criteria: Directory.Build.props exists with shared properties
```
