#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
    based on DARUMA EmLogger

    coloredlogs はデフォルトで root ロガーにハンドラをインストールする
    つまり、ルートの fmt 関係をいじっているので
    自前で、かならず coloredlogs を通して操作する

Kengo NAKADA, kengo.nakada@mat.shimane-u.ac.jp, kengo.nakada@gmail.com
"""
# from control.logger import MyLogger

import sys
import os
import platform

import multiprocessing
import coloredlogs
import logging
import logging.handlers
from logging.handlers import TimedRotatingFileHandler

from x_logger.version import __version__

coloredlogs.CAN_USE_BOLD_FONT = True

coloredlogs.DEFAULT_FIELD_STYLES = {'asctime': {'color': 'green'},
                                    'hostname': {'color': 'magenta'},
                                    'levelname': {'color': 'black', 'bold': True},
                                    'name': {'color': 'blue'},
                                    'ProcessName': {'color': 'blue'},
                                    'programname': {'color': 'cyan'}
                                    }
coloredlogs.DEFAULT_LEVEL_STYLES = {'critical': {'color': 'red', 'bold': True},
                                    'error': {'color': 'red'},
                                    'warning': {'color': 'yellow'},
                                    'notice': {'color': 'magenta'},
                                    'info': {},
                                    'debug': {'color': 'green'},
                                    'spam': {'color': 'green', 'faint': True},
                                    'success': {'color': 'green', 'bold': True},
                                    'verbose': {'color': 'blue'}
                                    }


class HostnameFormatter(logging.Formatter):
    def format(self, record):
        # record.hostname = os.environ.get('HOSTNAME', 'unknown_host')
        record.hostname = platform.node()
        return super().format(record)


class XLogger(object):
    """

    """

    def __init__(
            self,
            log_level: str = 'info',
            log_mode: str = 'default',
            log_format: str = None,
            log_name: str = 'elves_log',
            app_name: str = None,
            logger_name: str = None,
    ):
        """

        Args:
            log_level (str):
            log_mode (str): default, rotating
            log_format (str):
            log_name (str): ログ名 (file for windows) systemd がない環境向け(あっても使える)
            app_name (str):  ログ名 (Eventlog for Windows)
            logger_name (str):
        """
        # create logger instance
        if logger_name is None:
            # logger_name = __name__
            logger_name = 'e'

        # ロガー取得
        self._logger = logging.getLogger(logger_name)
        # self._logger = logging.getLogger(os.path.splitext(os.path.basename(__file__))[0])
        # self._logger = multiprocessing.get_logger()

        # log rotating 用のデフォルトカウント
        self._backup_count = 365 * 5  # 365日*3 backup 保存

        self.app_name = None
        self.init_default_logger(log_level=log_level, log_mode=log_mode, log_name=log_name, app_name=app_name)

    @property
    def coloredlogs(self):
        return coloredlogs

    def get_logger(self):
        return self._logger

    def init_default_logger(
            self,
            log_level=None,
            log_mode=None,
            log_name='log',
            app_name=None
    ):
        """
        ログローテート対応のファイル出力 ＆ 標準出力(color)
        
        Args:
            log_level:
            log_mode:
            log_name:
            app_name:

        Returns:

        """
        # print("")
        # print("INIT logger")
        # print("ElLogger = %s" % ElLogger.version())
        # print("")

        if log_level is None:
            log_level = 'INFO'
        if app_name is None:
            app_name = 'python: ' + str(self.__class__.__name__)

        self.app_name = app_name
        self.log_level = log_level

        #################################
        # colorings (stdout)
        #################################
        coloredlogs.DEFAULT_LOG_FORMAT = '[%(asctime)s] %(hostname)s ' \
                                         '%(name)s[%(process)d] %(levelname)s ' \
                                         '%(message)s'

        # default level is INFO (ルートロガーを書き換える)
        coloredlogs.install(log_level, logger=self._logger)

        if log_mode == 'rotating':
            # logrotate (file)
            # 取得したロガー（ある名前の）に対してローテーションするハンドラーを加える
            # 主にサーバープロセス用

            rotating_handler = TimedRotatingFileHandler(
                # TimedRotatingFileHandlerを使うときは、ログファイル名に拡張子を付けてはいけない
                # 'log/myapp',  # logフォルダが存在しないとエラーになるので注意。また、拡張子があると古いファイルが削除されてくれないので注意。
                log_name,  # logフォルダが存在しないとエラーになるので注意。また、拡張子があると古いファイルが削除されてくれないので注意。
                when='midnight',  # S=秒, M=分, H=時, D=日, midnight=夜中
                # backupCount=7,  # when='midnight', interval=1だと1ファイルが1日分なので7日分保持することになる
                backupCount=self._backup_count,
                interval=1,  # when='midnight' なので1日でローテーションという意味になる
                encoding='utf-8')

            formatter = HostnameFormatter(
                '[%(asctime)s] %(hostname)s %(name)s %(levelname)s %(message)s',
                style='%'
            )
            rotating_handler.setFormatter(formatter)
            self._logger.addHandler(rotating_handler)

        if log_mode == 'file':
            # simple output for client process
            # ローテーションしない基本的にファイル書き出し（主にクラアントプロセス用）

            handler = logging.FileHandler(log_name, 'w', 'utf-8')
            handler.setFormatter(
                logging.Formatter('%(asctime)s : %(levelname)s : %(message)s', datefmt='%Y/%m/%d %H:%M:%S')
            )
            self._logger.addHandler(handler)

        self._logger.debug(__file__)
        self._logger.debug('set log_level = %s' % log_level)

        return self._logger

    def set_backup_count(self, val):
        self._backup_count = val

    def get_backup_count(self):
        return self._backup_count

    backup_count = property(get_backup_count, set_backup_count)

    def setLevel(self, log_level):
        coloredlogs.set_level(log_level)

    def set_log_level(self, log_level):
        coloredlogs.set_level(log_level)

    def get_log_level(self):
        return coloredlogs.get_level()

    log_level = property(get_log_level, set_log_level)

    def set_fmt(self, fmt):
        """ for coloredlogs """
        coloredlogs.DEFAULT_LOG_FORMAT = fmt

    def get_fmt(self):
        """ for coloredlogs """
        return coloredlogs.DEFAULT_LOG_FORMAT

    # for coloredlogs
    fmt = property(get_fmt, set_fmt)

    @property
    def logger(self):
        return self._logger

    def info(self, val):
        return self._logger.info(val)

    @property
    def INFO(self):
        return logging.INFO

    def debug(self, val):
        return self._logger.debug(val)

    @property
    def DEBUG(self):
        return logging.DEBUG

    def error(self, val):
        return self._logger.error(val)

    @property
    def WARNING(self):
        return logging.WARNING

    def warning(self, val):
        return self._logger.warning(val)

    def critical(self, val):
        return self._logger.critical(val)

    @property
    def CRITICAL(self):
        return logging.CRITICAL

    def get_version(self):
        return __version__

    @classmethod
    def version(cls):
        return __version__

    #
    # support func
    #

    def chk_windows(self):
        return self.is_windows()

    def is_windows(self):
        """
            windows のチェック
        """
        WIN = False
        try:
            sys.getwindowsversion()
        except Exception:
            pass
        else:
            WIN = True

        return WIN
