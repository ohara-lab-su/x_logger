#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Logger

DARUMA Logger ->  Em Logger --> X Logger -> simple iba`版で再構築

Kengo NAKADA, kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
import logging
import coloredlogs
from logging.handlers import TimedRotatingFileHandler

# root logger へ coloredlogs install（競合回避）
if not getattr(logging, "_coloredlogs_installed", False):
    logging.getLogger().handlers.clear()
    coloredlogs.install(
        level="INFO",
        logger=logging.getLogger(),
        fmt="%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logging.getLogger().setLevel(logging.INFO)
    setattr(logging, "_coloredlogs_installed", True)


class XLogger:
    def __init__(
        self,
        log_level="INFO",
        log_mode="default",  # 'default', 'file', 'rotating'
        log_name=None,  # ファイル名
        backup_count=30,  # ローテート時の保存数（日数）
        logger_name=None,  # ロガー名
    ):
        self.log_level = log_level
        self.log_mode = log_mode
        self.log_name = log_name
        self.backup_count = backup_count
        self.logger_name = logger_name

        if self.logger_name is None:
            self.logger_name = "SimpleLogger"
        self.logger = logging.getLogger(self.logger_name)

        for h in list(self.logger.handlers):
            self.logger.removeHandler(h)
        self.logger.setLevel(self.log_level.upper())

        fmt = "%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"

        if self.log_mode == "file":
            if not self.log_name:
                raise ValueError("log_name must be specified for file mode")

            # ファイル出力
            handler_file = logging.FileHandler(self.log_name, encoding="utf-8")
            handler_file.setFormatter(logging.Formatter(fmt, datefmt))
            self.logger.addHandler(handler_file)

            # 標準出力にも同時出力（coloredlogsフォーマットで！）
            handler_stream = logging.StreamHandler()
            handler_stream.setFormatter(coloredlogs.ColoredFormatter(fmt, datefmt))
            self.logger.addHandler(handler_stream)
            self.logger.propagate = False

        elif self.log_mode == "rotating" or self.log_mode == "rotate":
            if not self.log_name:
                raise ValueError("log_name must be specified for rotating mode")
            # print(f"log_name = {log_name}")

            handler_rot = TimedRotatingFileHandler(
                self.log_name,
                when="midnight",
                backupCount=self.backup_count,
                encoding="utf-8",
            )
            handler_rot.setFormatter(logging.Formatter(fmt, datefmt))
            self.logger.addHandler(handler_rot)

            # 標準出力にも同時出力（coloredlogsフォーマットで！）
            handler_stream = logging.StreamHandler()
            handler_stream.setFormatter(coloredlogs.ColoredFormatter(fmt, datefmt))
            self.logger.addHandler(handler_stream)
            self.logger.propagate = False

        else:  # 'default'（画面のみ）: root loggerに流すだけ
            self.logger.propagate = True

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
        self.logger.setLevel(level.upper() if isinstance(level, str) else level)
        for handler in self.logger.handlers:
            handler.setLevel(level.upper() if isinstance(level, str) else level)

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

