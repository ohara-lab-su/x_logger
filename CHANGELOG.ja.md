# CHANGELOG

## 2026.10.05, v0.3.0, nakada

- v0.2.15 を基準に logger 構成を再設計
- Python logging の named logger を基盤として `logger_name` を
  logical logger の識別名として統一
- XLogger が生成した handler を識別し、同一 logger の再設定時に
  XLogger 管理 handler のみを置換する構成へ変更
- `default`、`file`、`rotating` / `rotate` の既存出力モードを維持
- `file` と `rotating` は console への同時出力を維持
- `setLevel()` で logger と XLogger 管理 handler の level を同期
- multiprocessing 用 `MultiProcessXLogger` を `multiprocess.py` に追加
- multiprocessing では QueueHandler / QueueListener を使用し、
  file / rotating handler を owner process に集約
- `fork` と `spawn` の multiprocessing 構成に対応

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