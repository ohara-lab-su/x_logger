[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/x_logger/en/manual/changelog.html) [![ja](https://img.shields.io/badge/lang-ja-blue.svg)](https://ohara-lab-su.github.io/x_logger/ja/manual/changelog.html)

# CHANGELOG

## 2026.10.05, v0.3.0, nakada

- Redesigned the logger configuration based on v0.2.15.
- Standardized `logger_name` as the logical logger identifier, based on Python logging's named loggers.
- Added identification of handlers created by XLogger; reconfiguring a logger now replaces only handlers managed by XLogger.
- Retained the existing output modes: `default`, `file`, and `rotating` / `rotate`.
- Retained simultaneous console output in `file` and `rotating` modes.
- Synchronized the levels of the logger and XLogger-managed handlers through `setLevel()`.
- Added `MultiProcessXLogger` for multiprocessing in `multiprocess.py`.
- Used QueueHandler / QueueListener for multiprocessing, consolidating file and rotating handlers in the owner process.
- Added support for multiprocessing configurations using both `fork` and `spawn`.

## 2026.07.28, v0.2.15, nakada

- After the cobotta3/4 setup.

## 2026.07.14, v0.2.14, nakada

- Version handed over to the Yashiro Laboratory.

## 2026.03.09, v0.2.13, nakada

- Final version before the business trip (2026.03.15).

## 2026.03.09, v0.2.12, nakada

Documentation adjustments.

## 2026.03.04, v0.2.11, nakada

- Introduced the `loglevel` option (compatible with logging); internally named `log_level`.

## 2026.02.06, v0.2.10, nakada

- Fixed a bug in which the logger configuration did not work correctly when displaying logs on screen.

## 2026.01.08, v0.2.9, nakada

- Changed to standard logger-style calls such as `logger.debug(self, msg, *args)` (wording preserved from the original history).

## 2025.11.06, v0.2.8, nakada

- Discontinued the symlink approach.

## 2025.11.06, v0.2.7, nakada

- Restored `setup.py` in addition to `pyproject.toml` to allow setup in an offline Python 3.6 environment.
  - Symlink: `<project root>/x_logger`.

## 2025.10.16, v0.2.6, nakada

- Added the Sphinx module (`project.toml`, as recorded in the original history).

## 2025.09.5, v0.2.5, nakada

- Documentation.

## 2025.09.5, v0.2.4, nakada

- `sphinx_docs`: not very useful because most code has no docstrings.

## 2025.09.1, v0.2.3, nakada

Fixed `project.toml` (as recorded in the original history).

## 2025.07.29, v0.2.2, nakada

- Both `rotate` and `rotating` are accepted.

## 2025.07.29, v0.2.1, nakada

- Converted log-name-related settings into instance variables (so they can be retrieved through `get_xxx`).

## 2025.07.29, v0.2.0, nakada

- Restored and fixed simultaneous standard-output logging in `file` / `rotate` modes, which had been omitted in v0.1.x.

## v0.1.1, nakada

Resolved conflicts and added test code.

## v0.1.0, nakada

Rebuilt the logger because a bug involving duplicated logging occasionally manifested itself.

## v0.0.2, nakada

Recovered debugging-print utilities that had been casually added to `util` and were causing various problems.

## v0.0.1, nakada

Added the `get_silent_logger()` method to `util`.
