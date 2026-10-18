import re

from markdown import Markdown

from jetfuelburn import __version__
from jetfuelburn._pyodide import (
    makeExtension,
    pin_install_spec,
    wheel_filename,
    wheel_url,
)


def test_pin_bare_name():
    assert pin_install_spec("jetfuelburn") == f"jetfuelburn=={__version__}"


def test_pin_is_idempotent():
    once = pin_install_spec("jetfuelburn")
    assert pin_install_spec(once) == once


def test_pin_extra_and_leave_other_packages():
    spec = "jetfuelburn[optionaldependencies], openap"
    assert pin_install_spec(spec) == (
        f"jetfuelburn[optionaldependencies]=={__version__},openap"
    )


def test_leave_existing_specifier_and_other_packages():
    assert pin_install_spec("jetfuelburn==3.4.0") == "jetfuelburn==3.4.0"
    assert pin_install_spec("jetfuelburn>=3") == "jetfuelburn>=3"
    assert pin_install_spec("openap") == "openap"


def test_rendered_attribute_uses_documented_version():
    html = '<div class="pyodide" data-install="jetfuelburn"></div>'
    rendered = Markdown(extensions=[makeExtension()]).convert(html)
    assert re.findall(r'data-install="([^"]*)"', rendered) == [
        f"jetfuelburn=={__version__}"
    ]


def test_wheel_replaces_the_bare_name_only():
    wheel = "https://docs.example/en/latest/_static/wheel/jetfuelburn-4.0.0-py3-none-any.whl"
    assert pin_install_spec("jetfuelburn", wheel=wheel) == wheel
    assert pin_install_spec("jetfuelburn, openap", wheel=wheel) == f"{wheel},openap"
    # A URL cannot carry extras, so extras keep the version pin.
    assert pin_install_spec("jetfuelburn[optionaldependencies]", wheel=wheel) == (
        f"jetfuelburn[optionaldependencies]=={__version__}"
    )
    assert pin_install_spec("jetfuelburn==3.4.0", wheel=wheel) == "jetfuelburn==3.4.0"


def test_wheel_url_needs_the_base_url_and_the_file(tmp_path, monkeypatch):
    monkeypatch.delenv("READTHEDOCS_CANONICAL_URL", raising=False)
    assert wheel_url(version="4.0.0", wheel_dir=tmp_path) is None
    base = "https://jetfuelburn.readthedocs.io/en/latest/"
    assert wheel_url(version="4.0.0", base_url=base, wheel_dir=tmp_path) is None
    (tmp_path / wheel_filename("4.0.0")).write_bytes(b"")
    assert wheel_url(version="4.0.0", base_url=base, wheel_dir=tmp_path) == (
        f"{base}_static/wheel/jetfuelburn-4.0.0-py3-none-any.whl"
    )
    monkeypatch.setenv("READTHEDOCS_CANONICAL_URL", base)
    assert wheel_url(version="4.0.0", wheel_dir=tmp_path) == (
        f"{base}_static/wheel/jetfuelburn-4.0.0-py3-none-any.whl"
    )


def test_rendered_attribute_uses_the_wheel():
    wheel = "https://docs.example/en/latest/_static/wheel/jetfuelburn-4.0.0-py3-none-any.whl"
    html = '<div class="pyodide" data-install="jetfuelburn"></div>'
    rendered = Markdown(extensions=[makeExtension(wheel=wheel)]).convert(html)
    assert re.findall(r'data-install="([^"]*)"', rendered) == [wheel]
