#!/usr/bin/env python
"""
APD 制御の上位API、DS
Mistral 中の APD 制御・連携に関するDS

  - DsArcPlasma を下位APIとして用いる
  - DsMistral を用いる

"""
import sys


# LOG = logging.getLogger(__name__)
from x_logger import XLogger


def main():
    logger = XLogger(log_level="DEBUG")

    logger.debug("debug AAAA")

if __name__ == "__main__":
    main()
