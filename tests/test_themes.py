import json
from importlib import resources

import matplotlib as mpl
import pytest

from namuplot import themes

# Use a non-interactive backend for tests
mpl.use("Agg", force=True)


@pytest.fixture(scope="session")
def default_style() -> dict:
    raw = (resources.files("namuplot") / "style.json").read_text(encoding="utf-8")
    return json.loads(raw)


@pytest.fixture(autouse=True)
def restore_rcparams():
    with mpl.rc_context():
        yield


def test_available_matches_style_json(default_style: dict):
    assert set(themes.available()) == set(default_style)


def test_get_known_theme(default_style: dict):
    theme = themes.get("light")

    assert theme.name == "light"
    assert theme.colors["background"] == default_style["light"]["background"]
    assert isinstance(theme.rc, mpl.RcParams)


def test_get_unknown_theme_raises():
    with pytest.raises(KeyError) as excinfo:
        themes.get("unknown-theme")

    msg = str(excinfo.value)
    assert "Unknown theme: 'unknown-theme'" in msg
    assert "Available:" in msg


def test_use_applies_theme_rcparams(default_style: dict):
    theme = themes.use("dark")

    assert theme is themes.get("dark")
    assert mpl.rcParams["figure.facecolor"] == default_style["dark"]["background"]
    assert mpl.rcParams["text.color"] == default_style["dark"]["text"]
    assert mpl.rcParams["axes.prop_cycle"].by_key()["color"][0] == default_style["dark"]["a"]


def test_iter_use_applies_each_requested_theme(default_style: dict):
    names = ["light", "dark"]
    seen = []

    for name, theme in themes.iter_use(names):
        seen.append(name)
        assert theme.name == name
        assert mpl.rcParams["figure.facecolor"] == default_style[name]["background"]

    assert seen == names
    assert mpl.rcParams["figure.facecolor"] == default_style[names[-1]]["background"]


def test_context_temporarily_applies_theme(default_style: dict):
    original_facecolor = mpl.rcParams["figure.facecolor"]

    with themes.context("light"):
        assert mpl.rcParams["figure.facecolor"] == default_style["light"]["background"]

    assert mpl.rcParams["figure.facecolor"] == original_facecolor


def test_to_rcparams_returns_isolated_copy():
    theme_rc = themes.get("dark").rc

    rc_copy = themes.to_rcparams("dark")

    assert rc_copy is not theme_rc
    assert rc_copy["figure.facecolor"] == theme_rc["figure.facecolor"]

    rc_copy["figure.facecolor"] = "#123456"
    assert theme_rc["figure.facecolor"] != "#123456"
