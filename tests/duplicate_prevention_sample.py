#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sample intentionally exercising duplicate-prone logger usage."""
import logging
from pathlib import Path

from x_logger.x_logger import XLogger


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)
LOG_FILE = LOG_DIR / "duplicate_prevention.log"


def configure_same_logger_repeatedly():
    logger = None

    for index in range(5):
        logger = XLogger(
            logger_name="DuplicatePreventionSample",
            log_mode="file",
            log_name=str(LOG_FILE),
            log_level="INFO",
        )
        logger.info(
            "configuration_%d emitted once",
            index,
        )

    return logger


def main():
    if LOG_FILE.exists():
        LOG_FILE.unlink()

    logging.getLogger().info(
        "root logger remains a separate output path"
    )

    logger = configure_same_logger_repeatedly()

    marker = "FINAL_DUPLICATE_CHECK"
    logger.info(marker)

    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    count = 0

    for line in lines:
        if marker in line:
            count += 1

    print("marker count in file:", count)

    if count != 1:
        raise AssertionError(
            "duplicate output detected: expected 1, got %d" % count
        )

    print("PASS: repeated XLogger construction did not duplicate output")


if __name__ == "__main__":
    main()
