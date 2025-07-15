import logging
import coloredlogs
from logging.handlers import TimedRotatingFileHandler

# root loggerへ一度だけ coloredlogs install（競合回避）
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
        log_mode="default",  # 'default'（画面のみ）, 'file', 'rotating'
        log_name=None,  # ファイル名
        backup_count=30,  # ローテート時の保存数（日数）
        logger_name=None,  # ロガー名
    ):
        if logger_name is None:
            logger_name = "SimpleLogger"
        self.logger = logging.getLogger(logger_name)
        for h in list(self.logger.handlers):
            self.logger.removeHandler(h)
        self.logger.setLevel(log_level.upper())
        fmt = "%(asctime)s %(name)s[%(process)d] %(levelname)s %(message)s"
        datefmt = "%Y-%m-%d %H:%M:%S"
        if log_mode == "file":
            if not log_name:
                raise ValueError("log_name must be specified for file mode")
            handler = logging.FileHandler(log_name, encoding="utf-8")
            handler.setFormatter(logging.Formatter(fmt, datefmt))
            self.logger.addHandler(handler)
            self.logger.propagate = False
        elif log_mode == "rotating":
            if not log_name:
                raise ValueError("log_name must be specified for rotating mode")
            handler = TimedRotatingFileHandler(
                log_name, when="midnight", backupCount=backup_count, encoding="utf-8"
            )
            handler.setFormatter(logging.Formatter(fmt, datefmt))
            self.logger.addHandler(handler)
            self.logger.propagate = False
        else:  # default: 標準出力はroot loggerのcoloredlogsへ流すだけ
            self.logger.propagate = True

    def get_logger(self):
        return self.logger

    def setLevel(self, level):
        self.logger.setLevel(level.upper() if isinstance(level, str) else level)
        for handler in self.logger.handlers:
            handler.setLevel(level.upper() if isinstance(level, str) else level)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.critical(msg)

    def exception(self, msg, *args, **kwargs):
        self.logger.exception(msg, *args, **kwargs)
