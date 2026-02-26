#!/usr/bin/env python3
"""Calculate the health score for a backlog directory and output JSON.

Scans health/*.md files and reads SUMMARY.md to produce a comprehensive
score breakdown including tier-level detail and issue counts.

Usage:
  python calculate_score.py <path-to-backlog-dir>
  python calculate_score.py backlog/phmatray_NewSLN
  python calculate_score.py --help
"""

import json
import os
import re
import sys


# Tier labels used when the label is not found in the file itself
DEFAULT_TIER_LABELS = {
    1: "Required",
    2: "Recommended",
    3: "Nice to Have",
}


def print_help():
    print(__doc__.strip())
    print()
    print("Arguments:")
    print("  <dir>     Path to a backlog directory (containing SUMMARY.md and health/)")
    print("  --help    Show this help message")


def parse_metadata_table(text):
    """Extract key-value pairs from a markdown metadata table."""
    metadata = {}
    for match in re.finditer(
        r"^\|\s*\*\*(.+?)\*\*\s*\|\s*(.+?)\s*\|", text, re.MULTILINE
    ):
        key = match.group(1).strip()
        value = match.group(2).strip().strip("`")
        metadata[key] = value
    return metadata


def parse_tier_value(value):
    """Parse tier number from value like '1 — Required'."""
    match = re.match(r"(\d+)", value)
    if match:
        return int(match.group(1))
    return 0


def scan_health_files(health_dir):
    """Scan health directory for tier-*.md files and parse each one.

    Returns a list of dicts with: tier, points, status, title, filename.
    """
    items = []
    if not os.path.isdir(health_dir):
        return items

    for filename in sorted(os.listdir(health_dir)):
        if not filename.endswith(".md"):
            continue
        if not re.match(r"tier-\d+--", filename):
            continue

        filepath = os.path.join(health_dir, filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()
        except IOError:
            continue

        metadata = parse_metadata_table(text)

        # Extract title from H1
        title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else filename

        tier = parse_tier_value(metadata.get("Tier", "0"))
        try:
            points = int(metadata.get("Points", "0"))
        except ValueError:
            points = 0
        status = metadata.get("Status", "").upper()

        items.append({
            "tier": tier,
            "points": points,
            "status": status,
            "title": title,
            "filename": filename,
        })

    return items


def parse_summary(summary_path):
    """Parse SUMMARY.md to extract repository name, scan date, passing checks,
    action items table, and issue information.
    """
    result = {
        "repository": "",
        "scan_date": "",
        "action_items": [],
        "passing_checks": [],
        "issues_text": "",
    }

    if not os.path.isfile(summary_path):
        return result

    try:
        with open(summary_path, "r", encoding="utf-8") as f:
            text = f.read()
    except IOError:
        return result

    # Extract repository from H1: "# Repo Scan: owner/repo"
    h1_match = re.search(r"^#\s+Repo Scan:\s*(.+)$", text, re.MULTILINE)
    if h1_match:
        result["repository"] = h1_match.group(1).strip()

    # Extract scan date from "> Generated: YYYY-MM-DD"
    date_match = re.search(r">\s*Generated:\s*(\S+)", text)
    if date_match:
        result["scan_date"] = date_match.group(1).strip()

    # Parse the action items table for all items (including PASS items in the table)
    # Format: | # | [Name](path) | Tier | Points | Status |
    # or:     | # | [Name](path) | Tier | Points | Status — [PR #N](url) |
    for match in re.finditer(
        r"^\|\s*\d+\s*\|\s*\[(.+?)\]\((.+?)\)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(.+?)\s*\|",
        text,
        re.MULTILINE,
    ):
        name = match.group(1).strip()
        path = match.group(2).strip()
        tier = int(match.group(3))
        points = int(match.group(4))
        # Status may contain extra info like "PASS — [PR #12](url)"
        status_raw = match.group(5).strip()
        # Extract the core status
        status_core = re.match(r"(PASS|FAIL|WARN)", status_raw)
        status = status_core.group(1) if status_core else status_raw

        pr_url = ""
        pr_match = re.search(r"\[PR #\d+\]\((.+?)\)", status_raw)
        if pr_match:
            pr_url = pr_match.group(1)

        result["action_items"].append({
            "name": name,
            "path": path,
            "tier": tier,
            "points": points,
            "status": status,
            "pr_url": pr_url,
        })

    # Parse passing checks section
    # Lines like: - **README** — Found (1,977 bytes)
    passing_section = ""
    passing_match = re.search(
        r"^##\s+Health\s+.+Passing Checks\s*\n(.*?)(?=^##\s+|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if passing_match:
        passing_section = passing_match.group(1)

    for match in re.finditer(r"^-\s+\*\*(.+?)\*\*", passing_section, re.MULTILINE):
        result["passing_checks"].append(match.group(1).strip())

    # Parse issues section
    issues_match = re.search(
        r"^##\s+Open Issues\s*\n(.*?)(?=^##\s+|\Z)",
        text,
        re.MULTILINE | re.DOTALL,
    )
    if issues_match:
        result["issues_text"] = issues_match.group(1).strip()

    return result


def count_issues(backlog_dir, issues_text):
    """Count issue items from the issues/ subdirectory and summary text."""
    issues_dir = os.path.join(backlog_dir, "issues")
    total = 0
    open_count = 0
    pr_created = 0
    closed = 0

    if os.path.isdir(issues_dir):
        for filename in os.listdir(issues_dir):
            if not filename.endswith(".md"):
                continue
            if not re.match(r"issue-\d+--", filename):
                continue

            total += 1
            filepath = os.path.join(issues_dir, filename)
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    text = f.read()
            except IOError:
                open_count += 1
                continue

            metadata = parse_metadata_table(text)
            status = metadata.get("Status", "OPEN").upper()
            if status == "CLOSED":
                closed += 1
            elif "PR" in status:
                pr_created += 1
            else:
                open_count += 1

    return {
        "total": total,
        "open": open_count,
        "pr_created": pr_created,
        "closed": closed,
    }


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("--help", "-h"):
        print_help()
        sys.exit(0 if "--help" in sys.argv or "-h" in sys.argv else 1)

    backlog_dir = sys.argv[1]

    if not os.path.isdir(backlog_dir):
        print(
            "Error: Directory not found: {}".format(backlog_dir), file=sys.stderr
        )
        sys.exit(1)

    health_dir = os.path.join(backlog_dir, "health")
    summary_path = os.path.join(backlog_dir, "SUMMARY.md")

    # Parse SUMMARY.md for the full picture
    summary = parse_summary(summary_path)
    repository = summary["repository"]
    scan_date = summary["scan_date"]

    # Build the unified item list from the SUMMARY action items table
    # This is the authoritative source: it includes ALL items (PASS, FAIL, WARN)
    # The individual health files only exist for items that were created as backlog
    all_items = summary["action_items"]

    # If no summary action items, fall back to scanning health files directly
    if not all_items:
        health_items = scan_health_files(health_dir)
        for item in health_items:
            all_items.append({
                "name": item["title"],
                "tier": item["tier"],
                "points": item["points"],
                "status": item["status"],
                "path": "",
                "pr_url": "",
            })

    # Also account for passing checks listed in SUMMARY that are NOT in the
    # action items table (these are items that passed without needing a file)
    # We need to figure out their tier and points. Use known defaults.
    KNOWN_CHECK_DEFAULTS = {
        "README": {"tier": 1, "points": 4},
        "LICENSE": {"tier": 1, "points": 4},
        "Description": {"tier": 1, "points": 4},
        ".gitignore": {"tier": 2, "points": 2},
        "Topics": {"tier": 2, "points": 2},
        "CI/CD workflows": {"tier": 2, "points": 2},
        "CI/CD Workflows": {"tier": 2, "points": 2},
        "CI Workflow Health": {"tier": 2, "points": 2},
        "CI workflow health": {"tier": 2, "points": 2},
        ".editorconfig": {"tier": 2, "points": 2},
        "Issue templates": {"tier": 2, "points": 2},
        "Issue Templates": {"tier": 2, "points": 2},
        "CODEOWNERS": {"tier": 2, "points": 2},
        "PR Template": {"tier": 2, "points": 2},
        "SECURITY.md": {"tier": 3, "points": 1},
        "CONTRIBUTING.md": {"tier": 3, "points": 1},
        "Security Alerts": {"tier": 3, "points": 1},
        ".editorconfig Drift": {"tier": 3, "points": 1},
        "EditorConfig Drift": {"tier": 3, "points": 1},
    }

    # Collect names already in action items (case-insensitive match)
    action_item_names = set()
    for item in all_items:
        action_item_names.add(item["name"].lower())

    # Add passing checks that aren't in the action items table
    for check_name in summary["passing_checks"]:
        if check_name.lower() not in action_item_names:
            defaults = KNOWN_CHECK_DEFAULTS.get(check_name, {"tier": 0, "points": 0})
            all_items.append({
                "name": check_name,
                "tier": defaults["tier"],
                "points": defaults["points"],
                "status": "PASS",
                "path": "",
                "pr_url": "",
            })

    # Calculate scores
    tier_data = {}
    total_earned = 0
    total_possible = 0
    count_pass = 0
    count_fail = 0
    count_warn = 0
    total_items = len(all_items)

    for item in all_items:
        tier = item["tier"]
        points = item["points"]
        status = item["status"].upper()

        if tier not in tier_data:
            tier_data[tier] = {
                "earned": 0,
                "possible": 0,
                "label": DEFAULT_TIER_LABELS.get(tier, "Unknown"),
            }

        tier_data[tier]["possible"] += points
        total_possible += points

        if status == "PASS":
            tier_data[tier]["earned"] += points
            total_earned += points
            count_pass += 1
        elif status == "WARN":
            count_warn += 1
        else:
            count_fail += 1

    # Calculate percentage (avoid division by zero)
    percentage = round(total_earned * 100 / total_possible) if total_possible > 0 else 0

    # Count issues
    issues = count_issues(backlog_dir, summary["issues_text"])

    # Build tier output (sorted by tier number)
    tiers_output = {}
    for tier_num in sorted(tier_data.keys()):
        tiers_output[str(tier_num)] = tier_data[tier_num]

    output = {
        "repository": repository,
        "scan_date": scan_date,
        "score": {
            "earned": total_earned,
            "possible": total_possible,
            "percentage": percentage,
        },
        "tiers": tiers_output,
        "items": {
            "total": total_items,
            "pass": count_pass,
            "fail": count_fail,
            "warn": count_warn,
        },
        "issues": issues,
    }

    json.dump(output, sys.stdout, indent=2, ensure_ascii=False)
    print()  # trailing newline


if __name__ == "__main__":
    main()
