#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""XLogger single-process usage sample."""
from pathlib import Path

from x_logger.x_logger import XLogger


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def main():
    console_logger = XLogger(
        logger_name="ConsoleSample",
        log_level="DEBUG",
    )
    console_logger.debug("debug message")
    console_logger.info("info message")
    console_logger.warning("warning message")
    console_logger.error("error message")

    file_logger = XLogger(
        logger_name="FileSample",
        log_mode="file",
        log_name=str(LOG_DIR / "file_sample.log"),
        log_level="DEBUG",
    )
    file_logger.info("file mode message")

    rotating_logger = XLogger(
        logger_name="RotatingSample",
        log_mode="rotating",
        log_name=str(LOG_DIR / "rotating_sample.log"),
        backup_count=7,
        log_level="DEBUG",
    )
    rotating_logger.info("rotating mode message")

    rotating_logger.setLevel("ERROR")
    rotating_logger.info("this INFO message is filtered")
    rotating_logger.error("this ERROR message is recorded")


if __name__ == "__main__":
    main()
