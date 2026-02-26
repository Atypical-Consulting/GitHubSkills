# LICENSE

| Field | Value |
|-------|-------|
| **Repository** | `phmatray/BelgiumVatChecker` |
| **Source** | Health Check |
| **Tier** | 1 — Required |
| **Points** | 4 |
| **Status** | FAIL |
| **Detected** | 2026-02-26 |

## What's Missing

No LICENSE file exists in the repository.

## Why It Matters

Without a license, the project is technically "all rights reserved" by default, meaning no one can legally use, modify, or distribute the code. For an open-source .NET library, this discourages contributions and adoption.

## How to Fix

### Quick Fix

```bash
gh api repos/phmatray/BelgiumVatChecker/license # confirm missing
# Then add a LICENSE file — MIT is common for .NET projects:
curl -o LICENSE https://choosealicense.com/licenses/mit/
```

### Full Solution

Create a `LICENSE` file in the repository root. For a .NET Web API project, MIT or Apache-2.0 are common choices. Replace `[year]` and `[fullname]` with appropriate values:

```
MIT License

Copyright (c) 2026 phmatray

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Acceptance Criteria

- [ ] A LICENSE file exists in the repository root
- [ ] GitHub recognizes it as a valid license (shown in repo sidebar)

## References

- https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/licensing-a-repository
- https://choosealicense.com/
