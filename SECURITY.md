# Security reporting

Report a vulnerability privately through the affected repository's GitHub
**Security → Report a vulnerability** form. For this community repository use
[private vulnerability reporting](https://github.com/open-ott-play/.github/security/advisories/new).
For an application, follow its own SECURITY.md first. Do not put credentials,
private configuration, household addresses or exploitable details in a public issue.

Include the affected repository and commit, the impact, reproduction steps with
synthetic data, and any suggested mitigation. Keep original sensitive logs private;
provide a redacted sample. Maintainers coordinate a fix and disclosure through the
private report. If you exposed a credential publicly, revoke it promptly; deleting
the visible text does not remove copies from history.

This repository contains public profile assets and CI configuration. Its checks
validate that content and automation; they do not certify applications, deployed
devices or services elsewhere in the organization. Action references use immutable
commits; the vendored Scorecard action also pins its container digest and retains
its upstream license. Review changes to permissions, secrets and reusable workflow
references as code.
