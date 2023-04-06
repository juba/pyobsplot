# Get __version__ from pyproject.toml (currently installed)
try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:
    from importlib_metadata import PackageNotFoundError, version  # type: ignore

try:
    __version__ = version("pyobsplot")
except PackageNotFoundError:
    __version__ = "uninstalled"


from .obsplot import Obsplot  # noqa:F401
from .parsing import js  # noqa:F401
from .jsmodules import Plot, d3, Math  # noqa:F401

__all__ = ["Obsplot", "Plot", "d3", "Math", "js", "__version__"]
