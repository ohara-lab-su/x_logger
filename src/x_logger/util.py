#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""x_logger の補助ユーティリティ。"""
import os
import traceback
from types import SimpleNamespace
from typing import Any, Optional


def _noop_log(*args: Any, **kwargs: Any) -> None:
    """silent logger の各 logging method が使用する no-op 処理。"""
    return None


def get_silent_logger() -> SimpleNamespace:
    """何も出力しない logger 互換オブジェクトを返す。

    logger が任意指定の処理で、呼び出し側に ``None`` 判定を要求せず
    ``debug`` から ``critical`` までの基本 logging method を呼べるようにする。

    Returns:
        logging の基本 method を no-op として持つ SimpleNamespace。
    """
    methods = ["debug", "info", "warning", "error", "critical"]
    namespace = {}
    for method in methods:
        namespace[method] = _noop_log
    return SimpleNamespace(**namespace)


def safe_print_stack(limit: Optional[int] = 3) -> None:
    """現在の stack を取得し、各 frame の位置を標準出力へ表示する。

    実在するファイルは通常のファイル位置として表示し、実在しないパスは
    ``(not found)`` を付けて表示する。

    Args:
        limit: 取得する stack frame 数。None の場合は全 frame を取得する。
    """
    stack = traceback.extract_stack(limit=limit)
    for frame in stack:
        # traceback 上のパスが現在も実在するかを明示して表示する。
        if os.path.exists(frame.filename):
            print(
                "File: {}, Line: {}, in {}".format(
                    frame.filename,
                    frame.lineno,
                    frame.name,
                )
            )
        else:
            print(
                "File: {} (not found), Line: {}, in {}".format(
                    frame.filename,
                    frame.lineno,
                    frame.name,
                )
            )
