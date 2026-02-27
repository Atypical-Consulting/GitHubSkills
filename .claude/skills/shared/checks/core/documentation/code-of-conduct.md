---
name: Code of Conduct
slug: code-of-conduct
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Code of Conduct

## Verification

```bash
echo "=== ROOT ===" && (gh api repos/{owner}/{repo}/contents/CODE_OF_CONDUCT.md 2>&1 || true)
echo "=== DOCS ===" && (gh api repos/{owner}/{repo}/contents/docs/CODE_OF_CONDUCT.md 2>&1 || true)
echo "=== COMMUNITY ===" && (gh api repos/{owner}/{repo}/community/profile --jq '.files.code_of_conduct' 2>&1 || true)
```

### Pass Condition
A CODE_OF_CONDUCT.md file exists in the repository root or docs directory, or GitHub's community profile detects one (including org-level).

### Status Rules
- **PASS**: Code of conduct file found or community profile reports one
- **FAIL**: No code of conduct detected

## Backlog Content

### What's Missing
No CODE_OF_CONDUCT.md file exists in the repository.

### Why It Matters
A code of conduct sets expectations for participant behavior and signals that the project is a welcoming space. GitHub highlights its presence in the community profile, and many contributors check for it before engaging with a project.

### Quick Fix
```bash
# Adopt the Contributor Covenant (most popular)
curl -sL https://www.contributor-covenant.org/version/2/1/code_of_conduct/code_of_conduct.md \
  -o CODE_OF_CONDUCT.md
```

### Full Solution
The [Contributor Covenant](https://www.contributor-covenant.org/) is the most widely adopted code of conduct for open source. Download version 2.1 and customize the contact method:

```markdown
# Contributor Covenant Code of Conduct

## Our Pledge

We as members, contributors, and leaders pledge to make participation in our
community a harassment-free experience for everyone...

## Enforcement

Instances of abusive, harassing, or otherwise unacceptable behavior may be
reported to the community leaders responsible for enforcement at
[INSERT CONTACT METHOD].
```

Replace `[INSERT CONTACT METHOD]` with an email address or other contact mechanism.

### Acceptance Criteria
- [ ] CODE_OF_CONDUCT.md exists in the repository

### Notes
GitHub can also inherit a code of conduct from the `.github` organization-wide repository. If the community profile already reports a code of conduct via org-level settings, this check passes.

### References
- https://www.contributor-covenant.org/
- https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-a-code-of-conduct-to-your-project
