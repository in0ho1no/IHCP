# IHCP

## 開発

### テンプレートから作成後に実行する

workspace名の変更

    git mv wsXXX.code-workspace wsDST.code-workspace

README.mdのタイトルを変更する

### 環境準備

仮想環境を作成する

    pipenv --python 3.10

単体テスト環境を用意する

    pipenv install pytest

## 単体テスト

setup.pyファイルを用意して、以下記載する。

    from setuptools import setup, find_packages

    setup(
        name="parser-project",
        version="0.1",
        packages=find_packages(),
    )

各ディレクトリには、\__init__.pyを用意すること

上記後、以下コマンドを実行する

    pipenv install -e .

    -eは開発モードでパッケージをインストールする

実行時は仮想環境化で以下実行する

    pytest

各試験結果を個別に確認したい場合は -v オプションをつける
