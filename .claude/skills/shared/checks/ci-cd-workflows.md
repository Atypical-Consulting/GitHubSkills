---
name: CI/CD Workflows
slug: ci-cd-workflows
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# CI/CD Workflows

## Verification

```bash
gh api repos/{owner}/{repo}/contents/.github/workflows 2>&1 || true
```

### Pass Condition
The `.github/workflows/` directory exists and contains at least one `.yml` or `.yaml` file.

### Status Rules
- **PASS**: Directory exists with >= 1 .yml/.yaml file
- **FAIL**: Directory is missing or empty

## Backlog Content

### What's Missing
No GitHub Actions workflow files exist in the repository.

### Why It Matters
Without CI/CD, there's no automated build verification, test execution, or deployment pipeline. Bugs and regressions slip through more easily, and contributors have no confidence that their changes work.

### Quick Fix
```bash
mkdir -p .github/workflows
# Create .github/workflows/ci.yml with a starter workflow for your tech stack
```

### Full Solution
Create a CI workflow matching the project's tech stack.

#### .NET
```yaml
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
          dotnet-version: '8.0.x'
      - run: dotnet restore
      - run: dotnet build --no-restore
      - run: dotnet test --no-build --verbosity normal
```

#### Node.js
```yaml
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
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm test
```

#### Python
```yaml
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
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install -e ".[dev]"
      - run: pytest
```

#### Rust
```yaml
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
      - uses: dtolnay/rust-toolchain@stable
      - run: cargo build --verbose
      - run: cargo test --verbose
```

#### Go
```yaml
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
      - uses: actions/setup-go@v5
        with:
          go-version: '1.22'
      - run: go build ./...
      - run: go test ./...
```

Adjust the default branch name and language versions to match what the project actually uses.

### Acceptance Criteria
- [ ] At least one .yml/.yaml file exists in `.github/workflows/`
- [ ] The workflow includes build and test steps appropriate to the tech stack

### Notes
If CI already exists but is broken, fixing it is out of scope — the check only verifies existence. For multi-stack repos, consider a matrix strategy.

### References
- https://docs.github.com/en/actions/quickstart
