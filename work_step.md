# IHCP

## 開発環境準備

### 動作に必要な環境

仮想環境を作成する

    uv venv --python 3.13


GUI環境を用意する

    uv pip install streamlit

### 開発に必要な環境

単体テスト環境を用意する

    uv pip install pytest

設計図のリバース環境を用意する

    uv pip install pylint

## 開発途中の作業メモ

### 単体テスト

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

### 設計時のリバース

pyreverseを利用する  
https://pylint.readthedocs.io/en/latest/additional_tools/pyreverse/index.html

pyreverse は pylint に含まれるので先述した通り、uv仮想環境にpylintをインストールする。  

以下コマンドでsrcフォルダ以下のスクリプトファイルに基づいてクラス図・パッケージ図を生成する

    pyreverse -o svg ./src/

20250310時点でのバージョンは以下

    PS D:\work\Py\21IHCP\IHCP> pylint --version
    pylint 3.3.5
    astroid 3.3.9
    Python 3.13.2 (tags/v3.13.2:4f8bb39, Feb  4 2025, 15:23:48) [MSC v.1942 64 bit (AMD64)]

今回試した限りでは、以下のような出力先フォルダの指定は成功しなかった。

    pyreverse -o svg -d=./src/docs/img_reverse/ ./src/
    pyreverse -o svg --output-directory=./src/docs/img_reverse/ ./src/

出力後のファイル群は手動で移動させる。


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

batファイルも用意したので、以下ファイルをダブルクリックすることでも起動可能

    run_gui.bat
