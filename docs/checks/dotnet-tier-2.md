# .NET — Tier 2 — Recommended

Tier 2 .NET checks verify professional standards for well-maintained .NET solutions. Each check is worth **2 points**. There are 8 checks in this tier for a maximum of 16 points. These checks only run when a `.sln` file is detected.

## Nullable Reference Types

| Slug | Category | What it checks |
|------|----------|----------------|
| `dotnet-nullable` | Code Quality | `<Nullable>enable</Nullable>` is set in `Directory.Build.props` or all `.csproj` files |

Nullable reference types catch null-reference bugs at compile time. Enabling them project-wide eliminates an entire class of runtime errors.

---

## global.json SDK Pinning

| Slug | Category | What it checks |
|------|----------|----------------|
| `dotnet-global-json` | Build Config | A `global.json` file exists with an SDK version pin |

Pins the .NET SDK version for the solution, ensuring all developers and CI use the same SDK. Prevents "works on my machine" issues from SDK version differences.

---

## Code Coverage

| Slug | Category | What it checks |
|------|----------|----------------|
| `dotnet-code-coverage` | Testing | A coverage tool (coverlet) is referenced in test projects |

Code coverage measurement tracks which code paths are exercised by tests. Without it, you're guessing about test quality.

---

## Central Package Management

| Slug | Category | What it checks |
|------|----------|----------------|
| `dotnet-central-packages` | Build Config | A `Directory.Packages.props` file exists with `<ManagePackageVersionsCentrally>true</ManagePackageVersionsCentrally>` |

Centralizes NuGet package version management across all projects. Prevents version conflicts and makes upgrades a single-file change.

---

## XML Documentation

| Slug | Category | What it checks |
|------|----------|----------------|
| `dotnet-xml-docs` | Code Quality | `<GenerateDocumentationFile>true</GenerateDocumentationFile>` is enabled |

Generates XML documentation from `///` comments, enabling IntelliSense in consuming projects and documentation generation tools.

---

## NuGet Metadata

| Slug | Category | What it checks |
|------|----------|----------------|
| `dotnet-nuget-metadata` | Packaging | Projects intended for NuGet have `PackageId`, `Authors`, `Description`, and `PackageLicenseExpression` |

Complete NuGet metadata ensures packages are discoverable, properly attributed, and legally clear on NuGet.org.

---

## Solution Structure

| Slug | Category | What it checks |
|------|----------|----------------|
| `dotnet-solution-structure` | Build Config | The `.sln` file organizes projects into `src\` and `tests\` solution folders |

A well-organized solution structure makes it immediately clear where source projects and test projects live, improving navigation for new contributors.

---

## Implicit Usings

| Slug | Category | What it checks |
|------|----------|----------------|
| `dotnet-implicit-usings` | Code Quality | `<ImplicitUsings>enable</ImplicitUsings>` is set |

Implicit usings reduce boilerplate by automatically importing common namespaces (`System`, `System.Collections.Generic`, etc.). Keeps source files focused on actual logic.
