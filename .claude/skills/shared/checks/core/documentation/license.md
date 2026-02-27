---
name: LICENSE
slug: license
tier: 1
tier_label: Required
points: 4
scoring: normal
---

# LICENSE

## Verification

```bash
gh api repos/{owner}/{repo}/license --jq '.license.spdx_id' 2>&1 || true
```

### Pass Condition

Exists (any recognized license).

### Status Rules

- **PASS**: LICENSE file exists with a recognized license
- **FAIL**: LICENSE file is missing

## Backlog Content

Use the content below when generating the backlog item file for a FAIL/WARN result.

### What's Missing

No LICENSE file exists in the repository.

### Why It Matters

Without a license, the code is technically "all rights reserved" by default. Contributors and users have no legal clarity about how they can use, modify, or distribute the code. This blocks adoption and contribution.

### Quick Fix

```bash
curl -o LICENSE https://choosealicense.com/licenses/mit/
```

### Full Solution

1. Determine the appropriate license. If the repo already has license hints (e.g., a `<PackageLicenseExpression>` in a .csproj, a `license` field in package.json), use that.
2. Download the license text from choosealicense.com or GitHub's license API.
3. Replace placeholder fields (year, author name) with actual values from the repo owner's profile.

Common options: MIT (`https://choosealicense.com/licenses/mit/`), Apache 2.0 (`https://choosealicense.com/licenses/apache-2.0/`), GPL 3.0 (`https://choosealicense.com/licenses/gpl-3.0/`).

### Acceptance Criteria

- [ ] `LICENSE` file exists in the repository root
- [ ] File contains a recognized open-source license

### Notes

- If unsure which license to use, suggest MIT as a safe default and let the user choose.
- Some licenses require the copyright holder name and year -- fill these in rather than leaving placeholders.

### References

- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository
