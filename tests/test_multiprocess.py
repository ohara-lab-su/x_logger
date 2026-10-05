#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Automatic multiprocessing aggregation and duplication tests."""
import multiprocessing
import os
import re
import tempfile
from pathlib import Path

from x_logger.multiprocess import MultiProcessXLogger


WORKER_COUNT = 4
MESSAGES_PER_WORKER = 5


def worker(logger, worker_index):
    pid = os.getpid()

    for message_index in range(MESSAGES_PER_WORKER):
        logger.info(
            "MULTI_EVENT worker=%d message=%d body_pid=%d",
            worker_index,
            message_index,
            pid,
        )


def run_test(start_method):
    with tempfile.TemporaryDirectory() as temporary_directory:
        log_file = Path(temporary_directory) / (
            "multiprocess_%s.log" % start_method
        )

        logger = MultiProcessXLogger(
            logger_name="MultiDuplicateTest_%s" % start_method,
            log_mode="rotating",
            log_name=str(log_file),
            backup_count=3,
            log_level="INFO",
            start_method=start_method,
        )

        context = multiprocessing.get_context(start_method)
        processes = []

        for worker_index in range(WORKER_COUNT):
            process = context.Process(
                target=worker,
                args=(logger, worker_index),
            )
            processes.append(process)
            process.start()

        worker_pids = []
        for process in processes:
            process.join()
            if process.exitcode != 0:
                raise AssertionError(
                    "worker failed: pid=%s exitcode=%s"
                    % (process.pid, process.exitcode)
                )
            worker_pids.append(process.pid)

        logger.close()

        lines = log_file.read_text(encoding="utf-8").splitlines()
        event_lines = []

        for line in lines:
            if "MULTI_EVENT" in line:
                event_lines.append(line)

        expected_count = WORKER_COUNT * MESSAGES_PER_WORKER
        actual_count = len(event_lines)

        if actual_count != expected_count:
            raise AssertionError(
                "%s output count: expected %d, got %d"
                % (start_method, expected_count, actual_count)
            )

        seen_events = set()
        seen_header_pids = set()
        seen_body_pids = set()

        for line in event_lines:
            event_match = re.search(
                r"worker=(\d+) message=(\d+) body_pid=(\d+)",
                line,
            )
            if event_match is None:
                raise AssertionError(
                    "event body could not be parsed: %s" % line
                )

            header_match = re.search(r"\[(\d+)\]", line)
            if header_match is None:
                raise AssertionError(
                    "logger PID could not be parsed: %s" % line
                )

            worker_index = int(event_match.group(1))
            message_index = int(event_match.group(2))
            body_pid = int(event_match.group(3))
            header_pid = int(header_match.group(1))

            event_key = (worker_index, message_index)
            if event_key in seen_events:
                raise AssertionError(
                    "duplicate event detected: %s" % (event_key,)
                )

            seen_events.add(event_key)
            seen_header_pids.add(header_pid)
            seen_body_pids.add(body_pid)

            if header_pid != body_pid:
                raise AssertionError(
                    "LogRecord PID %d != worker PID %d"
                    % (header_pid, body_pid)
                )

        if seen_body_pids != set(worker_pids):
            raise AssertionError(
                "worker PID set mismatch: log=%s process=%s"
                % (sorted(seen_body_pids), sorted(worker_pids))
            )

        if seen_header_pids != set(worker_pids):
            raise AssertionError(
                "header PID set mismatch: log=%s process=%s"
                % (sorted(seen_header_pids), sorted(worker_pids))
            )

        print(
            "PASS: %s: %d events, no duplicates, PID preserved"
            % (start_method, actual_count)
        )


def main():
    methods = multiprocessing.get_all_start_methods()

    if "spawn" in methods:
        run_test("spawn")

    if "fork" in methods:
        run_test("fork")


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
