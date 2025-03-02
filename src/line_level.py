import re


class LineLevel:
    LEVEL_MIN = 0
    LEVEL_MAX = 20
    LEVEL_ERROR = -1
    LEVEL_NONE = -2

    TAB2SPACE = 4

    def __init__(self) -> None:
        self.lv: int = 0

    def __create_indent_pattern(self, tab_count: int) -> str:
        """インデントパターンを動的に生成する

        行頭は タブ*n個 もしくは 半角空白m個 で、任意の文字が続いて行末 となるパターン

        Args:
            tab_count (int): タブの数

        Returns:
            str: 生成したインデントパターンの正規表現

        Raises:
            ValueError: tab_countが負の数の場合
        """
        if tab_count < 0:
            raise ValueError("tab_count must be non-negative")

        # タブと半角スペースを変換する
        space_count = tab_count * self.TAB2SPACE

        # 正規表現を作成する
        # {}の数、書き方に注意
        # f-stringの置換の為に変数名の前後に1組必要
        # さらに、直前の文字がn個続く表現{n}を表すために、{}を2重で記載する必要がある。
        # 間に空白を含むとエラーになるので、{}を3組連続で記載することになる。
        pattern = f"^(?:[ ]{{{space_count}}}|\t{{{tab_count}}})\\S.*$"
        return pattern

    def get_line_level(self, line: str) -> int:
        """与えられた行のレベルを取得する

        インデントの記載に誤りがあればエラーを返す

        Args:
            line (str): レベルを取得したい行

        Returns:
            int: タブの数(半角空白なら4文字)をレベルとして返す
        """
        # 空行は無視する
        strip_line = line.strip()
        if strip_line is None:
            return self.LEVEL_NONE

        # レベル0から順にインデントをチェックする
        for level in range(self.LEVEL_MIN, self.LEVEL_MAX):
            # レベルに応じたチェックパターンを生成する
            tab_count = level
            pattern = self.__create_indent_pattern(tab_count)

            # 該当したレベルを返す
            if re.match(pattern, line) is not None:
                return level

        raise ValueError(f"Wrong indent pattern: {line}")

    def set_line_level(self, line: str) -> None:
        self.lv = self.get_line_level(line)
