[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/x_logger/en/tutorials/logger_intro.html) [![ja](https://img.shields.io/badge/lang-ja-blue.svg)](https://ohara-lab-su.github.io/x_logger/ja/tutorials/logger_intro.html)

# Tutorial

Basic logger features and usage.

## Display logs on screen

```python
from x_logger import XLogger

logger = XLogger(
    log_level="INFO",
    logger_name="Sample",
)

logger.info("INFO")
logger.warning("WARNING")
logger.error("ERROR")
```

Logs are displayed in the following format:

```text
2026-03-05 10:24:54 Sample[138144] INFO INFO
```

`[138144]` is the PID of the process that emitted the log.

## Change the log level

```python
from x_logger import XLogger

logger = XLogger(
    log_level="INFO",
    logger_name="Sample",
)

logger.info("INFO")
logger.debug("DEBUG")

logger.setLevel("DEBUG")

logger.info("INFO")
logger.debug("DEBUG")
```

The first `DEBUG` message is not displayed; `DEBUG` messages after `setLevel("DEBUG")` are displayed.

## Save logs to a file

```python
from x_logger import XLogger

logger = XLogger(
    log_level="INFO",
    log_mode="file",
    log_name="sample.log",
    logger_name="Sample",
)

logger.info("INFO")
logger.error("ERROR")
```

Logs are saved to `sample.log` while also being displayed on screen.

## Use log rotation

```python
from x_logger import XLogger

logger = XLogger(
    log_level="INFO",
    log_mode="rotating",
    log_name="device.log",
    backup_count=30,
    logger_name="DeviceSample",
)

logger.info("server started")
```

The log is rotated when the date changes. `log_mode="rotate"` is also supported. `backup_count` specifies how many rotated generations to retain.

## Create the same logger multiple times

Repeatedly creating a logger with the same `logger_name` does not accumulate XLogger-managed handlers.

```python
from x_logger import XLogger

for index in range(5):
    logger = XLogger(
        log_level="INFO",
        log_mode="file",
        log_name="sample.log",
        logger_name="Sample",
    )
    logger.info(
        "configuration_%d",
        index,
    )

logger.info("FINAL")
```

`FINAL` is emitted only once.

## Use multiprocessing

When a single Device Server uses multiple processes, use `MultiProcessXLogger`.

Create one logger in the parent process and pass the same instance to each worker process.

```python
import multiprocessing
import os

from x_logger.multiprocess import MultiProcessXLogger


def worker(logger, worker_name):
    logger.info(
        "%s pid=%d",
        worker_name,
        os.getpid(),
    )


def main():
    logger = MultiProcessXLogger(
        log_level="INFO",
        log_mode="rotating",
        log_name="device.log",
        backup_count=30,
        logger_name="DeviceSample",
        start_method="spawn",
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

    logger.close()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
```

The workers share the logger's Queue created in the parent process, consolidating logs from every process into one logical logger.

For example, if the parent emits one record and each of three workers emits one record, a total of four records is saved.

Duplicate handler registration does not increase the number of records.

The log format includes the PID, so the originating process can be identified.

## Multiprocessing tests

Tests emit logs concurrently from multiple workers and verify that:

- All workers' log records are saved.
- The same event is not duplicated.
- The PID recorded in each log matches the worker's actual PID.

For example, with four workers emitting five records each, tests verify that all 20 records are saved and that each event appears exactly once.

---
## Author
- Kengo NAKADA
