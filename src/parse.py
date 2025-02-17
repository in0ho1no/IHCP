import re

from define import LineInfo


class SimpleDiagramParser:
    LEVEL_MIN = 0
    LEVEL_MAX = 9
    LEVEL_ERROR = -1
    LEVEL_NONE = -2

    TAB2SPACE = 4

    def __init__(self, text_data: str) -> None:
        self.lines = text_data.strip().split("\n")
        self.pair_line_level: list[tuple] = self.__set_pair_line_level()

    @staticmethod
    def create_indent_pattern(tab_count: int) -> str:
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
        space_count = tab_count * SimpleDiagramParser.TAB2SPACE

        # 正規表現を作成する
        # {}の数、書き方に注意
        # f-stringの置換の為に変数名の前後に1組必要
        # さらに、直前の文字がn個続く表現{n}を表すために、{}を2重で記載する必要がある。
        # 間に空白を含むとエラーになるので、{}を3組連続で記載することになる。
        pattern = f"^(?:[ ]{{{space_count}}}|\t{{{tab_count}}})\\S.*$"
        return pattern

    @classmethod
    def get_line_level(cls, line: str) -> int:
        """与えられた行のレベルを取得する

        インデントの記載に誤りがあればエラーを返す

        Args:
            line (str): レベルを取得したい行

        Returns:
            int: タブの数(半角空白なら4文字)をレベルとして返す
        """
        # 空行は無視する
        if not line or not line.strip():
            return cls.LEVEL_NONE

        # レベル0から順にインデントをチェックする
        for level in range(cls.LEVEL_MIN, cls.LEVEL_MAX):
            # レベルに応じたチェックパターンを生成する
            tab_count = level
            pattern = cls.create_indent_pattern(tab_count)

            # 該当したレベルを返す
            if re.match(pattern, line) is not None:
                return level

        # 該当しなければエラーとする
        return cls.LEVEL_ERROR

    def __set_pair_line_level(self) -> list[tuple]:
        pair_line_level: list[tuple] = []
        for line in self.lines:
            line_level = self.get_line_level(line)
            if self.LEVEL_MIN > line_level:
                continue

            pair = (line_level, line)
            pair_line_level.append(pair)

        return pair_line_level

    def get_pair_line_level(self) -> list[tuple]:
        return self.pair_line_level

    def create_line_info_list(self) -> list[LineInfo]:
        line_info_list: list[LineInfo] = []

        start_count = 0
        for num, pair_line in enumerate(self.pair_line_level, start=start_count):
            line_info = LineInfo()
            line_info.no = num
            line_info.level = pair_line[0]
            line_info.text = pair_line[1]

            if num > start_count:
                # 同じレベルで1つ前の番号を見つける
                print(line_info.text)
                for search_no in range(num - 1, start_count, -1):
                    search_info = line_info_list[search_no]
                    if search_info.level == line_info.level:
                        line_info.before_no = search_info.no
                        print(line_info.before_no)
                        break
                    elif search_info.level < line_info.level:
                        # 自身よりレベルが小さいなら階層が変わる
                        break

            line_info_list.append(line_info)

        return line_info_list
