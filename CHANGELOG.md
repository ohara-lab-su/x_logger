# CHANGELOG

## 2026.09.28, v0.3.0, nakada

### multiprocessing 対応と logger 独立性の再設計

v0.3.0 では、従来の `XLogger` の使用感を維持したまま、複数 logger と multiprocessing を安全に扱うため内部設計を再構築した。

#### 複数 XLogger インスタンスの独立化

従来は `logging.getLogger(logger_name)` を使用していたため、同じ `logger_name`（既定値 `SimpleLogger`）を持つ複数の `XLogger` は、Python logging 内部では同一の `logging.Logger` オブジェクトを共有していた。さらに `XLogger` 初期化時に既存 handler を削除していたため、後から生成した logger が先に存在する logger の handler 構成を変更する可能性があった。

v0.3.0 では各 `XLogger` が独立した `logging.Logger` を所有する。既定の表示名 `SimpleLogger` や公開 API は変更せず、インスタンス間の handler 干渉だけを根本から除去した。

この変更の思想は、「logger 名が同じであること」と「logger インスタンスが同一であること」を分離することである。装置制御では複数装置が同じ既定 logger 名を利用することは自然であり、そのことを理由に内部 handler まで共有されるべきではない。

#### multiprocessing 対応

`multiprocess=True` を追加した。

複数プロセスから同じログファイルを使用する場合でも、`FileHandler` / `TimedRotatingFileHandler` を各プロセスが直接共有・操作する設計にはしていない。特に rotation は単純な書き込み排他だけでは安全性を保証できないためである。

代わりに、`XLogger` を生成した owner process だけが実際の stream/file/rotating handler と `QueueListener` を所有し、子プロセスは `QueueHandler` から `LogRecord` を owner へ配送する。したがって「一つの logger オブジェクトや FileHandler を共有する」のではなく、「一つの論理ログへの経路を共有する」という設計である。

この方式により、一つの装置内部で親プロセスと補助プロセスが動作する場合でも、一つの装置ログへ安全に集約できる。既存フォーマットに含まれる PID により発生元プロセスも識別できる。

#### fork / spawn の双方を考慮

- `spawn` / `forkserver`: pickle 時に listener、sink handler、内部 `logging.Logger` を子へ持ち込まず、子側では Queue client を再構築する。
- `fork`: pickle が発生しないため、ログ利用時に PID の変化を検出し、fork された子を Queue client へ自動的に切り替える。

これにより、fork で親の file handler が継承された場合でも、子がその handler を直接使用しない。

#### シングルプロセスを標準とする思想は維持

`multiprocess=False` を既定値とした。x_logger の主要用途は一装置一プロセスであり、通常利用に multiprocessing Queue/Listener の複雑性とコストを常時持ち込まない。必要な装置だけ明示的に multiprocessing transport を有効化する。

これは「稀な高度利用のために通常利用を複雑にしない」「ただし高度利用を装置クラス側の特殊実装にも押し付けない」という v0.3.0 の基本方針である。

#### 責務の整理

multiprocessing logging の安全性は `ProcessExecutor` や `SharedContext` ではなく logger 側の責務とした。装置クラス・worker クラスは従来どおり `logger.info(...)` 等を呼ぶだけでよい。

これにより `ProcessExecutor` を使う場合だけでなく、直接 `multiprocessing.Process` を使うクラスでも同じ `XLogger` の仕組みを利用できる。

#### API

追加:

- `multiprocess=False`
- `start_method=None`
- `close()`
- context manager (`with XLogger(...) as logger:`)

既存の logging メソッド、getter、`loglevel` 互換、`rotate` / `rotating` 互換は維持した。

`start_method` を明示する場合は、logger を受け取る multiprocessing executor/process と同じ start method を使用する。異なる multiprocessing context 由来の Queue/SemLock を混在させないためである。

また、従来モジュール import 時に root logger へ `coloredlogs.install()` を行っていたグローバル副作用を廃止した。`XLogger` 自身が formatter/handler を所有する設計に統一し、x_logger を import しただけでアプリケーション全体の root logger 構成を書き換えない。

## 2026.07.28, v0.2.15, nakada

- after cobotta3/4 setup

## 2026.07.14, v0.2.14, nakada

- 八代研引き渡し版

## 2026.03.09, v0.2.13, nakada

- 出張前 FINALバージョン(2026.03.15)

## 2026.03.09, v0.2.12, nakada

ドキュメント調整

## 2026.03.04, v0.2.11, nakada

- loglevel オプションを導入(logging 互換)
  (内部的には log_level とする)

## 2026.02.06, v0.2.10, nakada

- logger設定が、画面の見時にうまく機能しないバグを修正

## 2026.01.08, v0.2.9, nakada

- logger.debug(self, msg, *args) のような標準 logger に修正

## 2025.11.06, v0.2.8, nakada

- symlink 方式を止める
 
## 2025.11.06, v0.2.7, nakada

- python 3.6 環境でネットワークなし環境で setup するために
  pyproject.toml 意外に setup.py を復活させた
  - symlink: プロジェクトルート/x_logger

## 2025.10.16, v0.2.6, nakada

- added sphinx module (project.toml)
 
## 2025.09.5, v0.2.5, nakada
 
- docs
 
## 2025.09.5, v0.2.4, nakada

- sphinx_docs: そもそもdocstringほとんど書いてないので意味がない

## 2025.09.1, v0.2.3, nakada

fix project.toml

## 2025.07.29, v0.2.2, nakada

- rotate / rotating どちらでもok

## 2025.07.29, v0.2.1, nakada

- log name 関連をインスタンス変数化(get_xxx できるように)

## 2025.07.29, v0.2.0, nakada

- v0.1.x でオミットしていた標準出力の同時出力機能(file/rotate) を追加修正

## v0.1.1, nakada

コンフリクト解消、testsコード追加

## v0.1.0, nakada

logger の多重と六関係が、
バグっていたので（マレにバグが顕在化）
再構築

## v0.0.2, nakada

util に適当に追加しておいたデバッグプリント系がいろいろと悪さをしていたので、回収

## v0.0.1, nakada

get_silent_logger() method をutilに追加