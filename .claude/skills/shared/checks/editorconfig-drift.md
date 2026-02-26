---
name: EditorConfig Drift
slug: editorconfig-drift
tier: 3
tier_label: Nice to Have
points: 1
scoring: normal
---

# EditorConfig Drift

## Verification

```bash
# Only run if .editorconfig exists (the tier 2 editorconfig check handles missing files)
gh api repos/{owner}/{repo}/contents/.editorconfig --jq '.content' 2>&1 || true
```

Then base64-decode the content and compare against the matching shared reference file in `../editorconfigs/` (select by detected tech stack).

### Pass Condition
Content matches the shared reference, OR no shared reference exists for the detected tech stack.

### Status Rules
- **PASS**: Content matches the shared reference for the detected tech stack
- **FAIL**: Content differs from the shared reference
- **SKIP** (don't run): If no .editorconfig exists in the repository

## Backlog Content

### What's Missing
The repository's .editorconfig differs from the shared reference for the detected tech stack.

### Why It Matters
When an .editorconfig drifts from the team standard, different repos end up with inconsistent formatting rules. This makes context-switching between projects harder and can cause unnecessary formatting changes in PRs.

### Quick Fix
```bash
cp {skills-path}/shared/editorconfigs/{stack}.editorconfig .editorconfig
```

### Full Solution
1. Download the repo's current .editorconfig and compare against the matching shared reference.
2. Review the diff -- the repo may have intentional customizations.
3. If differences are unintentional drift (inconsistent indentation, missing sections), replace with shared reference.
4. If the repo has legitimate project-specific overrides, merge them into the shared reference as additional sections, keeping the shared base intact.

Tech stack detection:

| Indicator | Reference |
|-----------|-----------|
| .csproj, .sln | dotnet.editorconfig |
| package.json, tsconfig.json | javascript.editorconfig |
| pyproject.toml, setup.py | python.editorconfig |
| Cargo.toml | rust.editorconfig |
| go.mod | go.editorconfig |

### Acceptance Criteria
- [ ] .editorconfig content matches the shared reference
- [ ] Any project-specific overrides are documented with comments

### Notes
This check only runs if .editorconfig already exists. The shared references live in `.claude/skills/shared/editorconfigs/`. When the repo has customizations to preserve, add them as additional sections after the shared base.

### References
- https://editorconfig.org
