# CHANGELOG

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