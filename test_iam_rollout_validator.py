"""
Single-file tests for iam_rollout_validator.py

Goal:
- Keep tests small and readable.
- Prove the validator catches the most common mistake: wrong group name.
"""

import iam_rollout_validator as v


def test_unknown_group_is_reported():
    cfg = {
        "apps": [{"id": "jira", "name": "Jira", "saml": True, "sensitive": False}],
        "groups": [{"id": "engineering", "description": "Engineering users"}],
        "assignments": [{"app": "jira", "groups": ["engineers"]}],  # typo / wrong group
        "policies": [],
    }

    problems = v.validate(cfg)

    assert any("unknown group" in p.lower() for p in problems)
