#!/usr/bin/env python3
"""
IAM Rollout Validator

What it does:
- Reads a YAML file that describes apps, groups, assignments, and policies
- Prints a few common rollout problems (wrong/missing group, missing MFA policy, etc.)

Why YAML:
- In a real Okta rollout, these settings live in the admin UI.
- Here we represent the same ideas in a small config file so the tool is runnable.
"""

import argparse

import yaml


def load_config(path):
    """Load YAML config into a Python dictionary."""
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("Config root must be a YAML mapping (a dictionary).")

    return data


def index_by_id(items, name):
    """
    Turn a list like [{'id': 'jira', ...}, {'id': 'finance', ...}]
    into a dict like {'jira': {...}, 'finance': {...}}.
    """
    if items is None:
        return {}

    if not isinstance(items, list):
        raise ValueError(f"'{name}' must be a list.")

    out = {}
    for obj in items:
        if not isinstance(obj, dict) or "id" not in obj:
            raise ValueError(f"Each item in '{name}' must be a dict with an 'id'.")
        _id = obj["id"]
        if _id in out:
            raise ValueError(f"Duplicate id in '{name}': {_id}")
        out[_id] = obj
    return out


def validate(cfg):
    """
    Return a list of strings describing problems found.
    Keep it simple: if list is empty, config looks OK.
    """
    problems = []

    apps = index_by_id(cfg.get("apps"), "apps")
    groups = index_by_id(cfg.get("groups"), "groups")
    assignments = cfg.get("assignments", [])
    policies = cfg.get("policies", [])

    if not isinstance(assignments, list):
        raise ValueError("'assignments' must be a list.")
    if not isinstance(policies, list):
        raise ValueError("'policies' must be a list.")

    # 1) Assignments must reference real apps and real groups
    assigned_apps = set()

    for a in assignments:
        if not isinstance(a, dict):
            problems.append("ERROR: assignment must be a mapping (dict)")
            continue

        app_id = a.get("app")
        group_list = a.get("groups")

        if app_id not in apps:
            problems.append(f"ERROR: assignment references unknown app: {app_id}")
            continue

        if not isinstance(group_list, list):
            problems.append(f"ERROR: app '{app_id}' assignment has no groups list")
            continue

        assigned_apps.add(app_id)

        for g in group_list:
            if g not in groups:
                problems.append(f"ERROR: app '{app_id}' assignment references unknown group: {g}")

    # 2) Warn if an app has no assignment (nobody can access it)
    for app_id in apps:
        if app_id not in assigned_apps:
            problems.append(f"WARN: app '{app_id}' has no assignment (nobody can access it)")

    # 3) Sensitive apps should have at least one MFA policy targeting them
    mfa_apps = set()
    for p in policies:
        if not isinstance(p, dict):
            continue
        target_app = p.get("app")
        rule = p.get("rule", {})
        if isinstance(rule, dict) and rule.get("require_mfa") is True:
            mfa_apps.add(target_app)

    for app_id, app in apps.items():
        if app.get("sensitive") is True and app_id not in mfa_apps:
            problems.append(f"WARN: sensitive app '{app_id}' has no policy with require_mfa: true")

    return problems


def main():
    parser = argparse.ArgumentParser(description="Validate an IAM rollout YAML config.")
    parser.add_argument("config", help="Path to YAML config (e.g., sample_config.yml)")
    args = parser.parse_args()

    cfg = load_config(args.config)
    problems = validate(cfg)

    if not problems:
        print("OK: no issues found")
        return

    for line in problems:
        print(line)


if __name__ == "__main__":
    main()
