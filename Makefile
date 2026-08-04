## Makefile (repo-owned)
# Keep this file small. It can be edited without breaking template sync.

LOGO_FILE=.rhiza/assets/rhiza-logo.svg

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

fmt: install-uv
	@${UVX_BIN} -p ${PYTHON_VERSION} prek run --all-files

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
