
from types import SimpleNamespace

def get_silent_logger():
    """ロガー指定がないときにロガーが何も吐き出さないようにする"""
    noop = lambda *args, **kwargs: None
    methods = ["debug", "info", "warning", "error", "critical"]
    return SimpleNamespace(**{m: noop for m in methods})
