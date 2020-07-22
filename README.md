# e2e.common

Common code for the Python E2E package ecosystem.

This package complies with PEP-484, PEP-526, and PEP-561 for distribution of
type information.

## Core Modules

### `e2e.common.modelling`: Object-based Modelling Framework

A modelling framework is provided by `modelling.NamedParentable`, using
metaclass construction to stitch instance parents together in a class-based
modelling approach.

For examples on how this is used, please see
[e2e.pom](https://github.com/nickroeker/e2e.pom) or
[e2e.api](https://github.com/nickroeker/e2e.api), as both packages use this
modelling approach as of their 1.x releases.

For the 1.0 release, only `NamedParentable` is provided and requires users to
explicitly name instances of models for best-possible human-friendly logging.

For the 2.0 release, options will exist for auto-naming and omission of the
naming requirement. Stay tuned.

### `e2e.common.utils`: General Utility Functions

Generalised utility functions reside in here. To reside here, they must be used
by more than one e2e.* package.

## Compatibility

**Python 3.6+ is required** due to various metaclass and type-hinting
functinality used. Backporting to 3.5 is possible with more significant effort
and potential loss of certain features and type-hinting; please file an issue
if you require this, explaining the motivation if possible.

Other than that, this is a pure Python package and should be compatible with
any OS and platform which Python runs on.

## Contributing & Development

I haven't put much thought into others contributing here. Please reach out if
there are changes you'd like to make!

The `Makefile` (which has only been tested on Linux distros) holds my
development process:

* `make format`: to run `black` and `isort` formatters
* `make lint`: to run `mypy` (type check), `pylint`, and `flake8`
* `make test`: to run unit tests
* `make tox`: to run unit tests on multiple Python versions
* `make wheel` and `make sdist`: to build such package archives

Otherwise, this is a fairly standard package repo using virtual environments
and `setup.py`.

Note that the build environment (no unnecessary packages) is different from the
development environment (contains all packages for development).
