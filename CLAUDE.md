# CLAUDE.md

Guidance for working in this repository.

## What this is

`shrinkage` — linear and nonlinear shrinkage estimators for covariance matrices,
following Ledoit and Wolf. Part of the
[jebel-quant](https://github.com/jebel-quant) ecosystem. `numpy` is the only
runtime dependency; the package takes arrays and returns arrays.

Two families under `src/shrinkage/`, each a subpackage that re-exports its one
estimator:

- `linear/cov1para.py` → `cov1para` — the single-parameter linear shrinkage
  towards a scaled identity.
- `nonlinear/qis.py` → `nonlinear_shrinkage` — quadratic-inverse-shrinkage, the
  nonlinear estimator. Note the module and the function are named differently on
  purpose: `qis` is the method, `nonlinear_shrinkage` the public name.
- `_validation.py` — the shared input checks both estimators run first.

The public API is flat and declared three times over, each level with its own
`__all__`: `shrinkage/__init__.py`, `shrinkage/linear/__init__.py`,
`shrinkage/nonlinear/__init__.py`. A new estimator goes in the matching
subpackage and is re-exported up both levels.

`src/shrinkage/nonlinear/.gitkeep` and `tests/resources/.gitkeep` are placeholders
holding otherwise-empty directories in git — leave them until there is real
content beside them.

## Ownership: locally owned vs Rhiza-managed

This repo syncs its dev infrastructure from the
[`jebel-quant/rhiza`](https://github.com/jebel-quant/rhiza) template. The pinned
version lives in `.rhiza/template.yml` (`ref:`), and `/rhiza:update` re-applies
the template. **The authoritative, machine-generated list of synced files is the
`files:` block of `.rhiza/template.lock`** — when in doubt, consult it. The split
below summarises it.

### Locally owned — edit these freely

- `src/` — the library source
- `tests/` — the test suite
- `pyproject.toml` — project metadata, dependency groups, tool config, and the
  `[tool.rhiza-task]` table that configures the gates
- `README.md`, `CHANGELOG.md`, `mkdocs.yml`, `CLAUDE.md`
- `.rhiza/template.yml` — the template pin and the `profiles:`/`templates:`
  selection. The one file under `.rhiza/` this repo owns.
- `local.mk` — repo-specific make targets. The `Makefile` `-include`s it, and the
  template deliberately does not ignore it.

### Rhiza-managed — do NOT edit in place; fix upstream

These are overwritten by the next sync. To change one, open a PR against
`jebel-quant/rhiza` (or exclude the path in `.rhiza/template.yml`), then re-sync:

- `.github/workflows/rhiza_*.yml` — all CI/CD workflows
- `.github/` scaffolding — `dependabot.yml`, `release.yml`, rulesets,
  `secret_scanning.yml`, `CONFIG.md`
- `Makefile` — a 71-line shim that pins `RHIZA_TASK` and forwards every unmatched
  target to that CLI. Nothing goes below it; the next sync overwrites whatever was
  appended. Repo targets belong in `local.mk`.
- `.pre-commit-config.yaml`, `ruff.toml`, `pytest.ini`, `.bandit`,
  `.editorconfig`, `.python-version`, `cliff.toml` — tooling config
- `LICENSE`, `SECURITY.md`, and the synced `docs/` pages

`SECURITY.md` in particular is synced here: an edit to it is drift the next sync
reverts, and the `check-managed-files` pre-commit hook refuses the commit.

This repo's `.rhiza/template.yml` has no `exclude:` key at all — it takes the
`github-project` profile plus `legal` as they come. Adding an exclusion means
adding the key back.

## Quality gates

Since rhiza v1.4 the gates are tasks in the pinned `rhiza-task` CLI rather than
synced make fragments. Run them as bare `make <target>` (the shim forwards to
`uvx rhiza-task <task>`) — never call `.venv/bin/...` directly. `make help` lists
every task the pinned CLI knows, plus anything `local.mk` adds.

- `make install` — create the venv and sync dependencies
- `make fmt` — the pre-commit hooks over all files
- `make typecheck` — `ty` **and** `mypy`, because `[tool.rhiza-task]` sets
  `typechecker = "both"`
- `make test` — the full pytest suite with the coverage gate
- `make coverage` — coverage measurement into `_tests/coverage.xml`
- `make docs-coverage` — interrogate docstring coverage
- `make deps` — deptry unused/missing dependency analysis
- `make security` — the bandit scan
- `make license` — fail on GPL/LGPL/AGPL
- `make rhiza-test` — the rhiza repository checks, from `pytest-rhiza==0.2.1`
- `make all` — the gate set CI runs

Do not reach for `make mutation`. The task still exists in the CLI, but rhiza
v1.5.0 stopped offering mutation testing (Jebel-Quant/rhiza#1492) and the recipe
drives a mutmut 2.x CLI that mutmut 3 removed.

## Conventions

- **Coverage must stay at 100%.** `[tool.rhiza-task]` sets
  `coverage-fail-under = 100`, above rhiza-task's default of 90. Set it there, not
  in `[tool.coverage.report]`, which the CLI outranks.
- Every public symbol needs a docstring; docstring coverage must stay at 100%.
- Estimators are pure functions of their inputs. Validation belongs in
  `_validation.py` and runs first — do not scatter shape or dtype checks into the
  numeric code.
- `pytest.ini` uses `--import-mode=importlib`, so tests do not rely on
  implicit-namespace imports. Keep the `tests/` mirror of the source layout
  intact rather than flattening it.
- The per-test timeout is 60s (`pytest-timeout`).
- Three markers are declared: `stress`, `property`, `kaleido`. Use them rather
  than inventing new ones.

## Test layout

Tests mirror the source **one file per source module**, including the `__init__`
files, which is what keeps the re-export chain honest:

```text
src/shrinkage/__init__.py            → tests/shrinkage/test___init__.py
src/shrinkage/_validation.py         → tests/shrinkage/test__validation.py
src/shrinkage/linear/__init__.py     → tests/shrinkage/linear/test___init__.py
src/shrinkage/linear/cov1para.py     → tests/shrinkage/linear/test_cov1para.py
src/shrinkage/nonlinear/__init__.py  → tests/shrinkage/nonlinear/test___init__.py
src/shrinkage/nonlinear/qis.py       → tests/shrinkage/nonlinear/test_qis.py
```

`tests/test_rhiza_packaging.py` is the repo-level exception. Shared fixtures live
in `tests/conftest.py`; `tests/resources/` is empty apart from its `.gitkeep`.

Because these are estimators, prefer properties over golden numbers where you
can: symmetry, positive-definiteness, and the limiting cases (shrinkage
intensity 0 and 1) survive a refactor in a way that a pinned matrix does not.
