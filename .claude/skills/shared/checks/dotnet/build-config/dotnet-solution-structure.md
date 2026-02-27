---
name: Solution Structure
slug: dotnet-solution-structure
tier: 2
tier_label: Recommended
points: 2
scoring: normal
---

# Solution Structure

## Verification

```bash
gh api repos/{owner}/{repo}/contents/ --jq '.[].name' 2>&1 || true
```

### Pass Condition

Both `src` and `tests` directories exist in the repository root, indicating an organized solution structure.

### Status Rules

- **PASS**: Both `src` and `tests` directories are present in the root listing
- **FAIL**: One or both of `src` and `tests` directories are missing

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

The repository does not use the conventional `src/` and `tests/` folder separation for .NET solution structure.

### Why It Matters

Mixing source projects and test projects at the same level makes it harder to navigate the solution, configure CI pipelines, set up code coverage exclusions, and understand project boundaries. The `src/` + `tests/` convention is widely adopted in the .NET ecosystem (used by ASP.NET Core, EF Core, and most major open-source .NET projects). It provides clear separation of production code from test code, simplifies glob patterns in build scripts, and makes the repository structure immediately understandable to new contributors.

### Quick Fix

```bash
mkdir -p src tests
# Move source projects into src/
# Move test projects into tests/
# Update .sln file references accordingly
```

### Full Solution

1. Create `src/` and `tests/` directories at the repository root.
2. Move all source/library/application projects into `src/`.
3. Move all test projects (unit, integration, benchmarks) into `tests/`.
4. Update the `.sln` file to reflect the new paths — either manually edit the `Project` entries or re-add projects via `dotnet sln`.
5. Update any `Directory.Build.props` or `Directory.Build.targets` imports if they use relative paths.
6. Update CI workflow paths (e.g., `dotnet test tests/**/*.csproj`).
7. Build and run tests to verify nothing is broken.

### Acceptance Criteria

- [ ] `src/` directory exists in the repository root and contains source projects
- [ ] `tests/` directory exists in the repository root and contains test projects
- [ ] Solution file references are updated to the new paths
- [ ] CI pipeline builds and tests pass with the new structure

### References

- https://learn.microsoft.com/en-us/dotnet/core/porting/project-structure
- https://github.com/dotnet/aspnetcore (example of src/tests structure)
- https://gist.github.com/davidfowl/ed7564297c61fe9ab814 (David Fowler's .NET project structure guide)
