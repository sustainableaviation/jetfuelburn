# Installation

!!! info

    The core version of `jetfuelburn` only depends on the [Pint](https://pint.readthedocs.io/en/stable/) library and therefore has only one top-level dependency. This makes `jetfuelburn` well-suited for WebAssembly Python environments [like Pyodide](https://pyodide.org/en/stable/usage/loading-packages.html) that work best with small package file-size. 

You can install `jetfuelburn` from [PyPI](https://pypi.org) using your preferred package manager:

=== "pip"

    ```bash
    pip install jetfuelburn
    ```

=== "uv"

    To add the package to the current project:

    ```bash
    uv add jetfuelburn
    ```

    To install the package into an existing environment:

    ```bash
    uv pip install jetfuelburn
    ```

!!! warning

    If you want to use the modules:
    
    - [`jetfuelburn.utility.mapping`](api/mapping.md)
    - [`jetfuelburn.utility.ofp`](api/ofp.md)
    
    you need to install it including all optional dependencies:

    === "pip"

        ```bash
        pip install jetfuelburn[optionaldependencies]
        ```

    === "uv"

        ```bash
        uv add "jetfuelburn[optionaldependencies]"
        ```

        or

        ```bash
        uv pip install "jetfuelburn[optionaldependencies]"
        ```
