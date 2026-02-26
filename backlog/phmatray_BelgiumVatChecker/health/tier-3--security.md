# SECURITY.md

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/BelgiumVatChecker` |
| **Source** | Health Check |
| **Tier** | 3 — Nice to Have |
| **Points** | 1 |
| **Status** | FAIL |
| **Detected** | 2026-02-26 |

## What's Missing

No SECURITY.md file exists in the repository.

## Why It Matters

A security policy tells users how to responsibly report vulnerabilities. Without one, security issues may be reported publicly in issues, exposing the project to risk before a fix is available.

## How to Fix

### Quick Fix

```bash
cat > SECURITY.md << 'EOF'
# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly:

1. **Do not** open a public GitHub issue
2. Email [your-email@example.com] with details
3. Include steps to reproduce the vulnerability
4. Allow reasonable time for a fix before public disclosure

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest  | Yes       |
EOF
```

### Full Solution

Create a `SECURITY.md` in the repository root. Consider enabling GitHub's private vulnerability reporting feature in Settings > Security > Private vulnerability reporting.

## Acceptance Criteria

- [ ] SECURITY.md file exists in the repository root

## References

- https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository
