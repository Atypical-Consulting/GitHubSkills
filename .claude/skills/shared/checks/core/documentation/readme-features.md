---
name: README Features
slug: readme-features
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# README Features

## Verification

```bash
README_CONTENT=$(gh api repos/{owner}/{repo}/readme --jq '.content' 2>/dev/null | base64 -d 2>/dev/null)
if [ -z "$README_CONTENT" ]; then
  echo "SKIP: README not found"
  exit 0
fi

# Search for features-related headings (H1-H4)
FEATURES_HEADING=$(echo "$README_CONTENT" | grep -ciE '^#{1,4}\s.*(features|key features|highlights)' || true)
echo "Features headings found: $FEATURES_HEADING"
```

### Pass Condition

At least one heading (H1-H4) matches features-related keywords: "features", "key features", or "highlights".

### Status Rules

- **PASS**: 1+ features-related headings found
- **FAIL**: No features-related headings found
- **SKIP**: README is missing (the Tier 1 `readme` check handles that)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

The README does not contain a Features section listing the project's capabilities.

### Why It Matters

A Features section is the part visitors scan to decide if a project meets their needs. Without it, users must dig through documentation or source code to understand what the project offers. Listing features prominently helps users self-qualify and reduces time spent evaluating.

### Quick Fix

Add a Features section to your README:

```markdown
## Features

- Feature one description
- Feature two description
- Feature three description
```

### Full Solution

Add a comprehensive Features section that highlights the project's key capabilities:

```markdown
## Features

- **Type-safe API** — Compile-time validation of configuration rules
- **Fluent builder pattern** — Chainable, readable API for defining behavior
- **Async support** — Full async/await support for I/O-bound operations
- **Extensible** — Custom plugins via a simple interface
- **Well-tested** — 95%+ code coverage with unit and integration tests
- **Zero dependencies** — No external runtime dependencies
```

Tips:
- Lead with the most compelling features
- Use bold text for feature names, followed by a brief description
- Keep each item to one line for scannability
- Include 4-8 features (not too few, not overwhelming)
- Mention differentiators (what makes this project unique)

### Acceptance Criteria

- [ ] README contains a heading for Features (or "Key Features" or "Highlights")
- [ ] The section lists at least 3 project capabilities

### References

- https://www.makeareadme.com/
