
import builtins
import traceback
from types import SimpleNamespace

def get_silent_logger():
    """ロガー指定がないときにロガーが何も吐き出さないようにする"""
    noop = lambda *args, **kwargs: None
    methods = ["debug", "info", "warning", "error", "critical"]
    return SimpleNamespace(**{m: noop for m in methods})



def tracing_print(*args, **kwargs):
    original_print("🔍 print() called with:", *args)
    traceback.print_stack(limit=3)  # 直近3フレームだけ表示（必要に応じて増やす）
    original_print(*args, **kwargs)


original_print = builtins.print
builtins.print = tracing_print