#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MultiProcessXLogger usage sample."""
import multiprocessing
import os
import time
from pathlib import Path

from x_logger.multiprocess import MultiProcessXLogger


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)


def worker(logger, worker_name):
    logger.info(
        "%s started body_pid=%d",
        worker_name,
        os.getpid(),
    )

    for index in range(3):
        logger.info(
            "%s message_%d body_pid=%d",
            worker_name,
            index,
            os.getpid(),
        )
        time.sleep(0.05)

    logger.warning(
        "%s finished body_pid=%d",
        worker_name,
        os.getpid(),
    )


def main():
    logger = MultiProcessXLogger(
        logger_name="DeviceSample",
        log_mode="rotating",
        log_name=str(LOG_DIR / "device_sample.log"),
        backup_count=7,
        log_level="DEBUG",
        start_method="spawn",
    )

    logger.info(
        "parent started body_pid=%d",
        os.getpid(),
    )

    context = multiprocessing.get_context("spawn")
    processes = []

    for index in range(3):
        process = context.Process(
            target=worker,
            args=(logger, "worker_%d" % index),
        )
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    logger.info(
        "parent finished body_pid=%d",
        os.getpid(),
    )
    logger.close()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
