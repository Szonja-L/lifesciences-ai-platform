"""Life sciences AI and workflow automation platform."""

from importlib.metadata import version

# Single source of truth is pyproject.toml; read it from the installed metadata.
__version__: str = version("lifesciences-platform")

__all__ = ["__version__"]
