import json
from contextlib import contextmanager
from dataclasses import dataclass
from importlib import resources
from typing import Any, Dict, Iterable, Iterator, Mapping

import matplotlib as mpl


@dataclass(frozen=True)
class Theme:
    """A named matplotlib theme with associated colors and rcParams."""

    name: str
    colors: Mapping[str, str]
    rc: mpl.RcParams


def _read_default_style() -> Dict:
    data = (resources.files("namuplot") / "style.json").read_bytes()
    return json.loads(data.decode("utf-8"))


def _build_rcparams(colors: Mapping[str, str]) -> mpl.RcParams:
    rc = mpl.RcParams()

    text = colors["text"]
    bg = colors["background"]
    gray = colors["gray"]

    # Core look
    rc["figure.facecolor"] = bg
    rc["figure.edgecolor"] = bg
    rc["savefig.facecolor"] = bg
    rc["savefig.edgecolor"] = bg

    rc["axes.facecolor"] = bg
    rc["axes.edgecolor"] = text
    rc["axes.labelcolor"] = text
    rc["axes.titlecolor"] = text
    rc["text.color"] = text

    rc["xtick.color"] = text
    rc["ytick.color"] = text

    # Grid
    rc["axes.grid"] = True
    rc["grid.color"] = text
    rc["grid.alpha"] = 0.30
    rc["grid.linestyle"] = "-"
    rc["grid.linewidth"] = 0.8

    # Spines (cleaner)
    rc["axes.spines.top"] = False
    rc["axes.spines.right"] = False

    # Lines / markers
    rc["lines.linewidth"] = 2.0
    rc["lines.markersize"] = 6

    # Aesthetics: use palette as the default cycle
    cycle = [
        colors["a"],
        colors["b"],
        colors["c"],
        colors["d"],
        colors["e"],
    ]
    rc["axes.prop_cycle"] = mpl.cycler(color=cycle)

    # Fonts
    # (Users who don’t have NanumBarunGothicOTF still get a reasonable font.)
    rc["font.family"] = "sans-serif"
    rc["font.sans-serif"] = [
        "NanumBarunGothicOTF",
        "NanumBarunGothic",
        "NanumGothic",
        "Apple SD Gothic Neo",
        "Malgun Gothic",
        "DejaVu Sans",
    ]

    # Subtle gray for secondary elements
    rc["legend.frameon"] = False
    rc["axes.unicode_minus"] = False
    rc["axes.formatter.useoffset"] = False
    rc["axes.formatter.limits"] = (-4, 5)
    rc["errorbar.capsize"] = 2.0

    # Do not use unicode minus for negative values
    rc["axes.unicode_minus"] = False

    # Set a neutral “gray” as edge/outline defaults
    rc["patch.edgecolor"] = gray
    rc["boxplot.flierprops.markeredgecolor"] = gray

    return rc


def load_themes(configs: Mapping[str, Mapping[str, Any]]) -> Dict[str, Theme]:
    themes: Dict[str, Theme] = {}
    for name, colors in configs.items():
        themes[name] = Theme(name=name, colors=colors, rc=_build_rcparams(colors))
    return themes


_DEFAULT_THEMES = load_themes(_read_default_style())


def available() -> Iterable[str]:
    return _DEFAULT_THEMES.keys()


def get(name: str) -> Theme:
    try:
        return _DEFAULT_THEMES[name]
    except KeyError as e:
        raise KeyError(f"Unknown theme: {name!r}. Available: {sorted(_DEFAULT_THEMES)}") from e


def use(name: str) -> Theme:
    """Apply theme globally (updates matplotlib.rcParams) and return it."""
    theme = get(name)
    mpl.rcParams.update(theme.rc)
    return theme


def iter_use(names: Iterable[str] | None = None) -> Iterator[tuple[str, Theme]]:
    """Iterate through all available themes, applying each globally in turn."""
    if names is None:
        names = available()
    for name in names:
        yield name, use(name)


@contextmanager
def context(name: str):
    """Temporarily apply a theme within a with-block."""
    with mpl.rc_context(rc=get(name).rc):
        yield


def to_rcparams(name: str) -> mpl.RcParams:
    """Get a copy of the rcParams for a theme (so callers can modify safely)."""
    theme = get(name)
    rc = mpl.RcParams()
    rc.update(theme.rc)
    return rc
