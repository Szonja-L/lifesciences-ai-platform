# Changelog

All notable changes to this project are recorded here. Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); versions follow semantic versioning.

## [Unreleased]

### Added

- Python 3.12 project skeleton: `pyproject.toml` (hatchling build, `src` layout), package `lifesciences_platform` with `common` subpackage, smoke test.
- Tooling: ruff (lint and format), mypy (strict, two relaxations), pytest; `Makefile` targets `install`, `lint`, `typecheck`, `test`, `check`.
- ADR 0002: Python tooling.
