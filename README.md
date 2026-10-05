# x_logger

[ohara-lab-su](https://ohara-lab-su.github.io/)/
[x_logger](https://ohara-lab-su.github.io/x_logger/)

## 名前の由来

`daruma` 用 logger、`elves` 用の `el_logger` など、プロジェクトごとに
作成していた logger の共通機能をまとめ、用途を限定しない logger として
再構築したものが `x_logger` です。

`x` は任意・汎用の用途を表しています。また、他に適当な名前が
思いつかなかった、という単純な理由もあります。

## はじめに

`x_logger` は Python 標準の `logging` を基盤にした logger です。
`logger_name` を logical logger の識別名として扱い、console、file、
TimedRotatingFileHandler を簡単に構成できます。

同じ `logger_name` は同じ named logger を表します。異なる
`logger_name` は別の logger として扱われます。

デバイス用途では、`logger_name` にデバイスクラス名を使用することを
基本とします。これにより、ログ保存、multiprocessing、将来のログ閲覧
サーバーで同じ logical logger 名を一貫して使用できます。

## Single-process logger

通常は `XLogger` を使用します。

```python
from x_logger.x_logger import XLogger

logger = XLogger(
    logger_name="Cobotta",
    log_mode="rotating",
    log_name="Cobotta.log",
)

logger.info("started")
```

`XLogger` のインスタンスを他のクラスへ渡して使用することもできます。
ただし logger の論理的な識別はインスタンスではなく `logger_name` です。

### log_mode

`default` は console のみに出力します。

`file` は指定したファイルと console の両方へ出力します。単独の
ファイル保存用途として利用でき、デバイスサーバーやログ閲覧サーバーを
必要としません。

`rotating` または `rotate` は TimedRotatingFileHandler と console の
両方へ出力します。rotation は midnight、保存数は `backup_count` で
指定します。

## Handler management

XLogger が生成した handler には XLogger 管理用の識別情報を付与します。
同じ `logger_name` を XLogger で再設定した場合は、以前の XLogger handler
を閉じてから新しい構成へ置き換えます。

これにより、XLogger を再生成したことで console handler や file handler
が積み重なることを防ぎます。

named logger は `propagate = False` とし、XLogger の出力が root logger を
経由して再度 console へ出力される経路を遮断します。

root logger の coloredlogs 設定はプロセス内で一度だけ行います。

## Multiprocessing logger

multiprocessing 用には別クラス `MultiProcessXLogger` を使用します。
Single-process の `XLogger` と出力モード、logger name、level、format の
考え方を共通化しています。

```python
from x_logger.multiprocess import MultiProcessXLogger

logger = MultiProcessXLogger(
    logger_name="Cobotta",
    log_mode="rotating",
    log_name="Cobotta.log",
)
```

multiprocessing では各 process が file handler を持つ構成にはせず、
各 process からの LogRecord を QueueHandler で owner process へ送ります。
owner process の QueueListener だけが console/file/rotating handler を
所有します。

```text
parent process ---\
child process 1 ---+--> Queue --> QueueListener --> console
child process 2 ---/                         |
                                             +--> file / rotating file
```

この構成により、一つの logical logger に対する file 出力と rotation の
所有者を一つに保ちます。

`fork` では child process に継承された file handler を閉じ、QueueHandler
経由へ切り替えます。`spawn` では復元された logger に QueueHandler を
設定します。

multiprocessing の処理、Queue、QueueListener、process 判定、終了処理は
`multiprocess.py` に分離しています。

## Logical logger とログ閲覧

デバイスシステムでは、基本的にデバイスクラス名を `logger_name` として
使用します。

```text
Cobotta
  -> logger_name: Cobotta
  -> log storage: <prefix>/Cobotta/...

Camera
  -> logger_name: Camera
  -> log storage: <prefix>/Camera/...
```

将来のログ閲覧サーバーでは、この logical logger 名を基準に、現在の
ログと rotation 済みログを gRPC 等から参照できる構成を想定します。

XLogger はログの生成と保存を担当し、ログ閲覧サーバーは保存された
logical log stream の公開を担当します。
