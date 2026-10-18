"""Point Pyodide installs of jetfuelburn at the build being documented.

Interactive fences request the bare project name, which micropip would resolve
to the newest release on PyPI. That release can differ from the code these
pages document: ``latest`` is built from ``main``, and a tagged version may be
built before its release reaches PyPI. So each build of the documentation
installs its own code:

- On Read the Docs, ``.readthedocs.yaml`` builds the wheel of the checkout into
  ``docs/_static/wheel/`` and ``READTHEDOCS_CANONICAL_URL`` names the version
  being built, so the requirement becomes the URL of that wheel.
- Elsewhere, such as ``zensical serve``, the requirement is pinned to
  ``__version__``.

A requirement with extras, such as ``jetfuelburn[optionaldependencies]``, is
always pinned to ``__version__``, because a wheel URL cannot carry extras.
"""

import logging
import os
import re
from pathlib import Path

from markdown.extensions import Extension
from markdown.postprocessors import Postprocessor

from jetfuelburn import __version__

# The build runs from the project root, where .readthedocs.yaml puts the wheel.
WHEEL_DIR = Path("docs/_static/wheel")

_INSTALL_ATTR = re.compile(r'data-install="([^"]*)"')
# Longer operators come first so ``==`` is one specifier, not two characters.
_REQUIREMENT = re.compile(
    r"^(?P<name>jetfuelburn)"
    r"(?P<extra>\[[^\]]+\])?"
    r"(?P<specifier>(?:===|==|~=|!=|<=|>=|<|>).*)?$"
)

_logger = logging.getLogger("mkdocs.jetfuelburn._pyodide")
_warned: set[Path] = set()


def wheel_filename(version: str = __version__) -> str:
    """Name of the pure-Python wheel that ``pip wheel .`` builds for a version."""
    return f"jetfuelburn-{version}-py3-none-any.whl"


def wheel_url(
    version: str = __version__,
    base_url: str | None = None,
    wheel_dir: Path = WHEEL_DIR,
) -> str | None:
    """URL of this build's wheel on the documentation site, or ``None``.

    ``base_url`` defaults to ``READTHEDOCS_CANONICAL_URL``, which Read the Docs
    sets to the URL of the version being built. Without it, or when the wheel
    is missing from ``wheel_dir``, the result is ``None`` and the caller pins
    the version instead.
    """
    base_url = base_url or os.environ.get("READTHEDOCS_CANONICAL_URL")
    if not base_url:
        return None
    wheel = Path(wheel_dir) / wheel_filename(version)
    if not wheel.is_file():
        if wheel not in _warned:  # one warning per build, whatever the page count
            _warned.add(wheel)
            _logger.warning(
                f"{wheel} is missing, so the interactive code blocks install "
                f"jetfuelburn=={version} from PyPI instead."
            )
        return None
    return f"{base_url.rstrip('/')}/_static/wheel/{wheel.name}"


def pin_install_spec(
    spec: str, version: str = __version__, wheel: str | None = None
) -> str:
    """Replace an unversioned ``jetfuelburn`` requirement inside ``data-install``.

    Without extras the requirement becomes ``wheel`` when given, else
    ``jetfuelburn==version``. With extras it becomes
    ``jetfuelburn[extras]==version``. Other items stay as they are.
    """
    pinned: list[str] = []
    for raw in spec.split(","):
        item = raw.strip()
        if not item:
            continue
        match = _REQUIREMENT.fullmatch(item)
        if match and not match.group("specifier"):
            extra = match.group("extra")
            if wheel and not extra:
                item = wheel
            else:
                item = f"jetfuelburn{extra or ''}=={version}"
        pinned.append(item)
    return ",".join(pinned)


class _PinPyodidePostprocessor(Postprocessor):
    def __init__(self, md, wheel: str | None):
        super().__init__(md)
        self.wheel = wheel

    def run(self, text: str) -> str:
        def replace(match: re.Match[str]) -> str:
            return (
                f'data-install="{pin_install_spec(match.group(1), wheel=self.wheel)}"'
            )

        return _INSTALL_ATTR.sub(replace, text)


class PinPyodideExtension(Extension):
    """Rewrite Pyodide install attributes after raw HTML is restored."""

    def __init__(self, **kwargs):
        self.config = {
            # An empty default keeps the value a string. python-markdown parses
            # values for a None default as booleans.
            "wheel": ["", "Wheel URL to install. Default: from the environment."],
        }
        super().__init__(**kwargs)

    def extendMarkdown(self, md) -> None:
        wheel = self.getConfig("wheel") or wheel_url()
        # Priority 30 restores stashed HTML. A lower priority runs after that.
        md.postprocessors.register(
            _PinPyodidePostprocessor(md, wheel),
            "jetfuelburn_pyodide_pin",
            15,
        )


def makeExtension(**kwargs):
    return PinPyodideExtension(**kwargs)
