# Contributing

For an application repository, follow its repository-specific contribution and
security instructions. This community repository maintains the public organization
profile, assets and CI automation. Send proposed changes through a pull request;
use issues for non-sensitive bugs or suggestions and [SECURITY.md](SECURITY.md)
for vulnerabilities.

Explain the visible or CI behavior being changed and how you checked it. Preview
profile Markdown and changed images. Keep household configuration, credentials,
service addresses and operational exports out of commits. Preserve third-party
copyright and license notices.

Install Python 3.12, Node.js, Bash and actionlint 1.7.12, then run:

```sh
python3 -m pip install --require-hashes --only-binary=:all: -r .github/requirements-validation.txt
bash scripts/ci.sh
```

CodeQL scans the automation and Python tooling; dependency review checks pull-request dependency changes.
CI and syntax checks are not application, browser or hardware acceptance tests.
When adding executable behavior, include a regression test of its observable
behavior and document any required tools. Review workflow permissions and use
full commit references for third-party actions.
