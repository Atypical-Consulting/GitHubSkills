---
name: Test Projects Exist
slug: dotnet-tests-exist
tier: 1
tier_label: Required
points: 4
scoring: normal
---

# Test Projects Exist

## Verification

```bash
gh api repos/{owner}/{repo}/git/trees/HEAD --jq '.tree[].path' 2>&1 | grep -iE '(test|tests).*\.csproj$' || echo 'NOT_FOUND'
```

### Pass Condition

At least one test project (`.csproj` file with `Test` or `Tests` in the path) exists in the repository.

### Status Rules

- **PASS**: At least one test `.csproj` file found (path contains `Test` or `Tests`)
- **FAIL**: No test projects found (`NOT_FOUND` returned)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

No test project exists in the repository. There are no `.csproj` files with `Test` or `Tests` in their path, and no references to xUnit, NUnit, or MSTest were detected.

### Why It Matters

Automated tests are foundational for any .NET project. Without them, regressions go undetected, refactoring is risky, and contributors have no way to verify their changes. Test projects provide a structured home for unit tests, integration tests, and assertions about expected behavior. CI pipelines cannot run `dotnet test` if there are no test projects to discover.

### Quick Fix

```bash
dotnet new xunit -n MyProject.Tests -o tests/MyProject.Tests
dotnet sln add tests/MyProject.Tests/MyProject.Tests.csproj
cd tests/MyProject.Tests
dotnet add reference ../../src/MyProject/MyProject.csproj
```

### Full Solution

1. Create a test project using xUnit (recommended for new .NET projects):
   ```bash
   dotnet new xunit -n <ProjectName>.Tests -o tests/<ProjectName>.Tests
   ```
2. Add the test project to the solution file.
3. Add a project reference to the main project being tested.
4. Write at least one meaningful test that validates core functionality.
5. Verify with `dotnet test` that the test project is discovered and tests pass.
6. If the repository has CI, ensure the workflow includes a `dotnet test` step.

### Acceptance Criteria

- [ ] At least one test project (`.csproj`) exists in the repository
- [ ] The test project references a test framework (xUnit, NUnit, or MSTest)
- [ ] The test project is included in the solution file
- [ ] `dotnet test` discovers and runs at least one test

### References

- https://learn.microsoft.com/en-us/dotnet/core/testing/
- https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-with-dotnet-test
- https://xunit.net/docs/getting-started/netcore/cmdline
