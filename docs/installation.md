# Installation

You can install `jetfuelburn` from [PyPi](https://pypi.org) using `pip`:

```bash
pip install jetfuelburn
```

!!! info "[![PyPI Wheel Size](https://img.shields.io/badge/dynamic/json?url=https%3A%2F%2Fpypi.org%2Fpypi%2Fjetfuelburn%2Fjson&query=%24.urls%5B0%5D.size&label=PyPI%20Wheel%20Size&suffix=%20B&logo=pypi&logoColor=white)](https://pypi.org/project/jetfuelburn/)"

    The core version of `jetfuelburn` only depends on the [Pint](https://pint.readthedocs.io/en/stable/) library and therefore has only one top-level dependency. This makes `jetfuelburn` well-suited for WebAssembly Python environments [like Pyodide](https://pyodide.org/en/stable/usage/loading-packages.html) that work best with small package file-size. 

!!! warning

    If you want to use the modules:
    
    - [`jetfuelburn.utility.mapping`](api/mapping.md)
    - [`jetfuelburn.utility.ofp`](api/ofp.md)
    
    you need to install it including all optional dependencies:

    ```bash
    pip install jetfuelburn[optionaldependencies]
    ```