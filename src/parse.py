import re

MAX_LEVEL = 9
ERROR_LEVEL = MAX_LEVEL + 1
TAB2SPACE = 4


def create_indent_pattern(tab_count: int) -> str:
    """インデントパターンを動的に生成する

    行頭は タブ*n個 もしくは 半角空白m個 で、任意の文字が続いて行末 となるパターン

    Args:
        tab_count (int): タブの数

    Returns:
        str: 生成したインデントパターンの正規表現
    """
    # タブと半角スペースを変換する
    space_count = tab_count * TAB2SPACE

    # 正規表現を作成する
    # {}の数、書き方に注意
    # f-stringの置換の為に変数名の前後に1組必要
    # さらに、直前の文字がn個続く表現{n}を表すために、{}を2重で記載する必要がある。
    # 間に空白を含むとエラーになるので、{}を3組連続で記載することになる。
    # pattern = f"^( {{{space_count}}}|\t{{{tab_count}}})"
    pattern = f"^( {{{space_count}}}|\t{{{tab_count}}})\\S.*$"
    return pattern


def get_line_level(line: str) -> int:
    """与えられた行のレベルを取得する

    インデントの記載に誤りがあればエラーを返す

    Args:
        line (str): レベルを取得したい行

    Returns:
        int: タブの数(半角空白なら4文字)をレベルとして返す
    """
    # 初期化
    matched = False

    # レベル0から順にインデントをチェックする
    for level in range(0, MAX_LEVEL):
        tab_count = level
        pattern = create_indent_pattern(tab_count)
        result = re.match(pattern, line)
        if result is not None:
            matched = True
            break

    # 該当しなければエラーとする
    if matched is False:
        level = ERROR_LEVEL

    # 結果を返す
    return level
