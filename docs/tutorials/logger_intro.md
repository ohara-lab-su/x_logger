# チュートリアル

ロガーの基本機能と使い方

## ログローテーション機能を使う

```python
from x_logger import XLogger


def test_xxx():
    logger = XLogger(
        log_level="INFO",
        log_mode="rotate",
        log_name="c:/Users/nakada/Desktop/aho_rotate.txt",
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
```