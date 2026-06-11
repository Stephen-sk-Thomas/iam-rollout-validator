# iam-rollout-validator
IAM Rollout Validator is a small Python CLI tool that checks IAM rollout configurations before they go live. It reads a set of YAML files that describe apps (SAML SSO), groups, assignments, and sign-on policies and then runs validation checks to catch common rollout issues like missing group references, inconsistent MFA requirements etc.
