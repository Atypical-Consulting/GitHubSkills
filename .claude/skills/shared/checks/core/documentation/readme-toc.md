---
name: README Table of Contents
slug: readme-toc
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# README Table of Contents

## Verification

```bash
README_CONTENT=$(gh api repos/{owner}/{repo}/readme --jq '.content' 2>/dev/null | base64 -d 2>/dev/null)
if [ -z "$README_CONTENT" ]; then
  echo "SKIP: README not found"
  exit 0
fi

# Skip if README is too short (< 2000 bytes) — short READMEs don't need a TOC
README_SIZE=$(echo "$README_CONTENT" | wc -c | tr -d ' ')
if [ "$README_SIZE" -lt 2000 ]; then
  echo "SKIP: README is too short ($README_SIZE bytes < 2000) for a TOC to be necessary"
  exit 0
fi

# Search for TOC patterns: HTML comment, heading, or 3+ anchor links
TOC_COMMENT=$(echo "$README_CONTENT" | grep -ci '<!-- TOC\|<!-- TABLE OF CONTENTS' || true)
TOC_HEADING=$(echo "$README_CONTENT" | grep -ciE '^#{1,4}\s.*table of contents' || true)
ANCHOR_LINKS=$(echo "$README_CONTENT" | grep -c '](#' || true)

echo "TOC comment markers: $TOC_COMMENT"
echo "TOC headings: $TOC_HEADING"
echo "Anchor links: $ANCHOR_LINKS"
```

### Pass Condition

At least one of:
- A `<!-- TOC -->` or `<!-- TABLE OF CONTENTS -->` HTML comment marker
- A heading matching "Table of Contents"
- 3 or more markdown links to heading anchors (`](#`)

### Status Rules

- **PASS**: TOC pattern found
- **FAIL**: No TOC pattern found in a README >= 2000 bytes
- **SKIP**: README is missing OR README is < 2000 bytes (short READMEs don't need a TOC)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

The README is longer than 2000 bytes but does not include a Table of Contents for navigation.

### Why It Matters

Long READMEs without a Table of Contents force readers to scroll through the entire document to find what they need. A TOC provides quick navigation and helps users understand the document's structure at a glance. All well-organized long-form documentation includes one.

### Quick Fix

Add a simple Table of Contents after your introduction:

```markdown
## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
```

### Full Solution

Add a Table of Contents that links to all major sections of your README:

```markdown
## Table of Contents

- [Features](#features)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Basic Example](#basic-example)
  - [Advanced Example](#advanced-example)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)
```

Tips:
- Place the TOC early in the README (after badges and introduction)
- Include all H2 and important H3 headings
- Use nested lists for subsections
- Consider using a TOC generator tool to keep it in sync (e.g., `markdown-toc`, VS Code Markdown All in One extension)
- You can also use HTML comment markers (`<!-- TOC -->`) for auto-generated TOCs

### Acceptance Criteria

- [ ] README contains a Table of Contents (heading, HTML comment marker, or 3+ anchor links)
- [ ] TOC links match actual section headings in the README

### References

- https://github.com/jonschlinkert/markdown-toc
