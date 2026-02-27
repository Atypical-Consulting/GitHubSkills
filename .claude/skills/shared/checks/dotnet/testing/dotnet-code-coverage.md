---
name: Code Coverage Configuration
slug: dotnet-code-coverage
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# Code Coverage Configuration

## Verification

```bash
TEST_CSPROJS=$(gh api repos/{owner}/{repo}/git/trees/HEAD --jq '.tree[].path' 2>&1 | grep -iE '(test|tests).*\.csproj$')
if [ -z "$TEST_CSPROJS" ]; then
  echo 'NO_TEST_PROJECTS'
else
  FOUND_COVERLET=false
  for csproj in $TEST_CSPROJS; do
    CONTENT=$(gh api repos/{owner}/{repo}/contents/$csproj --jq '.content' 2>&1 | base64 -d 2>/dev/null)
    if echo "$CONTENT" | grep -qi 'coverlet'; then
      FOUND_COVERLET=true
      break
    fi
  done
  if [ "$FOUND_COVERLET" = true ]; then
    echo 'COVERLET_FOUND'
  else
    echo 'COVERLET_NOT_FOUND'
  fi
fi
```

### Pass Condition

At least one test project references `coverlet.collector` or `coverlet.msbuild` as a package.

### Status Rules

- **PASS**: Coverlet package reference found in a test project (`COVERLET_FOUND`)
- **FAIL**: Test projects exist but no coverlet reference found (`COVERLET_NOT_FOUND`)
- **WARN**: No test projects exist to check (`NO_TEST_PROJECTS`)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

Test projects exist but no code coverage tool (coverlet) is configured. There is no `coverlet.collector` or `coverlet.msbuild` package reference in any test project.

### Why It Matters

Code coverage metrics show which lines and branches are exercised by tests. Without coverage tooling, teams fly blind -- they cannot identify untested code paths, track coverage trends over time, or set minimum coverage thresholds in CI. Coverlet is the standard open-source coverage tool for .NET and integrates seamlessly with `dotnet test`.

### Quick Fix

```bash
cd tests/MyProject.Tests
dotnet add package coverlet.collector
# Run with coverage:
dotnet test --collect:"XPlat Code Coverage"
```

### Full Solution

1. Add `coverlet.collector` to each test project:
   ```bash
   dotnet add package coverlet.collector
   ```
2. Run tests with coverage collection:
   ```bash
   dotnet test --collect:"XPlat Code Coverage" --results-directory ./coverage
   ```
3. Install `reportgenerator` to produce HTML reports:
   ```bash
   dotnet tool install -g dotnet-reportgenerator-globaltool
   reportgenerator -reports:./coverage/**/coverage.cobertura.xml -targetdir:./coverage/report
   ```
4. Add coverage collection to CI workflows and optionally upload to a service like Codecov or Coveralls.
5. Consider setting a minimum coverage threshold in CI to prevent regressions.

### Acceptance Criteria

- [ ] At least one test project references `coverlet.collector` or `coverlet.msbuild`
- [ ] `dotnet test --collect:"XPlat Code Coverage"` produces a coverage report
- [ ] Coverage results are generated in Cobertura or OpenCover format

### References

- https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-code-coverage
- https://github.com/coverlet-coverage/coverlet
- https://learn.microsoft.com/en-us/dotnet/core/additional-tools/dotnet-coverage
