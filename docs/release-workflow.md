# Community repository validation

This repository publishes an organization profile and stores CI automation. It
has no application package, release channel, deployment job or device runtime.
The policy in [`.release-policy.json`](../.release-policy.json) is
`validation-only`; the local release client rejects application release requests.

## Local checks

Install Python 3.12, Node.js, Bash and actionlint 1.7.12. Use an isolated Python
environment and the committed hash lock:

```sh
python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install --require-hashes --only-binary=:all: -r .github/requirements-validation.txt
python3 scripts/release.py check
python3 scripts/release.py doctor
```

The checker parses Python, JSON and YAML, checks shell and JavaScript syntax,
and runs actionlint. YAML tags are parsed without constructing custom objects
or resolving includes. Failures report paths and line numbers rather than
source configuration values. These are syntax and automation checks, not tests
of application or hardware behavior. The `doctor` command reports the local
validation-only policy and does not require a release environment.

## Hosted checks

[`quality-gate.yml`](../.github/workflows/quality-gate.yml) runs for pull requests,
merge-queue entries, main pushes, scheduled validation and manual requests. It
calls three workflows:

- `validate.yml`: hash-locked YAML parser, checksum-verified actionlint and the
  same local checks;
- `codeql.yml`: separate Python and GitHub Actions analysis, invoked through the
  quality gate so ordinary pull requests do not launch duplicate scans;
- `dependency-review.yml`: checks dependency changes on pull requests.

The final **CI gate** requires every called validation job to succeed. The
separate workflow-validation job also validates automation changes. Scorecard
reports supply-chain findings in GitHub Security; its reports are evidence,
not a separate product certification. Review reported findings and retain the
existing review requirements when changing these workflows.

The local release client is vendored from `victron-venus/venus-os-ci-toolkit`.
Its general client tests run in that toolkit. Keep repository-specific policy
and validation changes reviewed together; do not add artificial beta/RC tags
for this community profile. See [CONTRIBUTING.md](../CONTRIBUTING.md) and
[SECURITY.md](../SECURITY.md) for contribution and vulnerability reporting.
