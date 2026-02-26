---
name: README License Mention
slug: readme-license-mention
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# README License Mention

## Verification

```bash
README_CONTENT=$(gh api repos/{owner}/{repo}/readme --jq '.content' 2>/dev/null | base64 -d 2>/dev/null)
if [ -z "$README_CONTENT" ]; then
  echo "SKIP: README not found"
  exit 0
fi

# Search for the word "license" (case-insensitive)
LICENSE_MENTION=$(echo "$README_CONTENT" | grep -ci 'license' || true)
echo "License mentions found: $LICENSE_MENTION"
```

### Pass Condition

The word "license" appears at least once in the README (case-insensitive).

### Status Rules

- **PASS**: "license" found in README text
- **FAIL**: "license" not found anywhere in README
- **SKIP**: README is missing (the Tier 1 `readme` check handles that)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

The README does not mention the project's license anywhere in its text.

### Why It Matters

Even when a LICENSE file exists in the repository, mentioning the license in the README makes it immediately visible to visitors without requiring them to check another file. It signals that the project is open source and clarifies usage rights upfront. This complements the Tier 1 `license` check which verifies the LICENSE file exists.

### Quick Fix

Add a License section at the bottom of your README:

```markdown
## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
```

### Full Solution

Add a License section as one of the last sections in your README:

```markdown
## License

This project is licensed under the [MIT License](LICENSE).
```

If your project uses multiple licenses or has specific terms:

```markdown
## License

This project is dual-licensed under the [MIT License](LICENSE-MIT) and [Apache License 2.0](LICENSE-APACHE). You may choose either license.
```

Tips:
- Place the License section near the bottom of the README (convention)
- Link to the actual LICENSE file in the repository
- State the license name explicitly (not just "see LICENSE")
- If you have a license badge, it also satisfies this check

### Acceptance Criteria

- [ ] The word "license" appears somewhere in the README
- [ ] Ideally links to the LICENSE file in the repository

### References

- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository
