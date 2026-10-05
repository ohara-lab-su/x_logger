# XLogger samples and duplicate-prevention tests

XLogger / MultiProcessXLogger の使用例と、多重出力防止の確認用プログラムです。

## ファイル

- `single_sample.py`
  - `default` / `file` / `rotating` の基本使用例
  - `setLevel()` の使用例

- `duplicate_prevention_sample.py`
  - 同じ `logger_name` の XLogger を意図的に何度も生成
  - handler が積み重なりやすい条件を作る
  - 最後の marker がファイルへ1回だけ記録されたことを確認

- `multiprocess_sample.py`
  - Device Server で1個の MultiProcessXLogger を生成
  - logger インスタンスを3 worker へ渡す
  - 全 worker のログを一つの logical logger へ集約
  - ログ本文にも worker PID を出し、目視確認可能

- `test_duplicate_prevention.py`
  - single-process の自動テスト
  - 同一 logger_name を10回再構成しても marker が1件だけ
  - file + console の2 handler だけであることを確認
  - 異なる logger_name のファイルが混ざらないことを確認
  - `propagate=False` を確認

- `test_multiprocess.py`
  - multiprocessing の自動テスト
  - 4 worker × 5 events = 20 events を生成
  - 20件すべてが残ることを確認
  - 同じ event が2回存在しないことを確認
  - ログフォーマット `[PID]` と worker の実 PID が一致することを確認
  - worker PID の集合とログ中 PID の集合が一致することを確認
  - `spawn` を確認
  - 利用可能な環境では `fork` も確認

## 実行

プロジェクトの import path から `x_logger` package を参照できる状態で実行します。

```text
python single_sample.py
python duplicate_prevention_sample.py
python multiprocess_sample.py
python test_duplicate_prevention.py
python test_multiprocess.py
```

特に `test_multiprocess.py` は、「ログが出た」だけではなく、
各 worker が生成した全イベントが欠落せず、かつ重複せず、
生成元 PID を保持していることを件数と内容の両方で検証します。
