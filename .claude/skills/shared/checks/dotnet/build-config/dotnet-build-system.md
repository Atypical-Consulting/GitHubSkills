---
name: Build System
slug: dotnet-build-system
tier: 3
tier_label: Nice to Have
points: 0
scoring: info
---

# Build System

## Verification

```bash
echo "=== NUKE ===" && (gh api repos/{owner}/{repo}/contents/.nuke --jq '.[] | .name' 2>&1 || true)
echo "=== CAKE ===" && (gh api repos/{owner}/{repo}/contents/build.cake --jq '.size' 2>&1 || true)
echo "=== FAKE ===" && (gh api repos/{owner}/{repo}/contents/build.fsx --jq '.size' 2>&1 || true)
echo "=== NUKE BUILD CS ===" && (gh api repos/{owner}/{repo}/contents/build/Build.cs --jq '.size' 2>&1 || true)
```

### Pass Condition

Reports which .NET build system (if any) is detected in the repository.

### Status Rules

- **INFO**: Reports the detected build system:
  - **NUKE** if `.nuke/` directory exists or `build/Build.cs` is present
  - **Cake** if `build.cake` exists
  - **FAKE** if `build.fsx` exists
  - **None detected** if no build system markers are found

## Backlog Content

Use the content below when generating the backlog item for an INFO result.

### What's Missing

No dedicated .NET build system (NUKE, Cake, or FAKE) was detected in the repository.

### Why It Matters

A dedicated build system provides a type-safe, versioned, and reproducible way to define build pipelines. While GitHub Actions YAML or plain `dotnet` CLI commands work for simple projects, larger solutions benefit from a build system that can orchestrate multi-step builds, manage cross-project dependencies, generate release notes, publish packages, and run locally with the same behavior as CI. Build systems also reduce vendor lock-in to a specific CI provider.

### Quick Fix

```bash
# Install NUKE (most popular modern .NET build system)
dotnet tool install Nuke.GlobalTool --global
nuke :setup
```

### Full Solution

1. Choose a build system based on project needs:

   | System | Language | Best For |
   |--------|----------|----------|
   | **NUKE** | C# | Type-safe builds, IDE integration, large solutions |
   | **Cake** | C# (DSL) | Familiar scripting style, rich plugin ecosystem |
   | **FAKE** | F# | F# teams, functional build pipelines |

2. For NUKE (recommended for most projects):
   ```bash
   dotnet tool install Nuke.GlobalTool --global
   nuke :setup
   ```
   This scaffolds a `build/` directory with a `Build.cs` file and a `.nuke/` configuration directory.

3. Define build targets (compile, test, pack, publish) in the build project.
4. Update CI to invoke the build system instead of raw `dotnet` commands.

### Acceptance Criteria

- [ ] A build system configuration exists in the repository (any of: `.nuke/`, `build.cake`, `build.fsx`)

### Notes

This is an **INFO-only check**. It carries no points and no penalty. Many projects work perfectly well with plain `dotnet` CLI commands in CI. A dedicated build system is most valuable for multi-project solutions with complex build pipelines, package publishing, or cross-platform build requirements.

### References

- https://nuke.build/
- https://cakebuild.net/
- https://fake.build/
