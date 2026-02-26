# CI/CD Workflows

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/NewSLN` |
| **Tier** | 2 — Recommended |
| **Points** | 2 |
| **Status** | FAIL |
| **Detected** | 2026-02-26 |

## What's Missing

No GitHub Actions workflow files found in `.github/workflows/`.

## Why It Matters

Without CI/CD, there is no automated build verification, test execution, or deployment pipeline. Bugs and regressions can be merged without detection. Automated workflows are essential for maintaining code quality as the project grows.

## How to Fix

### Quick Fix

```bash
mkdir -p .github/workflows && cat > .github/workflows/build.yml << 'EOF'
name: Build and Test

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Setup .NET
      uses: actions/setup-dotnet@v4
      with:
        dotnet-version: '8.0.x'
    - name: Restore
      run: dotnet restore
    - name: Build
      run: dotnet build --no-restore
    - name: Test
      run: dotnet test --no-build --verbosity normal
EOF
git add .github/workflows/build.yml && git commit -m "Add CI workflow" && git push
```

### Full Solution

Start with a basic build-and-test workflow, then expand with release workflows, code coverage, and linting as needed.

## Acceptance Criteria

- [ ] `.github/workflows/` directory exists
- [ ] At least one `.yml` or `.yaml` workflow file is present

## References

- https://docs.github.com/en/actions/quickstart
- https://github.com/actions/setup-dotnet
