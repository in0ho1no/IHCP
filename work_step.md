# IHCP

## 開発

### テンプレートから作成後に実行する

workspace名の変更

    git mv wsXXX.code-workspace wsDST.code-workspace

### 環境準備

仮想環境を作成する

    uv venv --python 3.13

単体テスト環境を用意する

    uv pip install pytest

GUI環境を用意する

    uv pip install streamlit

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

## 対応している表記

HCPの記法に基づいてインデント(空白4つ∪タブ)でレベルを表現

### レベル0に記載できる表記

表記 | 内容 | 注意点
---| --- | ---
\module | モジュールの開始 | モジュール名とセットで必ず記載すること。

### レベル1以上に記載できる表記

表記 | 内容 | 注意点
---| --- | ---
\data | モジュール内で利用するデータの定義 | \in, \outで利用するデータは必ず定義すること。
\fork | 条件分岐 | -
\true | 条件分岐の条件が真の場合 | \branchでもよい
\false | 条件分岐の条件が偽の場合 | \branchでもよい
\branch | 条件分岐の条件が真偽以外の場合 | -
\repeat | 繰り返し | -
\mod | 関数呼び出し | -
\return | 処理の終了 | 関数の出口・繰り返し・caseの終了等に用いる

### レベル1以上に追加で記載できる表記

表記 | 内容 | 注意点
---| --- | ---
\in | 処理・関数への入力 | レベル1へ記載した場合、関数への入力として扱う。レベル2以上へ記載した場合、単なる処理の入力として扱う。
\out | 処理・関数からの出力 | レベル1へ記載した場合、関数からの出力として扱う。レベル2以上へ記載した場合、単なる処理の出力として扱う。

## GUI起動

仮想環境のターミナルにて以下コマンド実行する

    streamlit run <file-name>
