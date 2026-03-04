
x logger (ロガー)
---

```{toctree}
:maxdepth: 2
:caption: Contents:

api/modules
tutorials/logger_intro
```

# シンプルで単純なロガー

プログラムの動作記録のための基本ソフトウエア。
ある意味プログラムで一番中心となる根幹クラスライブラリである

主に３つの機能を用意していある

- デバイスサーバー向け: ログのローテーション
- デバイスの制御クライアント向け: 単純にファイルにログを保存
- テスト用/サーバー用: ログの画面表示

## 使い方

このロガーの代わりに logging を使ってログ機能を使う時

```python

import logging

log_level = "INFO"
logging.basicConfig(level=log_level.upper())
logger = logging.getLogger(__name__)

logger.info("Hello")
```

ロガーを使う。

```
from xlogger import Logger
logger = Logger(log_level="INFO")

```

# 作者
- Kengo NAKADA (中田謙吾)
  - kengo.nakada@mat.shimane-u.ac.jp
  - kengo.nakada@gmail.com
