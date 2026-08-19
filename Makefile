## Makefile (repo-owned)
# Keep this file small. It can be edited without breaking template sync.

# Override template default: include mkdocstrings plugin for API docs
MKDOCS_EXTRA_PACKAGES = --with 'mkdocstrings[python]'

# Lock the coverage floor to the achieved 100% (template default is 90).
COVERAGE_FAIL_UNDER = 100

# Always include the Rhiza API (template-managed)
include .rhiza/rhiza.mk

# ---------------------------------------------------------------------------
# Run the hooks with prek instead of pre-commit.
#
# prek is a drop-in reimplementation of pre-commit in Rust: it reads the same
# .pre-commit-config.yaml, so that file stays exactly as the template ships it
# and every hook keeps its upstream `rev`. All 20 hooks pass unchanged.
#
# These overrides live here rather than in .rhiza/make.d/ because both callers
# of pre-commit (`fmt` in quality.mk, the hook install in python.mk) are
# template-owned and would be reverted by the next `make rhiza-update`. The
# root Makefile is repo-owned and is read after `include .rhiza/rhiza.mk`
# (which globs .rhiza/make.d/*.mk at its end), so a target redefined here is
# the last definition GNU Make sees and therefore the one that wins.
#
# Deliberately no `## ...` help comment: `make help` and the README block that
# the update-readme-help hook regenerates are built by awk over the raw text of
# MAKEFILE_LIST, so annotating these would list `fmt` and `post-install` twice.
#
# Note for CI: rhiza's reusable workflow runs this gate as plain `make fmt`, so
# CI picks prek up automatically. Its cache step still keys on
# ~/.cache/pre-commit, which prek does not use (it caches in ~/.cache/prek), so
# hook environments are rebuilt on every run until that moves upstream.
# ---------------------------------------------------------------------------

# A second, optional config for hooks the template does not own.
#
# .pre-commit-config.yaml is template-owned, so hooks added there are lost on the
# next rhiza-update. This file is invisible to the template (it is not in
# .rhiza/template.lock), so it survives. Commit it for repo-local hooks, or keep
# it out of the index via .git/info/exclude for personal ones -- .gitignore is
# itself template-owned and would be reverted.
#
# prek merges nothing: recognised config filenames are prek.toml,
# .pre-commit-config.yaml and .pre-commit-config.yml, and only one is read per
# directory. So this is a genuinely separate config, run as a second pass. It
# does get the full repo-wide file list, unlike prek's workspace mode, where a
# nested config only ever sees files beneath its own directory.
#
# Consequences of it being a separate run, not a merge:
#   - Top-level settings are NOT inherited. A node or python hook here needs its
#     own `default_language_version` pin.
#   - `prek install` bakes a single --config into .git/hooks/pre-commit, and
#     there is only one such shim, so these hooks deliberately do NOT run on
#     commit -- only via `make fmt` and CI. Do not point post-install at this
#     file: that would silently stop the template's hooks from running on commit.
PREK_EXTRA_CONFIG ?= .pre-commit-extra.yaml

# Both passes always run and the target fails if either did, rather than make
# aborting after the first: a failure in the template hooks must not hide one in
# the local hooks.
fmt: install-uv
	@rc=0; \
	${UVX_BIN} -p ${PYTHON_VERSION} prek run --all-files || rc=1; \
	if [ -f "${PREK_EXTRA_CONFIG}" ]; then \
	  printf "${BLUE}[INFO] Running local hooks from ${PREK_EXTRA_CONFIG}...${RESET}\n"; \
	  ${UVX_BIN} -p ${PYTHON_VERSION} prek run --all-files --config ${PREK_EXTRA_CONFIG} || rc=1; \
	fi; \
	exit $$rc

# Replace the pre-commit shim that the template's `install` target writes just
# before it calls post-install. --force is required precisely because that shim
# is already in place; without it prek declines to overwrite a foreign hook.
# The core.hooksPath guard mirrors the template's: with an external hook manager
# in charge, prek refuses to install, and that is not an error worth failing on.
post-install::
	@if [ -f ".pre-commit-config.yaml" ]; then \
	  if [ -n "$$(git config --get core.hooksPath 2>/dev/null)" ]; then \
	    printf "${BLUE}[INFO] Skipping prek hook install: core.hooksPath is set${RESET}\n"; \
	  else \
	    printf "${BLUE}[INFO] Installing prek hooks...${RESET}\n"; \
	    ${UVX_BIN} -p ${PYTHON_VERSION} prek install --force || { printf "${YELLOW}[WARN] Failed to install prek hooks${RESET}\n"; }; \
	  fi; \
	fi

# Optional: developer-local extensions (not committed)
-include local.mk
