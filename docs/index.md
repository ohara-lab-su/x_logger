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
ある意味プログラムで一番中心となる根幹クラスライブラリである。

主に以下の機能を用意している。

- デバイスサーバー向け: ログのローテーション
- デバイスの制御クライアント向け: 単純にファイルにログを保存
- テスト用/サーバー用: ログの画面表示
- multiprocess で動作するプログラムから一つのログへの集約

同じ名前の logger を複数回生成した場合などでも、
handler が積み重なって同じログが多重に出力されないようにしている。

multiprocess では、一つの親 process で作成した logger を
複数の worker process に渡して使用できる。
各 process から出力されたログは一つのログへ集約される。

## 使い方

`print()` の代わりに logger を使うことで、
時刻、logger 名、PID、ログレベルとともに動作状況を記録できる。

### logging を使う

このロガーを使わず、Python 標準の logging を直接使う場合は、
例えば以下のように記述する。

```python
import logging

log_level = "INFO"
logging.basicConfig(level=log_level.upper())
logger = logging.getLogger(__name__)

logger.info("Hello")
```

フォーマット、ファイル保存、ローテーションなどを自分で設定する場合は、
Python 標準の logging を直接使用することもできる。

### x_logger を使う

基本的には `XLogger` を作成して `print()` の代わりに使用する。

```python
from x_logger import XLogger

logger = XLogger(
    log_level="INFO",
    logger_name="Sample",
)

logger.info("Hello")
logger.debug("DEBUG")
```

ログレベルが `INFO` の場合、`debug()` は出力されない。

```python
logger = XLogger(
    log_level="DEBUG",
    logger_name="Sample",
)

logger.info("Hello")
logger.debug("DEBUG")
```

ログレベルが `DEBUG` の場合は両方とも出力される。

ログレベルを実行中に変更する場合は `setLevel()` を使用する。

```python
logger.setLevel("DEBUG")
logger.debug("DEBUG")
```

画面やログファイルには、

```text
2026-03-05 10:24:54 Sample[138144] INFO Hello
```

のように、

```text
時刻 logger名[PID] ログレベル メッセージ
```

の形式で出力される。

`logger_name` は logger の名前である。
デバイスサーバーで使用する場合は、DeviceClass 名など、
そのログを識別できる名前を指定する。

### ログをファイル保存

`log_mode="file"` を指定すると、
画面表示と同時に指定したファイルへログを保存する。

```python
from x_logger import XLogger

logger = XLogger(
    log_level="INFO",
    log_mode="file",
    log_name="sample.log",
    logger_name="Sample",
)

logger.info("INFO")
logger.error("ERROR")
```

### ローテーション機能を使う

サーバーなどを長時間動作させる場合は、
一つのログファイルへ書き続けるのではなくログをローテーションする。

```python
from x_logger import XLogger

logger = XLogger(
    log_level="INFO",
    log_mode="rotating",
    log_name="device.log",
    backup_count=30,
    logger_name="DeviceSample",
)

logger.info("server started")
```

`rotating` は日付が変わるタイミングでログをローテーションする。

`rotate` も使用できる。

`backup_count` で保存する世代数を指定する。

### 同じ logger を再度作成する

同じ `logger_name` で `XLogger` を再度作成した場合も、
XLogger が作成した handler を整理してから再設定する。

```python
from x_logger import XLogger

logger = XLogger(
    log_mode="file",
    log_name="sample.log",
    logger_name="Sample",
)

logger = XLogger(
    log_mode="file",
    log_name="sample.log",
    logger_name="Sample",
)

logger.info("Hello")
```

この場合、最後の `Hello` が handler の多重登録によって
複数回出力されることはない。

### multiprocess で使う

一つのデバイスサーバーの中で複数 process を動作させる場合は、
`MultiProcessXLogger` を使用する。

親 process で logger を一つ作成し、
その logger インスタンスを各 worker process に渡す。

```python
import multiprocessing
import os

from x_logger.multiprocess import MultiProcessXLogger


def worker(logger, worker_name):
    logger.info(
        "%s pid=%d",
        worker_name,
        os.getpid(),
    )


def main():
    logger = MultiProcessXLogger(
        log_level="INFO",
        log_mode="rotating",
        log_name="device.log",
        backup_count=30,
        logger_name="DeviceSample",
        start_method="spawn",
    )

    context = multiprocessing.get_context("spawn")
    processes = []

    for index in range(3):
        process = context.Process(
            target=worker,
            args=(logger, "worker_%d" % index),
        )
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    logger.close()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
```

各 worker のログは同じ `DeviceSample` のログへ集約される。

ログに表示される PID は、実際にそのログを生成した process の PID になる。

file / rotating file への実際の出力は一か所に集約されるため、
複数 process が同じログファイルを直接操作する構成にはならない。

---
## 作者
- Kengo NAKADA
