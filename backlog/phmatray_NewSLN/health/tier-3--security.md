# SECURITY.md

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/NewSLN` |
| **Source** | Health Check |
| **Tier** | 3 — Nice to Have |
| **Points** | 1 |
| **Status** | FAIL |
| **Detected** | 2026-02-26 |

## What's Missing

No SECURITY.md file exists in the repository.

## Why It Matters

Without a security policy, vulnerability reporters don't know how to responsibly disclose issues. They may resort to public issue filing, exposing vulnerabilities before a fix is available.

## How to Fix

### Quick Fix

```bash
cat > SECURITY.md << 'EOF'
# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly by emailing [your-email@example.com]. Do not open a public issue.

We will acknowledge receipt within 48 hours and provide an estimated timeline for a fix.
EOF
git add SECURITY.md && git commit -m "Add security policy" && git push
```

### Full Solution

Include supported versions, disclosure timeline, and a PGP key or GitHub Security Advisories link for encrypted reporting.

## Acceptance Criteria

- [ ] SECURITY.md exists in the repository root

## References

- https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository
