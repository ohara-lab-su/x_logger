# x logger (ロガー)
view on [github](https://github.com/ohara-lab-su/x_logger/) / [ohara-lab-su (doc)](https://ohara-lab-su.github.io/)


---
```{toctree}
:maxdepth: 2
:caption: Contents:

api/modules
tutorials/logger_intro
```
---

# シンプルで単純なロガー

プログラムの動作記録のための基本ソフトウエア。
ある意味プログラムで一番中心となる根幹クラスライブラリである

主に３つの機能を用意していある

- デバイスサーバー向け: ログのローテーション
- デバイスの制御クライアント向け: 単純にファイルにログを保存
- テスト用/サーバー用: ログの画面表示

ロガーを複数立ち上げてしまうとおかしくなる現象を避けるために、
いろいろな工夫をしているのでわりと堅牢なロガーになっている（と思う）

## 使い方

print() の代わりに logger を使うことで、時間とクラスやメソッドの情報などを含めて
全ての状況を記録することが可能です。

### logging を使う

このロガーの代わりに単純に logging を使ってログ機能を使う時

```python

import logging

log_level = "INFO"
logging.basicConfig(level=log_level.upper())
logger = logging.getLogger(__name__)

logger.info("Hello")
```

自分でフォーマッタを含めて、毎回全てを記述するならば、そのまま logging を素で使うのでも構わないがあまり現実ではない。
特にマルチプロセスやマルチスレッド環境では注意する必要がある。

### x_logger を使う時にロガーの基礎

print の代わりに使います。loglvel で切り替えることができます。

```python
from x_logger import Logger
logger = Logger(log_level="INFO")
```

ログレベル info だと
```python
from x_logger import Logger
logger = Logger(log_level="INFO")
logger.info("Hello")
logger.debug("DEBUG")
```

今はログレベルが info なので、```logger.debug('DEBUG')``` は表示されない。

```python
logger = Logger(log_level="debug")
logger.info("Hello")
logger.debug("DEBUG")
```

このときはログレベルが debug なので、```logger.debug('DEBUG')``` は表示される

画面上には
```text
2026-03-05 10:24:54 JoyPadClient[138144] INFO [Frame:GrpcClient][joypad_send_dpose] completed
```

のように、時間と使っているプログラム名・クラス名などとともに、
どの状態のログなのか？が表示できる

### ログをファイル保存

```python
def test_xxx():
    logger = XLogger(
        log_level="INFO",
        log_mode="file",
        log_name="c:/Users/nakada/Desktop/aho_file",
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
指定ファイルに保存される

### ローテーション機能を使う

サーバーなどを立ち上げっぱなしだとログファイルのサイズが大きくなってします。
そのためのローテーションという作業を行う

```aiignore
log20260306
log20260307
log20260308
```

などの日付ごとなど、いろいろな設定が可能であるが。
とりあえずデフォルトで良い。

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

# 作者
- Kengo NAKADA (中田謙吾)
  - kengo.nakada@mat.shimane-u.ac.jp
  - kengo.nakada@gmail.com
