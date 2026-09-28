from importlib.metadata import PackageNotFoundError, version

from fintables.api.client import FintablesClient

try:
    __version__ = version("fintables")
except PackageNotFoundError:
    __version__ = "0.1.0"

__all__ = ["FintablesClient", "__version__"]

