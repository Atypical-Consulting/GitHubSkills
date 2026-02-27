---
name: README Description
slug: readme-description
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# README Description

## Verification

```bash
README_CONTENT=$(gh api repos/{owner}/{repo}/readme --jq '.content' 2>/dev/null | base64 -d 2>/dev/null)
if [ -z "$README_CONTENT" ]; then
  echo "SKIP: README not found"
  exit 0
fi

# Count non-empty lines that aren't headings, badges, tables, or HTML
PROSE_LINES=$(echo "$README_CONTENT" | grep -v '^\s*$' | grep -v '^\s*#' | grep -v '^\s*|' | grep -v '^\[!' | grep -v '^\!\[' | grep -v '^\s*<' | grep -v '^\s*```' | grep -v '^\s*---' | grep -v '^\s*\*\*\*' | wc -l | tr -d ' ')
echo "Prose lines found: $PROSE_LINES"
```

### Pass Condition

3 or more prose lines found (non-empty lines that are not headings, badges, table rows, or HTML).

### Status Rules

- **PASS**: 3+ prose lines found
- **FAIL**: Fewer than 3 prose lines
- **SKIP**: README is missing (the Tier 1 `readme` check handles that)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

The README lacks substantive prose description. It may contain only headings, badges, or tables without explaining what the project does or why it exists.

### Why It Matters

A clear prose description is the first thing visitors read. Without it, people can't quickly understand what the project does, what problem it solves, or why they should care. All well-maintained open source projects open with a compelling description paragraph.

### Quick Fix

Add a 2-3 sentence description at the top of your README, right after the title and badges:

```markdown
# {repo}

A brief description of what this project does, what problem it solves, and who it's for.
```

### Full Solution

Add a substantive introduction section to your README:

1. **Tagline**: A one-line summary of what the project does
2. **Description paragraph**: 2-3 sentences explaining the problem it solves, the approach it takes, and who benefits
3. **"Why" section** (optional): Explain what makes this project different or why it was created

Example:
```markdown
# MyProject

> A fast, type-safe library for building form validations in .NET.

MyProject simplifies form validation by providing a fluent API that catches errors at compile time. Instead of writing repetitive validation logic, you declare rules once and the library handles the rest — including error messages, async validation, and cross-field dependencies.

## Why MyProject?

- **Type-safe**: Validation rules are checked at compile time
- **Fluent API**: Readable, chainable rule definitions
- **Extensible**: Add custom validators with a single method
```

### Acceptance Criteria

- [ ] README contains at least 3 lines of prose description (not headings, badges, or tables)
- [ ] The description explains what the project does and why it exists

### References

- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes
- https://www.makeareadme.com/
