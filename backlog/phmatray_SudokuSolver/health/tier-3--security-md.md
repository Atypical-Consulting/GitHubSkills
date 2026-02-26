# SECURITY.md

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/SudokuSolver` |
| **Source** | Health Check |
| **Tier** | 3 — Nice to Have |
| **Points** | 1 |
| **Status** | PASS |
| **PR** | https://github.com/phmatray/SudokuSolver/pull/18 |
| **Detected** | 2026-02-26 |

## What's Missing

No SECURITY.md file exists in the repository.

## Why It Matters

Without a security policy, anyone who discovers a vulnerability has no guidance on how to report it responsibly. They may open a public issue, exposing the vulnerability before a fix is available.

## How to Fix

### Quick Fix

```bash
cat > SECURITY.md <<'EOF'
# Security Policy

## Reporting a Vulnerability

If you discover a security vulnerability, please report it responsibly by emailing the maintainer directly rather than opening a public issue.

## Supported Versions

| Version | Supported |
|---------|-----------|
| latest  | Yes       |
EOF
```

### Full Solution

Include your preferred contact method, expected response time, and which versions receive security patches.

## Acceptance Criteria

- [x] SECURITY.md file exists in the repository root

## References

- https://docs.github.com/en/code-security/getting-started/adding-a-security-policy-to-your-repository
