# NamuPlot

Light/Dark Matplotlib themes that blends well with NamuWiki's color palette.

## Install
```bash
pip install namuplot
```

## Usage
```python
import matplotlib.pyplot as plt
import namuplot

for mode, theme in namuplot.iter_use():
    plt.plot([0, 1, 2], [1, 2, 3], label="line")
    plt.plot([1], [2], color=theme.colors["major"])
    plt.legend()
    plt.savefig(f"images/example_plot_{mode}.svg", bbox_inches="tight", format="svg")
    plt.show()
```

## Available themes
```python
import mpl_visual as mv
print(list(mv.available()))  # [light, dark]
```

## License
See `LICENSE`.

Note: This project is not affiliated with NamuWiki.
