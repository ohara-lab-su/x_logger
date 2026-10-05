#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automatic duplicate-prevention tests for XLogger."""
import logging
import tempfile
from pathlib import Path

from x_logger.x_logger import XLogger


def count_marker(path, marker):
    count = 0
    lines = path.read_text(encoding="utf-8").splitlines()

    for line in lines:
        if marker in line:
            count += 1

    return count


def main():
    with tempfile.TemporaryDirectory() as temporary_directory:
        log_file = Path(temporary_directory) / "single.log"

        logger = None
        for index in range(10):
            logger = XLogger(
                logger_name="DuplicateTest",
                log_mode="file",
                log_name=str(log_file),
                log_level="DEBUG",
            )

        marker = "SINGLE_EXACTLY_ONCE"
        logger.info(marker)

        count = count_marker(log_file, marker)
        if count != 1:
            raise AssertionError(
                "same-name reconstruction duplicated output: %d" % count
            )

        handlers = []
        for handler in logger.get_logger().handlers:
            handlers.append(handler)

        if len(handlers) != 2:
            raise AssertionError(
                "expected file + console handlers, got %d" % len(handlers)
            )

        other_file = Path(temporary_directory) / "other.log"
        other_logger = XLogger(
            logger_name="OtherLogger",
            log_mode="file",
            log_name=str(other_file),
            log_level="INFO",
        )

        other_marker = "OTHER_LOGGER_ONLY"
        other_logger.info(other_marker)

        if count_marker(other_file, other_marker) != 1:
            raise AssertionError("other logger output count is not 1")

        if count_marker(log_file, other_marker) != 0:
            raise AssertionError("different logger_name leaked into file")

        if logger.get_logger().propagate:
            raise AssertionError(
                "XLogger propagate must be False to avoid root duplication"
            )

        logging.getLogger().info("ROOT_LOGGER_TEST")

    print("PASS: single-process duplicate-prevention tests")


if __name__ == "__main__":
    main()
