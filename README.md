# x_logger

[ohara-lab-su](https://ohara-lab-su.github.io/) / [x_logger](https://ohara-lab-su.github.io/x_logger/)

## はじめに

`x_logger` は、装置制御・実験制御コードから Python の logging を簡単に利用するための薄いラッパーです。

v0.3.0 では従来 API を維持したまま、内部設計を整理し、次の二点を重点的に改修しました。

1. 複数の `XLogger` インスタンスを同時に安全に利用できるようにする。
2. 一つの装置・一つの論理ログを、親プロセスと子プロセスから安全に利用できるようにする。

基本思想は、利用側のクラスに logging の内部事情を持ち込まないことです。装置クラスは従来どおり `logger.info(...)` 等を呼ぶだけで、ファイル排他、ログ配送、ローテーションの所有者といった問題は `XLogger` 側が担当します。

## 基本的な使い方

```python
from x_logger import XLogger

logger = XLogger()
logger.info("start")
logger.warning("warning")
```

デフォルトでは標準出力だけに出力します。

### ファイル出力

```python
logger = XLogger(
    log_mode="file",
    log_name="device.log",
)
```

`file` モードではファイルと標準出力の両方へ出力します。

### 日次ローテーション

```python
logger = XLogger(
    log_mode="rotating",
    log_name="device.log",
    backup_count=30,
)
```

`rotate` も従来どおり `rotating` の別名として使用できます。

### ログレベル

```python
logger = XLogger(log_level="DEBUG")
```

従来互換の `loglevel` も使用できます。

```python
logger = XLogger(loglevel="DEBUG")
```

両方を指定した場合は `log_level` を優先します。

## v0.3.0: 複数 XLogger インスタンスの独立性

v0.2.x 以前では、内部で `logging.getLogger("SimpleLogger")` を使用していました。Python の `logging.getLogger()` は同名 logger をプロセス全体で共有するため、次の二つは実際には同じ `logging.Logger` を参照していました。

```python
instance1 = XLogger()
instance2 = XLogger()
```

さらに初期化時に既存 handler を削除していたため、後から作成した `instance2` が `instance1` の handler を変更・削除する可能性がありました。

v0.3.0 では、各 `XLogger` が独立した `logging.Logger` オブジェクトを所有します。表示上の既定 logger 名 `SimpleLogger` は変更していません。

したがって次の利用は、それぞれ独立した logger として扱われます。

```python
instance1 = XLogger(log_mode="file", log_name="dev1.log")
dev1 = DeviceClass1("dev1class", logger=instance1)

instance2 = XLogger(log_mode="file", log_name="dev2.log")
dev2 = DeviceClass2("dev2class", logger=instance2)
```

`instance2` の生成によって `instance1` の handler が書き換えられることはありません。

## multiprocessing 対応

### なぜ通常の FileHandler 共有では不十分か

複数プロセスが同じ `FileHandler` や `TimedRotatingFileHandler` を直接操作する設計は採用していません。

特にローテーションでは、複数プロセスが同時に「日付が変わったのでファイルを rename する」と判断する可能性があります。単純な書き込み Lock だけでは、handler が持つ状態や rotation 処理まで安全に統一できません。

v0.3.0 では、multiprocessing 利用時の責務を次のように分けています。

```text
main process                         child process

XLogger owner                        XLogger client
    |                                    |
    |                               QueueHandler
    |                                    |
    +----------- Queue <-----------------+
    |
QueueListener
    |
    +-- StreamHandler
    +-- FileHandler / TimedRotatingFileHandler
```

ファイルやローテーション handler を所有するのは、`XLogger` を生成した owner process だけです。子プロセスは `LogRecord` を Queue へ送るだけです。

このため、親・子からのログを一つのファイルへ集約しながら、実ファイル操作は一プロセスに限定できます。

### multiprocessing を有効にする

```python
logger = XLogger(
    log_mode="rotating",
    log_name="device.log",
    multiprocess=True,
)
```

通常利用では `multiprocess=False` がデフォルトです。そのため、ほとんどがシングルプロセスである既存の装置クラスに Queue や listener のコストを追加しません。

### 親と子で同じ論理 logger を使う

```python
import multiprocessing
from x_logger import XLogger


def worker(logger):
    logger.info("message from worker")


if __name__ == "__main__":
    logger = XLogger(
        log_mode="file",
        log_name="device.log",
        multiprocess=True,
        start_method="spawn",
    )

    ctx = multiprocessing.get_context("spawn")

    logger.info("message from parent")

    process = ctx.Process(target=worker, args=(logger,))
    process.start()
    process.join()

    logger.close()
```

親と子の両方のレコードが `device.log` に入ります。フォーマットには従来から PID (`%(process)d`) が含まれるため、どのプロセスから出力されたかも識別できます。

### spawn と fork

v0.3.0 は両方を考慮しています。

`spawn` / `forkserver` では、`XLogger` が pickle される際に listener、handler、内部 `logging.Logger` を子へ複製せず、子では QueueHandler のみを再構築します。

`fork` では Python の pickle 経路を通らないため、ログ出力時に PID を確認します。生成元 PID と異なる場合は、そのプロセスを自動的に Queue client へ切り替えます。これにより fork で継承されたファイル handler を子が直接使用することを防ぎます。

### start_method

別の multiprocessing フレームワークで start method を明示している場合、`XLogger` にも同じ start method を指定してください。

```python
logger = XLogger(
    log_mode="file",
    log_name="device.log",
    multiprocess=True,
    start_method="spawn",
)

executor = ProcessExecutor(
    ...,
    start_method="spawn",
)
```

これは multiprocessing の Queue/SemLock を異なる context 間で混在させないためです。

## ProcessExecutor / 装置クラスとの責務分離

multiprocessing logging は原則として logger 側の責務です。

`ProcessExecutor` や `SharedContext` に「ログファイルを安全に扱うための仕組み」を実装すると、executor が logging 実装へ依存し、直接 `multiprocessing.Process` を使う別の装置クラスでは同じ問題を再実装することになります。

したがって v0.3.0 の設計では、装置側は従来どおり logger を dependency として受け取ります。

```python
logger = XLogger(
    log_mode="rotating",
    log_name="device.log",
    multiprocess=True,
    start_method="spawn",
)

device = DeviceClass("device", logger=logger)
```

worker constructor へ logger を渡す必要がある構造では、通常の引数として渡します。

```python
executor = ProcessExecutor(
    worker_class=DeviceWorker,
    worker_kwargs={"logger": logger},
    start_method="spawn",
)
```

`DeviceWorker` 側は multiprocessing-aware な logging コードを書く必要はありません。

```python
class DeviceWorker:
    def __init__(self, logger):
        self.logger = logger

    def execute(self):
        self.logger.info("execute")
```

つまり共有するのは「同じ FileHandler」ではなく「同じ論理ログへの経路」です。

## logger の終了

multiprocessing モードでは owner process に QueueListener が存在します。明示的に `close()` することを推奨します。

```python
logger.close()
```

context manager も利用できます。

```python
with XLogger(
    log_mode="file",
    log_name="device.log",
    multiprocess=True,
) as logger:
    logger.info("running")
```

`close()` は owner process だけが listener、handler、Queue を終了します。子プロセスが owner の資源を close することはありません。

## 公開 API

従来 API は維持しています。

```text
debug()
info()
warning()
error()
critical()
exception()
setLevel()

get_log_level()
get_log_mode()
get_log_name()
get_backup_count()
get_logger_name()
get_logger()
```

v0.3.0 では次を追加しています。

```text
multiprocess=...
start_method=...
close()
context manager (__enter__ / __exit__)
```

## 設計原則

v0.3.0 で重視しているのは次の三点です。

- **既存利用を壊さない。** シングルプロセスでは従来と同じ書き方を維持する。
- **装置クラスに logging の都合を漏らさない。** multiprocessing の安全性は logger が担当する。
- **一つの装置を一つの論理ログとして扱えるようにする。** 複数プロセスであっても、ファイル handler 自体を共有するのではなく、ログレコードを owner に集約する。

通常の一装置一プロセスを複雑化せず、必要な装置だけ multiprocessing transport を有効にする、というのが v0.3.0 系の基本方針です。
