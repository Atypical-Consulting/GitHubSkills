# CI/CD Workflows

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/SudokuSolver` |
| **Source** | Health Check |
| **Tier** | 2 — Recommended |
| **Points** | 2 |
| **Status** | PASS |
| **PR** | https://github.com/phmatray/SudokuSolver/pull/12 |
| **Detected** | 2026-02-26 |

## What's Missing

No GitHub Actions workflow files found in `.github/workflows/`.

## Why It Matters

Without CI/CD, there's no automated build or test verification on pull requests or pushes. Bugs and regressions can be merged without detection. For a .NET project using OR-Tools, automated builds also verify that dependencies resolve correctly across environments.

## How to Fix

### Quick Fix

```bash
mkdir -p .github/workflows && cat > .github/workflows/ci.yml <<'EOF'
name: CI

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
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '10.0.x'
      - run: dotnet restore
      - run: dotnet build --no-restore
      - run: dotnet test --no-build --verbosity normal
EOF
```

### Full Solution

Create a workflow that:
1. Triggers on push to `main` and on pull requests
2. Sets up .NET SDK 10.0 (matching `global.json`)
3. Restores, builds, and runs tests
4. Optionally adds caching for NuGet packages to speed up builds

## Acceptance Criteria

- [x] `.github/workflows/` directory exists with at least one `.yml` or `.yaml` file
- [ ] Workflow runs successfully on push/PR

## References

- https://docs.github.com/en/actions/automating-builds-and-tests/building-and-testing-net
