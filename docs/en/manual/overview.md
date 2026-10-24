[![en](https://img.shields.io/badge/lang-en-red.svg)](https://ohara-lab-su.github.io/x_logger/en/manual/overview.html) [![ja](https://img.shields.io/badge/lang-ja-blue.svg)](https://ohara-lab-su.github.io/x_logger/ja/manual/overview.html)

# x logger (logger)
View on [GitHub](https://github.com/ohara-lab-su/x_logger/) / [ohara-lab-su documentation](https://ohara-lab-su.github.io/)

---

# A simple, straightforward logger

Basic software for recording program operation. In a sense, logging is one of the most fundamental class libraries in a program.

The main functions are:

- For device servers: log rotation.
- For device-control clients: straightforward log-file storage.
- For testing and servers: display logs on screen.
- For multiprocessing programs: consolidate output into a single log.

Even if a logger with the same name is created multiple times, handlers do not accumulate and cause duplicate log output.

For multiprocessing, a logger created in one parent process can be passed to multiple worker processes. Records emitted by all processes are consolidated into one log.

## Usage

Using a logger instead of `print()` records operational status together with the time, logger name, PID, and log level.

### Using standard logging

Without this logger, Python's standard `logging` can be used directly, for example:

```python
import logging

log_level = "INFO"
logging.basicConfig(level=log_level.upper())
logger = logging.getLogger(__name__)

logger.info("Hello")
```

Python's standard `logging` can also be used directly when you want to configure formatting, file storage, and rotation yourself.

### Using x_logger

Normally, create an `XLogger` and use it instead of `print()`.

```python
from x_logger import XLogger

logger = XLogger(
    log_level="INFO",
    logger_name="Sample",
)

logger.info("Hello")
logger.debug("DEBUG")
```

At log level `INFO`, `debug()` is not emitted.

```python
logger = XLogger(
    log_level="DEBUG",
    logger_name="Sample",
)

logger.info("Hello")
logger.debug("DEBUG")
```

At log level `DEBUG`, both messages are emitted.

Use `setLevel()` to change the level during execution.

```python
logger.setLevel("DEBUG")
logger.debug("DEBUG")
```

Screen and file output use a format such as:

```text
2026-03-05 10:24:54 Sample[138144] INFO Hello
```

That is:

```text
timestamp logger_name[PID] log_level message
```

`logger_name` is the name of the logger. For a device server, specify an identifiable name such as the DeviceClass name.

### Save logs to a file

With `log_mode="file"`, logs are saved to the specified file while also being displayed on screen.

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

### Use rotation

For long-running servers, rotate logs rather than writing indefinitely to a single file.

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

`rotating` rotates the log when the date changes. `rotate` is also accepted. `backup_count` specifies the number of retained generations.

### Recreate the same logger

When `XLogger` is recreated with the same `logger_name`, XLogger-managed handlers are cleaned up before reconfiguration.

```python
from x_logger import XLogger

logger = XLogger(
    log_mode="file",
    log_name="sample.log",
    logger_name="Sample",
)

logger = XLogger(
    log_mode="file",
    log_name="sample.log",
    logger_name="Sample",
)

logger.info("Hello")
```

In this case, the final `Hello` is not emitted multiple times because of duplicate handler registration.

### Use multiprocessing

When multiple processes run inside one device server, use `MultiProcessXLogger`.

Create one logger in the parent process and pass its instance to each worker process.

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

Records from all workers are consolidated into the same `DeviceSample` log.

The PID shown in each log record is the actual PID of the process that generated it.

File and rotating-file output are owned in one place, so multiple processes do not directly operate on the same log file.

---
## Author
- Kengo NAKADA
