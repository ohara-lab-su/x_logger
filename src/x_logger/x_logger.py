#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Small logging wrapper with optional multiprocessing-safe transport."""

from __future__ import annotations

import logging
import multiprocessing
import os
from logging.handlers import QueueHandler, QueueListener, TimedRotatingFileHandler
from typing import Any, Optional

import coloredlogs


_LOG_FORMAT = "%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class XLogger:
    """Logger compatible with the historical x_logger API.

    ``multiprocess=False`` keeps the lightweight local implementation.
    ``multiprocess=True`` makes the creating process the log owner. Child
    processes only enqueue ``LogRecord`` objects; file/rotation/stream
    handlers remain exclusively in the owner process.

    Args:
        log_level: Logging level. Takes precedence over ``loglevel``.
        loglevel: Alias compatible with existing logging-style callers.
        log_mode: ``default``, ``file``, ``rotating`` or ``rotate``.
        log_name: Output file path for file modes.
        backup_count: Number of rotated files retained.
        logger_name: Name shown in log records. Defaults to ``SimpleLogger``.
        multiprocess: Enable process-safe queue transport.
        start_method: Multiprocessing start method used to create the queue.
            When explicitly set on another multiprocessing framework, use the
            same method here as well.
    """

    def __init__(
        self,
        log_level: Any = None,
        loglevel: Any = None,
        log_mode: str = "default",
        log_name: Optional[str] = None,
        backup_count: int = 30,
        logger_name: Optional[str] = None,
        multiprocess: bool = False,
        start_method: Optional[str] = None,
    ) -> None:
        self.log_level = self._resolve_level(log_level, loglevel)
        self.log_mode = log_mode
        self.log_name = log_name
        self.backup_count = backup_count
        self.logger_name = logger_name or "SimpleLogger"
        self.multiprocess = bool(multiprocess)
        self.start_method = start_method

        self._owner_pid = os.getpid()
        self._closed = False
        self._queue = None
        self._listener = None
        self._sink_handlers = []
        self.logger = self._new_logger()

        if self.multiprocess:
            context = multiprocessing.get_context(self.start_method)
            self._queue = context.Queue()
            self._configure_owner()
        else:
            self._configure_local()

    @staticmethod
    def _resolve_level(log_level: Any, loglevel: Any) -> Any:
        if log_level is not None:
            return log_level
        if loglevel is not None:
            return loglevel
        return "INFO"

    def _level(self) -> Any:
        if isinstance(self.log_level, str):
            return self.log_level.upper()
        return self.log_level

    def _new_logger(self) -> logging.Logger:
        # Deliberately do not use logging.getLogger().  getLogger() returns a
        # process-global object for a given name, which made two independent
        # XLogger("SimpleLogger") instances overwrite each other's handlers.
        logger = logging.Logger(self.logger_name)
        logger.setLevel(self._level())
        logger.propagate = False
        return logger

    def _stream_handler(self) -> logging.Handler:
        handler = logging.StreamHandler()
        handler.setLevel(self._level())
        try:
            formatter = coloredlogs.ColoredFormatter(_LOG_FORMAT, _DATE_FORMAT)
        except Exception:
            formatter = logging.Formatter(_LOG_FORMAT, _DATE_FORMAT)
        handler.setFormatter(formatter)
        return handler

    def _build_sink_handlers(self) -> list[logging.Handler]:
        handlers: list[logging.Handler] = []
        mode = self.log_mode.lower()

        if mode == "file":
            if not self.log_name:
                raise ValueError("log_name must be specified for file mode")
            file_handler = logging.FileHandler(self.log_name, encoding="utf-8")
            file_handler.setLevel(self._level())
            file_handler.setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
            handlers.append(file_handler)
        elif mode in ("rotating", "rotate"):
            if not self.log_name:
                raise ValueError("log_name must be specified for rotating mode")
            rotating_handler = TimedRotatingFileHandler(
                self.log_name,
                when="midnight",
                backupCount=self.backup_count,
                encoding="utf-8",
            )
            rotating_handler.setLevel(self._level())
            rotating_handler.setFormatter(
                logging.Formatter(_LOG_FORMAT, _DATE_FORMAT)
            )
            handlers.append(rotating_handler)
        elif mode != "default":
            # Historical behavior treated unknown modes as console-only.
            pass

        handlers.append(self._stream_handler())
        return handlers

    def _replace_handlers(self, handlers: list[logging.Handler]) -> None:
        self.logger.handlers.clear()
        for handler in handlers:
            self.logger.addHandler(handler)

    def _configure_local(self) -> None:
        self._sink_handlers = self._build_sink_handlers()
        self._replace_handlers(self._sink_handlers)

    def _configure_owner(self) -> None:
        self._sink_handlers = self._build_sink_handlers()
        self._replace_handlers([QueueHandler(self._queue)])
        self._listener = QueueListener(
            self._queue,
            *self._sink_handlers,
            respect_handler_level=True,
        )
        self._listener.start()

    def _configure_client(self) -> None:
        """Configure this process as a queue-only logging client."""
        self._listener = None
        self._sink_handlers = []
        self.logger = self._new_logger()
        self._replace_handlers([QueueHandler(self._queue)])

    def _ensure_process_role(self) -> None:
        """Switch a forked child to queue-only mode on first use."""
        if self.multiprocess and os.getpid() != self._owner_pid:
            # With fork, __getstate__/__setstate__ is not invoked.  Detect the
            # PID change lazily so inherited file handlers are never used.
            if not (
                len(self.logger.handlers) == 1
                and isinstance(self.logger.handlers[0], QueueHandler)
            ):
                self._configure_client()

    def get_log_level(self):
        return self.log_level

    def get_log_mode(self):
        return self.log_mode

    def get_log_name(self):
        return self.log_name

    def get_backup_count(self):
        return self.backup_count

    def get_logger_name(self):
        return self.logger_name

    def get_logger(self):
        self._ensure_process_role()
        return self.logger

    def setLevel(self, level):
        self.log_level = level
        self._ensure_process_role()
        normalized = level.upper() if isinstance(level, str) else level
        self.logger.setLevel(normalized)
        for handler in self.logger.handlers:
            handler.setLevel(normalized)
        if os.getpid() == self._owner_pid:
            for handler in self._sink_handlers:
                handler.setLevel(normalized)

    def debug(self, msg: str, *args, **kwargs) -> None:
        self._ensure_process_role()
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        self._ensure_process_role()
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self._ensure_process_role()
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self._ensure_process_role()
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        self._ensure_process_role()
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        self._ensure_process_role()
        self.logger.exception(msg, *args, **kwargs)

    def close(self) -> None:
        """Flush and close resources owned by the creating process."""
        if self._closed:
            return
        self._closed = True

        if os.getpid() != self._owner_pid:
            return

        if self._listener is not None:
            self._listener.stop()
            self._listener = None

        for handler in self._sink_handlers:
            try:
                handler.flush()
            finally:
                handler.close()
        self._sink_handlers = []
        self.logger.handlers.clear()

        if self._queue is not None:
            self._queue.close()
            self._queue.join_thread()

    def __enter__(self) -> "XLogger":
        return self

    def __exit__(self, exc_type, exc_value, exc_tb) -> None:
        self.close()

    def __getstate__(self):
        """Serialize only process-transfer-safe state for spawn/forkserver."""
        state = self.__dict__.copy()
        state["logger"] = None
        state["_listener"] = None
        state["_sink_handlers"] = []
        state["_closed"] = False
        return state

    def __setstate__(self, state) -> None:
        self.__dict__.update(state)
        self._configure_client()
