import re

from define import DiagramElement, LineInfo


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
        strip_line = line.strip()
        if strip_line is None:
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

    @classmethod
    def get_line_type(cls, line: str) -> tuple[DiagramElement, str]:
        """与えられた行の種別を取得する

        想定しない種別の場合はエラーを返す

        Args:
            line (str): 種別を取得したい行

        Returns:
            int: タブの数(半角空白なら4文字)をレベルとして返す
        """
        # 空行は無視する
        strip_line = line.strip()
        if strip_line is None:
            return (DiagramElement.TYPE_NORMAL, line)

        # 種別指定が区切られていない行は無視する
        if " " not in strip_line:
            return (DiagramElement.TYPE_NORMAL, line)

        # 行から先頭要素を取得する
        line_elem = strip_line.split(" ", maxsplit=1)
        first_elem = line_elem[0]

        # 種別指定のない行は無視する
        line_type_str = re.match("^\\\\.*$", first_elem)
        if line_type_str is None:
            return (DiagramElement.TYPE_NORMAL, line)

        if line_type_str.group() == "\\fork":
            return (DiagramElement.TYPE_FORK, line_elem[1])
        elif line_type_str.group() == "\\repeat":
            return (DiagramElement.TYPE_REPEAT, line_elem[1])
        elif line_type_str.group() == "\\mod":
            return (DiagramElement.TYPE_MOD, line_elem[1])
        elif line_type_str.group() == "\\return":
            return (DiagramElement.TYPE_RETURN, line_elem[1])
        else:
            # 該当しなければエラーとする
            print(f"{line_type_str.group()!r} is None")
            return (DiagramElement.TYPE_NORMAL, line)

    def __set_pair_line_level(self) -> list[tuple]:
        pair_line_level: list[tuple] = []
        for line in self.lines:
            line_level = self.get_line_level(line)
            if self.LEVEL_MIN > line_level:
                continue

            line_type, line_org = self.get_line_type(line)
            line = line_org

            pair = (line_level, line, line_type)
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
            line_info.category = pair_line[2]

            if num > start_count:
                # 同じレベルで1つ前の番号を見つける
                for search_no in range(num - 1, start_count, -1):
                    if line_info_list[search_no].level == line_info.level:
                        # 1つ前の番号を保持する
                        line_info.before_no = line_info_list[search_no].no
                        # 同時に次の番号として保存する
                        line_info_list[search_no].next_no = line_info.no
                        break
                    elif line_info_list[search_no].level < line_info.level:
                        # 自身よりレベルが小さいなら階層が変わる
                        break

            line_info_list.append(line_info)

        return line_info_list
