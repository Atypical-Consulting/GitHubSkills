# .NET — Tier 1 — Required

Tier 1 .NET checks verify the fundamental build and test infrastructure every .NET repository must have. Each check is worth **4 points**. These checks only run when a `.sln` file is detected in the repository root.

## Directory.Build.props

| Property | Value |
|----------|-------|
| Slug | `dotnet-build-props` |
| Category | Build Config |
| Points | 4 |

**What it checks:** A `Directory.Build.props` file exists in the repository root.

**Why it matters:** `Directory.Build.props` centralizes MSBuild properties across all projects in a solution. Without it, settings like `<LangVersion>`, `<Nullable>`, and `<ImplicitUsings>` must be duplicated in every `.csproj` file, leading to drift and inconsistency.

**How to fix:** Create a `Directory.Build.props` in the repo root with shared properties:
```xml
<Project>
  <PropertyGroup>
    <LangVersion>latest</LangVersion>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
  </PropertyGroup>
</Project>
```

---

## Test Project Exists

| Property | Value |
|----------|-------|
| Slug | `dotnet-tests-exist` |
| Category | Testing |
| Points | 4 |

**What it checks:** At least one test project exists (matching `*Tests*/*.csproj` or `*Test*/*.csproj` patterns).

**Why it matters:** Automated tests are the foundation of software quality. A .NET solution without test projects cannot verify correctness, making refactoring and upgrades risky.

**How to fix:** Create a test project using xUnit, NUnit, or MSTest:
```bash
dotnet new xunit -n MyProject.Tests
dotnet sln add MyProject.Tests/MyProject.Tests.csproj
```
