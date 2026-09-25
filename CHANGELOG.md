# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com),
and entries are generated from [Conventional Commits](https://www.conventionalcommits.org).

## [0.2.0] - 2026-09-25

### New Features
- Add ClusterFuzzLite fuzzing scaffold for shrinkage (#24)
- Re-export cov1para from package root (#38) (#42)

### Bug Fixes
- Address quality scorecard findings (#49-#52) (#53)
- Cov1para divide-by-zero warning, and the missing half of the API reference (#80)
- Align docs scope and decouple the intensity assertion (#86, #88) (#89)
- Raise ValueError for rank-deficient input to nonlinear_shrinkage (#110) (#116)

### Documentation
- Align advertised scope with shipped estimators (#41) (#44)
- Cite the 2004 JMVA paper consistently for cov1para (#81)
- Add CLAUDE.md (#101)
- Fix CLAUDE.md drift and drop the stale nonlinear .gitkeep (#112) (#115)

### Maintenance
- Chore(deps)(deps): bump the python-dependencies group with 3 updates (#22)
- Chore(deps)(deps): bump actions/checkout in the github-actions group (#23)
- Chore(deps)(deps): bump the github-actions group with 3 updates (#27)
- Chore(deps)(deps): bump the python-dependencies group with 2 updates (#26)
- Update rhiza to v1.0.0 (#37)
- Add hypothesis property + ill-conditioned cases for cov1para (#40) (#45)
- Update rhiza to v1.0.1 (#46)
- Chore(deps)(deps): bump the github-actions group with 12 updates (#48)
- Sync rhiza template (flatten tests, drop requirements/suppression utils)
- Sync rhiza template to v1.1.3 (#54)
- Chore(deps-dev)(deps-dev): bump ruff in the python-dependencies group (#55)
- Drop fuzzing, scorecard, and weekly workflows (#56)
- Update rhiza to v1.2.1 (#57)
- *(pyproject)* Modernize Python version and license metadata (#66)
- Chore(deps-dev)(deps-dev): bump the python-dependencies group across 1 directory with 2 updates (#65)
- Update rhiza to v1.2.5 (#68)
- Chore(deps)(deps): bump the github-actions group across 1 directory with 11 updates (#67)
- Update rhiza to v1.3.0 (#69)
- Move [tool.bumpversion] into pyproject.toml (#70)
- Run the hooks with prek instead of pre-commit (#71)
- Chore(deps)(deps): bump the github-actions group with 3 updates (#73)
- Drop the lint dependency group and pytest-cov (#74)
- Drop the `lint` dependency group and pytest-cov (#75)
- Update rhiza to v1.3.2 (#76)
- *(ci)* Bump the rhiza pin to v1.3.3 (#84)
- Update rhiza to v1.3.3 (#85)
- Chore(deps)(deps): bump the github-actions group with 2 updates (#83)
- Chore(deps-dev)(deps-dev): bump hypothesis (#82)
- Chore(deps-dev)(deps-dev): bump hypothesis (#90)
- Update rhiza to v1.3.4 (#91)
- Update rhiza to v1.4.2 (#92)
- Update rhiza to v1.4.2 (#95)
- Update rhiza to v1.5.0 (#96)
- Drop template-owned .github/workflows/rhiza_fuzzing.yml (#97)
- Remove the retired rhiza_mutation.yml (#99)
- Drop the exclude entries for the retired mutation/fuzzing workflows (#100)
- Update rhiza to v1.6.0 (#102)
- Chore(deps-dev)(deps-dev): bump hypothesis (#103)
- Update rhiza to v1.7.1 (#104)
- Update rhiza to v1.7.2 (#105)
- Update rhiza to v1.8.0 (#108)
- Derive the version from the git tag (#109)
- Chore(deps-dev)(deps-dev): bump hypothesis (#106)
- Share the demeaning step and strengthen doctests (#113) (#114)

### Other Changes
- Sync Rhiza template v0.19.3 → v0.19.4 (#21)
- Sync Rhiza template v0.19.4 → v0.19.6 (#25)
- Sync Rhiza template v0.19.6 → v0.19.9 (#28)
- Remove dead debug scratch file _cov1para_debug.py (#33)
- Expand README with install and usage example (#35)
- Deepen cov1para test suite with numerical and invariant assertions (#34)
- Remove unused polars dependency (#36)
- Mirror package `__init__` tests to the source layout (#59)
- Resolve open quality issues (#2, #39, #47, #60, #61, #62) (#63)
- Update paths in template.yml for workflow exclusions (#93)
- Update excluded workflows in template.yml (#94)
- Use thomas.schmelzer@gmail.com as author email (#98)

## [0.1.2] - 2026-06-17

### Maintenance
- Chore(deps)(deps): bump the python-dependencies group with 2 updates (#15)
- Chore(deps)(deps): bump the github-actions group with 9 updates (#16)
- Add Rhiza Claude commands (/rhiza_quality, /rhiza_update) (#17)
- Chore(deps)(deps): bump the python-dependencies group with 3 updates (#18)

### Other Changes
- Add 'Private :: Do Not Upload' classifier
- Sync Rhiza template v0.18.8 → v0.19.3 (#20)

## [0.1.1] - 2026-06-08

### New Features
- Add cvx-linalg dependency and implement cov1para
- Add tests for cov1para and consolidate linear module
- Add debug variant of cov1para linear shrinkage estimator

### Bug Fixes
- Remove pycache, add module docstrings, fix deptry config
- Allow uppercase math variable names in linear module and document test security exceptions
- Downgrade setup-uv from v8.1.0 to v7.6.0, bump rhiza ref to v0.15.3
- Add mkdocs.yml and docs/api.md to fix BOOK workflow
- Remove leading newline from .python-version
- Suppress N803/N806 ruff rules for linear shrinkage source files
- Add missing pyproject.toml metadata and update lock file
- Exclude debug file from coverage to restore 100% threshold

### Maintenance
- Chore(deps)(deps): bump github/codeql-action in the github-actions group
- Chore(deps)(deps): bump numpy
- Sync rhiza template files
- Sync rhiza template files
- Apply rhiza sync v0.17.0
- Apply rhiza sync v0.18.4
- Chore(deps)(deps): bump the github-actions group with 8 updates
- Chore(deps)(deps): bump polars in the python-dependencies group
- Chore(deps)(deps): bump the github-actions group with 9 updates
- Rhiza v0.18.8 — inline git auth, release guards, new tests (#14)

### Other Changes
- Initial commit
- Rhiza framework
- Add pyproject.toml and uv.lock
- Add configuration files, workflows, and documentation templates
- Add placeholder directories for linear and nonlinear shrinkage
- Merge pull request #1 from Jebel-Quant/dependabot/github_actions/github-actions-8abaa2cbc6
- Update pyproject.toml: single package, drop inline tool config
- Sync rhiza template to v0.10.6
- Merge pull request #3 from Jebel-Quant/dependabot/uv/python-dependencies-8cd47ffab5
- Merge pull request #4 from Jebel-Quant/profiles
- Rhiza version
- Update templates in template.yml
- Merge pull request #8 from Jebel-Quant/rhiza_v0.17.0
- Merge pull request #9 from Jebel-Quant/rhiza_v0.18.4
- Merge pull request #11 from Jebel-Quant/rhiza_v0.18.4
- Merge pull request #10 from Jebel-Quant/dependabot/github_actions/github-actions-f379237d3f
- Merge pull request #13 from Jebel-Quant/dependabot/uv/python-dependencies-cd0e3294a2
- Merge pull request #12 from Jebel-Quant/dependabot/github_actions/github-actions-74b91dd3f0
- Bump version 0.1.0 → 0.1.1

<!-- generated by git-cliff -->
