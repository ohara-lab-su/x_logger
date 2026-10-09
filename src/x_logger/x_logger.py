#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XLogger

Python logging の named logger を基盤として、console、file、
TimedRotatingFileHandler を簡単に構成する。
"""
import logging
from logging.handlers import TimedRotatingFileHandler
from typing import Any, List, Optional, Union

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
    """Python logging の named logger を簡単に構成する logger。

    named logger に console/file/rotating handler を構成し、同じ
    ``logger_name`` で XLogger を再生成した場合も XLogger 自身が追加した
    handler を整理してから再構成する。

    Args:
        log_level: logging level。文字列または logging の整数 level を指定する。
        loglevel: ``log_level`` の互換 alias。``log_level`` が優先される。
        log_mode: ``default``、``file``、``rotating`` または ``rotate``。
        log_name: file/rotating mode で使用するログファイル名。
        backup_count: rotating mode で保持するバックアップ数。
        logger_name: Python logging の named logger 名。
    """

    def __init__(
        self,
        log_level=None,
        loglevel=None,
        log_mode="default",
        log_name=None,
        backup_count=30,
        logger_name=None,
    ) -> None:
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
    def _resolve_log_level(
        log_level: Optional[Union[int, str]],
        loglevel: Optional[Union[int, str]],
    ) -> Union[int, str]:
        """優先順位を適用して実際に使用する logging level を返す。"""
        if log_level is not None:
            return log_level
        if loglevel is not None:
            return loglevel
        return "INFO"

    @staticmethod
    def _normalize_level(level: Union[int, str]) -> Union[int, str]:
        """文字列 level を大文字へ正規化し、整数 level はそのまま返す。"""
        if isinstance(level, str):
            return level.upper()
        return level

    @staticmethod
    def _mark_handler(handler: logging.Handler) -> logging.Handler:
        """handler を XLogger 管理対象として識別できるように印を付ける。"""
        setattr(handler, _HANDLER_OWNER_ATTRIBUTE, True)
        return handler

    @staticmethod
    def _close_handler(handler: logging.Handler) -> None:
        """handler の flush と close を安全に実行する。"""
        try:
            handler.flush()
        except Exception:
            pass
        try:
            handler.close()
        except Exception:
            pass

    def _shutdown_previous_multiprocess_runtime(self) -> None:
        """同名 logger に残る multiprocessing runtime を停止する。"""
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

    def _remove_xlogger_handlers(self) -> None:
        """現在の named logger から XLogger 管理 handler だけを除去する。"""
        for handler in list(self.logger.handlers):
            if getattr(handler, _HANDLER_OWNER_ATTRIBUTE, False):
                self.logger.removeHandler(handler)
                self._close_handler(handler)

    def _stream_handler(self) -> logging.Handler:
        """色付き console 出力用 handler を生成する。"""
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

    def _file_handler(self) -> logging.Handler:
        """UTF-8 の通常ファイル出力用 handler を生成する。"""
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

    def _rotating_handler(self) -> logging.Handler:
        """毎日0時に切り替える rotating file handler を生成する。"""
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

    def _build_output_handlers(self) -> List[logging.Handler]:
        """log_mode に対応する出力 handler 群を生成する。"""
        handlers = []  # type: List[logging.Handler]

        if self.log_mode == "file":
            handlers.append(self._file_handler())
        elif self.log_mode == "rotating" or self.log_mode == "rotate":
            handlers.append(self._rotating_handler())

        handlers.append(self._stream_handler())
        return handlers

    def _attach_handlers(self, handlers: List[logging.Handler]) -> None:
        """生成済み handler 群を named logger に接続する。"""
        for handler in handlers:
            self.logger.addHandler(handler)

    def _detach_output_handlers(self) -> List[logging.Handler]:
        """XLogger 管理 handler を閉じずに logger から切り離して返す。"""
        handlers = []  # type: List[logging.Handler]
        for handler in list(self.logger.handlers):
            if getattr(handler, _HANDLER_OWNER_ATTRIBUTE, False):
                self.logger.removeHandler(handler)
                handlers.append(handler)
        return handlers

    def get_log_level(self) -> Union[int, str]:
        """現在設定されている logging level を返す。"""
        return self.log_level

    def get_log_mode(self) -> str:
        """現在のログ出力 mode を返す。"""
        return self.log_mode

    def get_log_name(self) -> Optional[str]:
        """設定されているログファイル名を返す。"""
        return self.log_name

    def get_backup_count(self) -> int:
        """rotating mode のバックアップ保持数を返す。"""
        return self.backup_count

    def get_logger_name(self) -> str:
        """使用している named logger 名を返す。"""
        return self.logger_name

    def get_logger(self) -> logging.Logger:
        """内部で使用している標準 logging.Logger を返す。"""
        return self.logger

    def setLevel(self, level: Union[int, str]) -> None:
        """logger と XLogger 管理 handler の logging level を変更する。"""
        self.log_level = level
        normalized_level = self._normalize_level(level)
        self.logger.setLevel(normalized_level)
        for handler in self.logger.handlers:
            if getattr(handler, _HANDLER_OWNER_ATTRIBUTE, False):
                handler.setLevel(normalized_level)

    def debug(
        self,
        msg: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """標準 logging.Logger.debug() へメッセージを渡す。"""
        self.logger.debug(msg, *args, **kwargs)

    def info(
        self,
        msg: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """標準 logging.Logger.info() へメッセージを渡す。"""
        self.logger.info(msg, *args, **kwargs)

    def warning(
        self,
        msg: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """標準 logging.Logger.warning() へメッセージを渡す。"""
        self.logger.warning(msg, *args, **kwargs)

    def error(
        self,
        msg: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """標準 logging.Logger.error() へメッセージを渡す。"""
        self.logger.error(msg, *args, **kwargs)

    def critical(
        self,
        msg: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """標準 logging.Logger.critical() へメッセージを渡す。"""
        self.logger.critical(msg, *args, **kwargs)

    def exception(
        self,
        msg: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """標準 logging.Logger.exception() へメッセージを渡す。"""
        self.logger.exception(msg, *args, **kwargs)
