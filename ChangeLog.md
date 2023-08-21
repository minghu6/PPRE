# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2023-08-21

### Upgraded:

- Migrate from dead Qt4 to Qt5.
- Migrate from dead python2 to python3 (=3.10).

### Added

- Set editable for QtComboBox to make use of quick search by name.

### Fixed

- Replace all hard code path using `os.path.join` and trim starting '/' from those const file path.
- Fix call exportToRom without `self` mistake which causes save failed.
- Fix wrong submodule init command in setup scripts.

[0.2.0]: https://github.com/minghu6/PPRE/tree/v0.2.0
