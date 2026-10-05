#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Multiprocessing support for XLogger."""
import logging
import multiprocessing
import os
from logging.handlers import QueueHandler, QueueListener
from typing import Any, Dict, List, Optional, Union

from .x_logger import (
    XLogger,
    _HANDLER_OWNER_ATTRIBUTE,
    _MULTIPROCESS_RUNTIME_ATTRIBUTE,
)


class MultiProcessXLogger(XLogger):
    """複数 process の LogRecord を一つの logical logger へ集約する。

    owner process が QueueListener と実際の出力 handler を保持し、child
    process は QueueHandler を介して LogRecord を owner 側へ送る。これにより
    console/file/rotating 出力を一か所で処理し、各 LogRecord の PID も保持する。

    Args:
        log_level: logging level。文字列または logging の整数 level を指定する。
        loglevel: ``log_level`` の互換 alias。``log_level`` が優先される。
        log_mode: ``default``、``file``、``rotating`` または ``rotate``。
        log_name: file/rotating mode で使用するログファイル名。
        backup_count: rotating mode で保持するバックアップ数。
        logger_name: Python logging の named logger 名。
        start_method: multiprocessing の start method。None は環境既定値を使う。
    """

    def __init__(
        self,
        log_level=None,
        loglevel=None,
        log_mode="default",
        log_name=None,
        backup_count=30,
        logger_name=None,
        start_method=None,
    ) -> None:
        effective_name = logger_name
        if effective_name is None:
            effective_name = "SimpleLogger"

        logger = logging.getLogger(effective_name)
        previous_runtime = getattr(
            logger,
            _MULTIPROCESS_RUNTIME_ATTRIBUTE,
            None,
        )
        if previous_runtime is not None:
            previous_runtime._shutdown_owner(logger)

        self.start_method = start_method
        self._owner_pid = os.getpid()
        self._client_pid = None  # type: Optional[int]
        self._listener = None  # type: Optional[QueueListener]
        self._sink_handlers = []  # type: List[logging.Handler]
        self._closed = False

        context = multiprocessing.get_context(self.start_method)
        self._queue = context.Queue()

        super().__init__(
            log_level=log_level,
            loglevel=loglevel,
            log_mode=log_mode,
            log_name=log_name,
            backup_count=backup_count,
            logger_name=logger_name,
        )

        self._sink_handlers = self._detach_output_handlers()
        self._install_queue_handler()
        self._listener = QueueListener(
            self._queue,
            *self._sink_handlers,
            respect_handler_level=True
        )
        self._listener.start()
        setattr(
            self.logger,
            _MULTIPROCESS_RUNTIME_ATTRIBUTE,
            self,
        )

    def _install_queue_handler(self) -> None:
        """現在の process の named logger に QueueHandler を接続する。"""
        queue_handler = QueueHandler(self._queue)
        queue_handler.setLevel(self._normalize_level(self.log_level))
        self._mark_handler(queue_handler)
        self.logger.addHandler(queue_handler)

    def _close_sink_handlers(self) -> None:
        """owner が保持する実出力 handler をすべて閉じる。"""
        for handler in self._sink_handlers:
            self._close_handler(handler)
        self._sink_handlers = []

    def _prepare_client_process(self) -> None:
        """fork 後の child process を QueueHandler 構成へ切り替える。"""
        current_pid = os.getpid()
        if current_pid == self._owner_pid:
            return
        if self._client_pid == current_pid:
            return

        self._close_sink_handlers()
        self._listener = None
        self._client_pid = current_pid

        self.logger = logging.getLogger(self.logger_name)
        self._remove_xlogger_handlers()
        self.logger.setLevel(self._normalize_level(self.log_level))
        self.logger.propagate = False
        self._install_queue_handler()

    def _shutdown_owner(self, logger: logging.Logger) -> None:
        """owner process の listener、handler、queue を順序よく終了する。"""
        if os.getpid() != self._owner_pid:
            return

        if self._listener is not None:
            self._listener.stop()
            self._listener = None

        self._close_sink_handlers()

        for handler in list(logger.handlers):
            if getattr(handler, _HANDLER_OWNER_ATTRIBUTE, False):
                logger.removeHandler(handler)
                self._close_handler(handler)

        runtime = getattr(
            logger,
            _MULTIPROCESS_RUNTIME_ATTRIBUTE,
            None,
        )
        if runtime is self:
            delattr(logger, _MULTIPROCESS_RUNTIME_ATTRIBUTE)

        if not self._closed:
            self._queue.close()
            self._queue.join_thread()
            self._closed = True

    def close(self) -> None:
        """現在の process が保持する multiprocessing logging 資源を閉じる。"""
        if self._closed:
            return

        current_pid = os.getpid()
        if current_pid == self._owner_pid:
            self._shutdown_owner(self.logger)
            return

        self._prepare_client_process()
        self._remove_xlogger_handlers()
        self._queue.close()
        self._queue.join_thread()
        self._closed = True

    def setLevel(self, level: Union[int, str]) -> None:
        """QueueHandler と owner 側 sink handler の logging level を変更する。"""
        self._prepare_client_process()
        super().setLevel(level)

        if os.getpid() == self._owner_pid:
            normalized_level = self._normalize_level(level)
            for handler in self._sink_handlers:
                handler.setLevel(normalized_level)

    def debug(
        self,
        msg: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """child process 構成を確認してから debug ログを出力する。"""
        self._prepare_client_process()
        super().debug(msg, *args, **kwargs)

    def info(
        self,
        msg: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """child process 構成を確認してから info ログを出力する。"""
        self._prepare_client_process()
        super().info(msg, *args, **kwargs)

    def warning(
        self,
        msg: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """child process 構成を確認してから warning ログを出力する。"""
        self._prepare_client_process()
        super().warning(msg, *args, **kwargs)

    def error(
        self,
        msg: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """child process 構成を確認してから error ログを出力する。"""
        self._prepare_client_process()
        super().error(msg, *args, **kwargs)

    def critical(
        self,
        msg: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """child process 構成を確認してから critical ログを出力する。"""
        self._prepare_client_process()
        super().critical(msg, *args, **kwargs)

    def exception(
        self,
        msg: str,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """child process 構成を確認してから exception ログを出力する。"""
        self._prepare_client_process()
        super().exception(msg, *args, **kwargs)

    def __getstate__(self) -> Dict[str, Any]:
        """spawn 用に listener と sink handler を除いた状態を返す。"""
        state = self.__dict__.copy()
        state["logger"] = None
        state["_listener"] = None
        state["_sink_handlers"] = []
        state["_client_pid"] = None
        state["_closed"] = False
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """spawn された child process で QueueHandler 構成を復元する。"""
        self.__dict__.update(state)
        self.logger = logging.getLogger(self.logger_name)
        self._remove_xlogger_handlers()
        self.logger.setLevel(self._normalize_level(self.log_level))
        self.logger.propagate = False
        self._client_pid = os.getpid()
        self._install_queue_handler()
