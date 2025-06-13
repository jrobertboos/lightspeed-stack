# CONTRIBUTING

<!-- the following line is used by tool to autogenerate Table of Content when the document is changed -->
<!-- vim-markdown-toc GFM -->

* [TLDR;](#tldr)
* [Setting up your development environment](#setting-up-your-development-environment)
* [Definition of Done](#definition-of-done)
    * [A deliverable is to be considered “done” when](#a-deliverable-is-to-be-considered-done-when)
* [Automation](#automation)
    * [Pre-commit hook settings](#pre-commit-hook-settings)
    * [Code coverage measurement](#code-coverage-measurement)
    * [Type hints checks](#type-hints-checks)
    * [Linters](#linters)
    * [Security checks](#security-checks)
* [Testing](#testing)
    * [Tips and hints for developing unit tests](#tips-and-hints-for-developing-unit-tests)
        * [Patching](#patching)
        * [Verifying that some exception is thrown](#verifying-that-some-exception-is-thrown)
        * [Checking what was printed and logged to stdout or stderr by the tested code](#checking-what-was-printed-and-logged-to-stdout-or-stderr-by-the-tested-code)
    * [Tips and hints for developing e2e tests](#tips-and-hints-for-developing-e2e-tests)
        * [Detecting which statements are called in real service](#detecting-which-statements-are-called-in-real-service)
* [Benchmarks](#benchmarks)
    * [Running benchmarks](#running-benchmarks)
    * [`pytest-benchmark` package](#pytest-benchmark-package)
    * [Basic usage of `benchmark` fixture](#basic-usage-of-benchmark-fixture)
    * [Combination of `benchmark` fixture with other fixtures](#combination-of-benchmark-fixture-with-other-fixtures)
    * [Example output from benchmarks](#example-output-from-benchmarks)
* [Updating Dependencies](#updating-dependencies)
* [Code style](#code-style)
    * [Docstrings style](#docstrings-style)
* [Adding a new provider/model](#adding-a-new-providermodel)

<!-- vim-markdown-toc -->

## TLDR;

1. Create your own fork of the repo
2. Make changes to the code in your fork
3. Run unit tests and integration tests
4. Check the code with linters
5. Submit PR from your fork to main branch of the project repo


## Prerequisities

- git
- Python 3.11, 3.12, or 3.13
- pip

The development requires at least [Python 3.11](https://docs.python.org/3/whatsnew/3.11.html) due to significant improvement on performance, optimizations which benefit modern ML, AI, LLM, NL stacks, and improved asynchronous processing capabilities. It is also possible to use Python 3.12 or Python 3.13.



### Tooling installation

1. `pip install --user pdm`
1. `pdm --version` -- should return no error



## Setting up your development environment

```bash
# clone your fork
git clone https://github.com/YOUR-GIT-PROFILE/lightspeed-stack.git

# move into the directory
cd lightspeed-stack

# setup your devel environment with pdm
pdm install -G dev

# Now you can run test commands trough make targets, or prefix the rest of commands with `pdm run`, eg. `pdm run make test`

# run unit tests
make unit-tests

# run integration tests
make integration-tests

# code formatting
# (this is also run automatically as part of pre-commit hook if configured)
make format

# code style and docstring style
# (this is also run automatically as part of pre-commit hook if configured)
make verify

# check type hints
# (this is also run automatically as part of pre-commit hook)
make check-types
```

Happy hacking!


## Automation

### Pre-commit hook settings

It is possible to run formatters and linters automatically for all commits. You just need
to copy file `hooks/pre-commit` into subdirectory `.git/hooks/`. It must be done manually
because the copied file is an executable script (so from GIT point of view it is unsafe
to enable it automatically).


### Type hints checks

It is possible to check if type hints added into the code are correct and whether assignments, function calls etc. use values of the right type. This check is invoked by following command:

```
make check-types
```

Please note that type hints check might be very slow on the first run.
Subsequent runs are much faster thanks to the cache that Mypy uses. This check
is part of a CI job that verifies sources.


### Linters

_Black_, _Ruff_, Pyright, and _Pylint_ tools are used as linters. There are a bunch of linter rules enabled for this repository. All of them are specified in `pyproject.toml`, such us in sections `[tool.ruff]` and `[tool.pylint."MESSAGES CONTROL"]`. Some specific rules can be disabled using `ignore` parameter (empty now).

List of all _Ruff_ rules recognized by Ruff can be retrieved by:


```
ruff linter
```

Description of all _Ruff_ rules are available on https://docs.astral.sh/ruff/rules/

Ruff rules can be disabled in source code (for given line or block) by using special `noqa` comment line. For example:

```python
# noqa: E501
```

List of all _Pylint_ rules can be retrieved by:

```
pylint --list-msgs
```

Description of all rules are available on https://pylint.readthedocs.io/en/latest/user_guide/checkers/features.html

To disable _Pylint_ rule in source code, the comment line in following format can be used:

```python
# pylint: disable=C0415
```



