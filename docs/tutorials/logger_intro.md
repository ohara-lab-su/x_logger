# チュートリアル

ロガーの基本機能と使い方。

## 画面へログを表示する

```python
from x_logger import XLogger

logger = XLogger(
    log_level="INFO",
    logger_name="Sample",
)

logger.info("INFO")
logger.warning("WARNING")
logger.error("ERROR")
```

ログは以下の形式で表示される。

```text
2026-03-05 10:24:54 Sample[138144] INFO INFO
```

`[138144]` の部分はログを出力した process の PID。

## ログレベルを変更する

```python
from x_logger import XLogger

logger = XLogger(
    log_level="INFO",
    logger_name="Sample",
)

logger.info("INFO")
logger.debug("DEBUG")

logger.setLevel("DEBUG")

logger.info("INFO")
logger.debug("DEBUG")
```

最初の `DEBUG` は表示されず、
`setLevel("DEBUG")` より後の `DEBUG` は表示される。

## ファイルへ保存する

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

画面表示と同時に `sample.log` へ保存される。

## ログローテーション機能を使う

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

日付が変わるタイミングでログをローテーションする。

`log_mode="rotate"` も使用できる。

`backup_count` で保存する世代数を指定する。

## 同じ logger を複数回作成する

同じ `logger_name` で logger を繰り返し作成しても、
XLogger の handler が積み重ならないようにしている。

```python
from x_logger import XLogger

for index in range(5):
    logger = XLogger(
        log_level="INFO",
        log_mode="file",
        log_name="sample.log",
        logger_name="Sample",
    )
    logger.info(
        "configuration_%d",
        index,
    )

logger.info("FINAL")
```

`FINAL` は一回だけ出力される。

## multiprocess で使う

一つの Device Server の中で複数 process を使用する場合は、
`MultiProcessXLogger` を使用する。

logger は親 process で一つ作成し、
同じインスタンスを各 worker process に渡す。

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

親 process で作成した logger の Queue を各 worker が共有し、
各 process のログを一つの logical logger へ集約する。

例えば親 process が1件、
3個の worker がそれぞれ1件ずつログを出した場合、
保存されるログは合計4件になる。

同じログが handler の多重登録によって増えることはない。

ログフォーマットには PID が含まれているため、
どの process が生成したログかを確認できる。

## multiprocess のテスト

テストでは複数 worker から同時にログを出し、

- 全 worker のログが保存される
- 同じイベントが重複しない
- ログに記録された PID と worker の実 PID が一致する

ことを確認する。

例えば4 workerから5件ずつ出力した場合は、
20件すべてが保存され、各イベントは一回だけ存在することを確認する。

---
## 作者
- Kengo NAKADA
