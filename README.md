# iam-rollout-validator
IAM Rollout Validator is a small Python CLI tool that checks IAM rollout configurations before they go live. It reads a set of YAML files that describe apps (SAML SSO), groups, assignments, and sign-on policies and then runs validation checks to catch common rollout issues like a user can’t access an app because they’re in the wrong group, the app is assigned to the wrong group, or a policy blocks access unexpectedly. It can also explain an access decision step-by-step (groups > app assignment > policy), using fully synthetic sample data.

## Run
Install dependencies:

- `python3 -m pip install pyyaml pytest`
Validate the sample config:

- `python3 iam_rollout_validator.py validate sample_config.yml`
- `python3 iam_rollout_validator.py explain sample_config.yml jira engineering`
Run tests:

- `python3 -m pytest -q`

Note: sample_config.yml includes an intentional mistake (wrong group name) to show the validator catching a real rollout issue.