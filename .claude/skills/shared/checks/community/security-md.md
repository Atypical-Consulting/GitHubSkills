---
name: Security Policy
slug: security-md
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Security Policy

## Verification

```bash
gh api repos/{owner}/{repo}/contents/SECURITY.md 2>&1 || true
```

### Pass Condition
The SECURITY.md file exists in the repository.

### Status Rules
- **PASS**: SECURITY.md exists in the repository root
- **FAIL**: SECURITY.md is missing from the repository

## Backlog Content

### What's Missing
No SECURITY.md file exists in the repository.

### Why It Matters
Without a security policy, people who discover vulnerabilities have no safe way to report them. They may open a public issue, exposing the vulnerability to attackers, or simply not report it at all.

### Quick Fix
```bash
# Create SECURITY.md in the repository root
cat > SECURITY.md << 'SECURITYEOF'
# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.
**Please do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please send an email with:
- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You can expect an initial response within 48 hours.
SECURITYEOF
```

### Full Solution
```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| latest  | :white_check_mark: |

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly.

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Instead, please send an email to [{owner's email or security contact}] with:

- A description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

You can expect an initial response within 48 hours. We will work with you to understand and address the issue before any public disclosure.

## Security Updates

Security updates will be released as patch versions. We recommend always using the latest version.
```

### Acceptance Criteria
- [ ] SECURITY.md exists in the repository root

### Notes
If the repo owner has a security email, use it. For org repos, there may be an org-level security policy -- check before creating a repo-level one.

### References
- https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository
