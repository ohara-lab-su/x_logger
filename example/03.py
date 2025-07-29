#!/usr/bin/env python
"""
APD 制御の上位API、DS
Mistral 中の APD 制御・連携に関するDS

  - DsArcPlasma を下位APIとして用いる
  - DsMistral を用いる

"""
import sys


# LOG = logging.getLogger(__name__)
from x_logger.version import __version__
from x_logger.x_logger import XLogger


def test_xxx():
    logger = XLogger(
        log_level="INFO", log_mode="file", log_name="c:/Users/nakada/Desktop/aho"
    )
    print("debug")
    logger.log_level = "debug"
    logger.debug("debug AAAA")

    print("info")
    logger.log_level = "INFO"
    logger.info("INFO BBBB")
    logger.debug("DEBUG BBBB")

    print("")
    print("debug")
    logger.log_level = "debug"
    logger.info("INFO CCCC")
    logger.debug("DEBUG CCCC")
    print("")


if __name__ == "__main__":
    test_xxx()
