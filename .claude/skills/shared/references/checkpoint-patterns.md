# Checkpoint Patterns

Standardized human-in-the-loop interaction patterns for GHS skills. Use these typed checkpoints instead of ad-hoc `AskUserQuestion` calls to ensure consistent UX across all skills.

## Checkpoint Types

### 1. Verification Required
- **When:** After batch operations complete, before creating PRs, before merging
- **Prompt:** "Type 'approved' or describe issues"
- **Implementation:** Use AskUserQuestion with options: ["Approve", "Reject with feedback"]
- **Example:** After backlog-fix wave completes, show results and ask to proceed

### 2. Decision Required
- **When:** Multiple valid paths exist, ambiguous user intent
- **Prompt:** Present options with descriptions
- **Implementation:** Use AskUserQuestion with 2-4 options
- **Example:** "Which merge strategy?" → Squash / Rebase / Merge commit

### 3. Action Required
- **When:** User must do something external (grant permissions, configure settings)
- **Prompt:** Clear instruction + "Type 'done' when complete"
- **Implementation:** Use AskUserQuestion with options: ["Done", "Skip", "Cancel"]
- **Example:** "Please enable Issues on the repository, then confirm"

### 4. Confirmation Required (Destructive)
- **When:** Irreversible or high-impact actions (force push, delete branches, merge PRs, create releases)
- **Prompt:** Show exactly what will happen, ask explicit confirmation
- **Implementation:** Use AskUserQuestion with options: ["Confirm {action}", "Cancel"]
- **Example:** "Will merge 5 PRs and delete their branches. Confirm?"

## Standard Patterns

### Pre-Flight Check

Before mutation skills begin, validate prerequisites and show a summary:

```
Pre-flight: {skill-name}
  [PASS] gh authenticated
  [PASS] Repository: owner/repo
  [PASS] Project: [GHS] owner/repo
  [FAIL] Missing: project scope → run `gh auth refresh -s project`
```

### Batch Confirmation

For skills processing multiple items:

```
Plan: {N} items to process
| # | Item | Action |
|---|------|--------|
| 1 | ... | ... |

Proceed with all {N} items?
```

### Post-Action Summary

After mutation, show what happened before routing:

```
Summary:
  Applied: 3
  Failed: 1
  Skipped: 0

  → Next: /ghs-merge-prs owner/repo
```

## When to Use Each Type

| Scenario | Checkpoint Type | Skip in --auto mode? |
|----------|----------------|---------------------|
| Review batch plan | Verification | Yes |
| Choose merge strategy | Decision | Use default |
| Grant missing permissions | Action | No (block) |
| Merge PRs | Confirmation | No (always confirm) |
| Delete branches | Confirmation | No (always confirm) |
| Create release | Confirmation | No (always confirm) |
| Select items to process | Decision | Process all |

## Anti-Patterns

| Do NOT | Do Instead | Why |
|--------|-----------|-----|
| Ask yes/no with AskUserQuestion | Use typed checkpoint with specific options | Yes/no is ambiguous and doesn't capture nuance |
| Skip confirmation for destructive ops | Always use Confirmation Required | Irreversible actions need explicit consent |
| Block on permissions in --auto mode | Log warning and skip the item | Auto mode should handle what it can |
| Combine checkpoint types | One checkpoint, one purpose | Mixed checkpoints confuse the user |
