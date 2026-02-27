---
name: README Badges
slug: readme-badges
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# README Badges

## Verification

```bash
README_CONTENT=$(gh api repos/{owner}/{repo}/readme --jq '.content' 2>/dev/null | base64 -d 2>/dev/null)
if [ -z "$README_CONTENT" ]; then
  echo "SKIP: README not found"
  exit 0
fi

# Search for common badge patterns
BADGE_COUNT=$(echo "$README_CONTENT" | grep -ciE 'shields\.io|badgen\.net|img\.shields|codecov\.io|badge\.svg|badge\.fury|github\.com/.*/(actions/)?workflows/.*\.svg|nuget\.org/.*badge|coveralls\.io' || true)
echo "Badge patterns found: $BADGE_COUNT"
```

### Pass Condition

At least one badge pattern found (shields.io, badgen.net, codecov, workflow SVGs, NuGet badges, etc.).

### Status Rules

- **PASS**: 1+ badge patterns found
- **FAIL**: No badge patterns found
- **SKIP**: README is missing (the Tier 1 `readme` check handles that)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

The README does not include any status badges (build status, NuGet version, coverage, license, etc.).

### Why It Matters

Badges provide at-a-glance project health signals. They show visitors that the project is actively maintained, has passing CI, is published to package registries, and has test coverage. Professional open source projects universally use badges as trust indicators.

### Quick Fix

Add a badge block at the top of your README, right after the title:

```markdown
# {repo}

[![NuGet](https://img.shields.io/nuget/v/{package-name})](https://www.nuget.org/packages/{package-name})
[![Build](https://github.com/{owner}/{repo}/actions/workflows/build.yml/badge.svg)](https://github.com/{owner}/{repo}/actions/workflows/build.yml)
[![License](https://img.shields.io/github/license/{owner}/{repo})](LICENSE)
```

### Full Solution

Add relevant badges based on your project's tech stack and services:

**For .NET projects:**
```markdown
[![NuGet](https://img.shields.io/nuget/v/{package-name})](https://www.nuget.org/packages/{package-name})
[![NuGet Downloads](https://img.shields.io/nuget/dt/{package-name})](https://www.nuget.org/packages/{package-name})
[![Build](https://github.com/{owner}/{repo}/actions/workflows/build.yml/badge.svg)](https://github.com/{owner}/{repo}/actions/workflows/build.yml)
[![Coverage](https://codecov.io/gh/{owner}/{repo}/branch/main/graph/badge.svg)](https://codecov.io/gh/{owner}/{repo})
[![License](https://img.shields.io/github/license/{owner}/{repo})](LICENSE)
```

**For Node.js projects:**
```markdown
[![npm](https://img.shields.io/npm/v/{package-name})](https://www.npmjs.com/package/{package-name})
[![Build](https://github.com/{owner}/{repo}/actions/workflows/ci.yml/badge.svg)](https://github.com/{owner}/{repo}/actions/workflows/ci.yml)
[![License](https://img.shields.io/github/license/{owner}/{repo})](LICENSE)
```

Common badge categories to consider:
- **Package version**: NuGet, npm, PyPI, crates.io
- **Build status**: GitHub Actions, Azure DevOps
- **Test coverage**: Codecov, Coveralls
- **License**: GitHub license detection
- **Downloads**: Package registry download counts

### Acceptance Criteria

- [ ] README contains at least one status badge
- [ ] Badges are placed prominently near the top of the README

### References

- https://shields.io/
- https://github.com/badges/shields
