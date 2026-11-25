"""Smoke test: the package is installed and reports a version."""

import re
from importlib.metadata import version

import lifesciences_platform


def test_version_matches_installed_metadata() -> None:
    assert lifesciences_platform.__version__ == version("lifesciences-platform")


def test_version_is_semver_like() -> None:
    assert re.fullmatch(r"\d+\.\d+\.\d+", lifesciences_platform.__version__)
