# x_logger

## Origin of the name

The `x_logger` package consolidates common functionality from project-specific loggers, such as the logger for `daruma` and `el_logger` for `elves`, and reconstructs it as a general-purpose logger without restricting its intended use.

The `x` denotes an arbitrary or general-purpose application. Another simple reason for the name is that no better name came to mind.

## Introduction

`x_logger` is a logger built on Python's standard `logging` module. It uses `logger_name` as the identifier of a logical logger and makes it easy to configure console output, file output, and `TimedRotatingFileHandler`.

The same `logger_name` refers to the same named logger; different `logger_name` values identify different loggers.

For devices, the basic convention is to use the device class name as `logger_name`. This makes it possible to use the same logical logger name consistently for log storage, multiprocessing, and a future log-viewing server.

## Single-process logger

Normally, use `XLogger`.

```python
from x_logger.x_logger import XLogger

logger = XLogger(
    logger_name="Cobotta",
    log_mode="rotating",
    log_name="Cobotta.log",
)

logger.info("started")
```

An `XLogger` instance can also be passed to other classes. However, the logical identity of the logger is its `logger_name`, not the instance itself.

### log_mode

`default` outputs to the console only.

`file` outputs to both the specified file and the console. It can be used for standalone file logging and does not require a device server or log-viewing server.

`rotating` or `rotate` outputs to both a `TimedRotatingFileHandler` and the console. Rotation occurs at midnight, and the number of retained backups is specified by `backup_count`.

## Handler management

Handlers created by XLogger are tagged with identification information for XLogger management. When XLogger reconfigures the same `logger_name`, it closes the previous XLogger-managed handlers before replacing them with the new configuration.

This prevents console or file handlers from accumulating when XLogger is recreated.

Named loggers use `propagate = False`, preventing XLogger output from passing through the root logger and appearing on the console again.

The root logger's coloredlogs configuration is performed only once per process.

## Multiprocessing logger

For multiprocessing, use the separate `MultiProcessXLogger` class. It shares the same concepts of output modes, logger names, levels, and formats as the single-process `XLogger`.

```python
from x_logger.multiprocess import MultiProcessXLogger

logger = MultiProcessXLogger(
    logger_name="Cobotta",
    log_mode="rotating",
    log_name="Cobotta.log",
)
```

In multiprocessing, each process does not own a file handler. Instead, each process sends `LogRecord` objects through a `QueueHandler` to the owner process. Only the owner's `QueueListener` owns console, file, and rotating handlers.

```text
parent process ---\
child process 1 ---+--> Queue --> QueueListener --> console
child process 2 ---/                         |
                                             +--> file / rotating file
```

This keeps file output and rotation under a single owner for each logical logger.

With `fork`, file handlers inherited by the child process are closed and logging is switched to `QueueHandler`. With `spawn`, `QueueHandler` is configured on the restored logger.

Multiprocessing operations, the Queue, QueueListener, process identification, and shutdown are separated into `multiprocess.py`.

## Logical loggers and log viewing

In device systems, the device class name is generally used as `logger_name`.

```text
Cobotta
  -> logger_name: Cobotta
  -> log storage: <prefix>/Cobotta/...

Camera
  -> logger_name: Camera
  -> log storage: <prefix>/Camera/...
```

A future log-viewing server is envisioned to expose current and rotated logs over gRPC or similar protocols, using this logical logger name as its reference.

XLogger is responsible for creating and storing logs, while the log-viewing server is responsible for exposing the stored logical log streams.
