#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XLogger

Python logging の named logger を基盤として、console、file、
TimedRotatingFileHandler を簡単に構成する。
"""
import logging
from logging.handlers import TimedRotatingFileHandler
from typing import List, Optional, Union

import coloredlogs


_LOG_FORMAT = (
    "%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s"
)
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
_HANDLER_OWNER_ATTRIBUTE = "_x_logger_handler"
_MULTIPROCESS_RUNTIME_ATTRIBUTE = "_x_logger_multiprocess_runtime"


# root logger の coloredlogs 設定はプロセス内で一度だけ行う。
if not getattr(logging, "_coloredlogs_installed", False):
    logging.getLogger().handlers.clear()
    coloredlogs.install(
        level="INFO",
        logger=logging.getLogger(),
        fmt=_LOG_FORMAT,
        datefmt=_DATE_FORMAT,
    )
    logging.getLogger().setLevel(logging.INFO)
    setattr(logging, "_coloredlogs_installed", True)


class XLogger:
    """Python logging の named logger を簡単に構成する logger。"""

    def __init__(
        self,
        log_level=None,
        loglevel=None,
        log_mode="default",
        log_name=None,
        backup_count=30,
        logger_name=None,
    ):
        self.log_level = self._resolve_log_level(log_level, loglevel)
        self.log_mode = log_mode
        self.log_name = log_name
        self.backup_count = backup_count
        self.logger_name = logger_name

        if self.logger_name is None:
            self.logger_name = "SimpleLogger"

        self.logger = logging.getLogger(self.logger_name)
        self._shutdown_previous_multiprocess_runtime()
        self._remove_xlogger_handlers()
        self.logger.setLevel(self._normalize_level(self.log_level))
        self.logger.propagate = False

        handlers = self._build_output_handlers()
        self._attach_handlers(handlers)

    @staticmethod
    def _resolve_log_level(log_level, loglevel):
        if log_level is not None:
            return log_level
        if loglevel is not None:
            return loglevel
        return "INFO"

    @staticmethod
    def _normalize_level(level):
        if isinstance(level, str):
            return level.upper()
        return level

    @staticmethod
    def _mark_handler(handler):
        setattr(handler, _HANDLER_OWNER_ATTRIBUTE, True)
        return handler

    @staticmethod
    def _close_handler(handler):
        try:
            handler.flush()
        except Exception:
            pass
        try:
            handler.close()
        except Exception:
            pass

    def _shutdown_previous_multiprocess_runtime(self):
        runtime = getattr(
            self.logger,
            _MULTIPROCESS_RUNTIME_ATTRIBUTE,
            None,
        )
        if runtime is None:
            return

        shutdown = getattr(runtime, "_shutdown_owner", None)
        if shutdown is not None:
            shutdown(self.logger)

    def _remove_xlogger_handlers(self):
        for handler in list(self.logger.handlers):
            if getattr(handler, _HANDLER_OWNER_ATTRIBUTE, False):
                self.logger.removeHandler(handler)
                self._close_handler(handler)

    def _stream_handler(self):
        handler = logging.StreamHandler()
        handler.setLevel(self._normalize_level(self.log_level))
        try:
            formatter = coloredlogs.ColoredFormatter(
                _LOG_FORMAT,
                _DATE_FORMAT,
            )
        except Exception:
            formatter = logging.Formatter(
                _LOG_FORMAT,
                _DATE_FORMAT,
            )
        handler.setFormatter(formatter)
        return self._mark_handler(handler)

    def _file_handler(self):
        if not self.log_name:
            raise ValueError("log_name must be specified for file mode")

        handler = logging.FileHandler(
            self.log_name,
            encoding="utf-8",
        )
        handler.setLevel(self._normalize_level(self.log_level))
        handler.setFormatter(
            logging.Formatter(_LOG_FORMAT, _DATE_FORMAT)
        )
        return self._mark_handler(handler)

    def _rotating_handler(self):
        if not self.log_name:
            raise ValueError(
                "log_name must be specified for rotating mode"
            )

        handler = TimedRotatingFileHandler(
            self.log_name,
            when="midnight",
            backupCount=self.backup_count,
            encoding="utf-8",
        )
        handler.setLevel(self._normalize_level(self.log_level))
        handler.setFormatter(
            logging.Formatter(_LOG_FORMAT, _DATE_FORMAT)
        )
        return self._mark_handler(handler)

    def _build_output_handlers(self):
        handlers = []  # type: List[logging.Handler]

        if self.log_mode == "file":
            handlers.append(self._file_handler())
        elif self.log_mode == "rotating" or self.log_mode == "rotate":
            handlers.append(self._rotating_handler())

        handlers.append(self._stream_handler())
        return handlers

    def _attach_handlers(self, handlers):
        for handler in handlers:
            self.logger.addHandler(handler)

    def _detach_output_handlers(self):
        handlers = []  # type: List[logging.Handler]
        for handler in list(self.logger.handlers):
            if getattr(handler, _HANDLER_OWNER_ATTRIBUTE, False):
                self.logger.removeHandler(handler)
                handlers.append(handler)
        return handlers

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
        return self.logger

    def setLevel(self, level):
        self.log_level = level
        normalized_level = self._normalize_level(level)
        self.logger.setLevel(normalized_level)
        for handler in self.logger.handlers:
            if getattr(handler, _HANDLER_OWNER_ATTRIBUTE, False):
                handler.setLevel(normalized_level)

    def debug(self, msg: str, *args, **kwargs) -> None:
        self.logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        self.logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        self.logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        self.logger.error(msg, *args, **kwargs)

    def critical(self, msg: str, *args, **kwargs) -> None:
        self.logger.critical(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        self.logger.exception(msg, *args, **kwargs)
