---
name: Benchmark Project
slug: dotnet-benchmarks
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# Benchmark Project

## Verification

```bash
BENCH_CSPROJS=$(gh api repos/{owner}/{repo}/git/trees/HEAD --jq '.tree[].path' 2>&1 | grep -iE 'benchmark.*\.csproj$')
if [ -n "$BENCH_CSPROJS" ]; then
  echo 'BENCHMARK_PROJECT_FOUND'
else
  # Fallback: search all .csproj for BenchmarkDotNet reference
  ALL_CSPROJS=$(gh api repos/{owner}/{repo}/git/trees/HEAD --jq '.tree[].path' 2>&1 | grep -iE '\.csproj$')
  FOUND=false
  for csproj in $ALL_CSPROJS; do
    CONTENT=$(gh api repos/{owner}/{repo}/contents/$csproj --jq '.content' 2>&1 | base64 -d 2>/dev/null)
    if echo "$CONTENT" | grep -qi 'BenchmarkDotNet'; then
      FOUND=true
      break
    fi
  done
  if [ "$FOUND" = true ]; then
    echo 'BENCHMARK_PROJECT_FOUND'
  else
    echo 'NOT_FOUND'
  fi
fi
```

### Pass Condition

A BenchmarkDotNet project exists, either as a project with `Benchmark` in its name or any project referencing the `BenchmarkDotNet` package.

### Status Rules

- **PASS**: Benchmark project found (`BENCHMARK_PROJECT_FOUND`)
- **FAIL**: No benchmark project or BenchmarkDotNet reference found (`NOT_FOUND`)

## Backlog Content

Use the content below when generating the backlog item file for a FAIL result.

### What's Missing

No BenchmarkDotNet project exists in the repository. There are no `.csproj` files with `Benchmark` in their name and no references to the `BenchmarkDotNet` package.

### Why It Matters

Performance regressions are hard to detect without a benchmark suite. BenchmarkDotNet provides statistically rigorous micro-benchmarks that can track throughput, memory allocations, and GC pressure over time. Having benchmarks in the repository makes it easy for contributors to measure the impact of changes on hot paths and prevents accidental performance degradation.

### Quick Fix

```bash
dotnet new console -n MyProject.Benchmarks -o benchmarks/MyProject.Benchmarks
cd benchmarks/MyProject.Benchmarks
dotnet add package BenchmarkDotNet
dotnet add reference ../../src/MyProject/MyProject.csproj
```

### Full Solution

1. Create a benchmark console project:
   ```bash
   dotnet new console -n <ProjectName>.Benchmarks -o benchmarks/<ProjectName>.Benchmarks
   ```
2. Add the `BenchmarkDotNet` NuGet package.
3. Add a project reference to the library or application being benchmarked.
4. Write at least one benchmark class targeting a performance-critical method:
   ```csharp
   [MemoryDiagnoser]
   public class MyBenchmarks
   {
       [Benchmark]
       public void BenchmarkMethod() { /* ... */ }
   }
   ```
5. Add the benchmark project to the solution file.
6. Document how to run benchmarks in the README (e.g., `dotnet run -c Release --project benchmarks/`).

### Acceptance Criteria

- [ ] A benchmark project exists with a reference to `BenchmarkDotNet`
- [ ] At least one benchmark class with `[Benchmark]` methods is present
- [ ] The benchmark project is included in the solution file
- [ ] Benchmarks run successfully with `dotnet run -c Release`

### References

- https://benchmarkdotnet.org/articles/guides/getting-started.html
- https://learn.microsoft.com/en-us/dotnet/core/diagnostics/benchmarking
- https://github.com/dotnet/BenchmarkDotNet
