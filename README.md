# JetFuelBurn

[![PyPI Downloads](https://img.shields.io/pypi/dm/jetfuelburn?label=PyPI%20Downloads&logo=pypi&logoColor=white)](https://pypi.org/project/jetfuelburn/)
[![License: MIT](https://img.shields.io/pypi/l/jetfuelburn?label=License&logo=open-source-initiative&logoColor=white)](https://pypi.org/project/jetfuelburn/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/jetfuelburn?logo=python&logoColor=white)](https://pypi.org/project/jetfuelburn/)

A Python package for calculating fuel burn of commercial aircraft.  
Maintainance Team: [@michaelweinold](https://github.com/michaelweinold)

## Installation

See [the package documentation](https://jetfuelburn.readthedocs.io/) for installation instructions.

## Development

### Documentation

The package documentation is based on [`mkdocs`](https://www.mkdocs.org). To build the documentation locally, install required packages from the `docs/_requirements.txt` file and navigate to the package root directory to execute:

```bash
mkdocs serve
```

### Testing

Package tests are based on [`pytest`](https://docs.pytest.org/en/stable/). To run all tests, navigate to the package root directory and execute:

```bash
pytest
```

When developing with Visual Studio Code, test can also be run from [the Test Explorer sidebar](https://code.visualstudio.com/docs/python/testing).

### CI/CD

The package uses [GitHub Actions](https://github.com/features/actions) for continuous integration and deployment. The CI/CD pipeline is defined in the `.github/workflows` directory.

| Workflow | Description | Trigger |
|----------|-------------|---------|
| `.github/workflows/test_package.yml` | Runs all tests. | Every new pull request and push to the `main` branch. |
| `.github/workflows/publish_testpypi.yml` | Runs all tests and uploads the package to TestPyPI. | Every new version `tag`. |
| `.github/workflows/publish_pypi.yml` | Runs all tests and uploads the package to PyPI. | Every new version `release`. |