"""The shared site tabs navigate in the same browser tab."""

from pathlib import Path

PARTIAL = Path(__file__).resolve().parents[1] / "docs" / "_overrides" / "partials" / "family.html"


def test_family_tabs_stay_in_the_same_tab():
    html = PARTIAL.read_text()
    assert html.count('target="_self"') == 4
    assert "_blank" not in html
