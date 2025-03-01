import re

from define import DataInfo, DiagramElement, InOutData, LineInfo


class SimpleDiagramParser:
    LEVEL_MIN = 0
    LEVEL_MAX = 9
    LEVEL_ERROR = -1
    LEVEL_NONE = -2

    TAB2SPACE = 4

    def __init__(self, text_data: str) -> None:
        self.lines = text_data.strip().split("\n")
        self.pair_line_level: list[tuple] = self.__set_pair_line_level()
        self.data_line: list[tuple] = self.__set_data_line(self.pair_line_level)
        self.process_line: list[tuple] = self.__set_process_line(self.pair_line_level)

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
        elif line_type_str.group() == "\\true":
            return (DiagramElement.TYPE_TRUE, line_elem[1])
        elif line_type_str.group() == "\\false":
            return (DiagramElement.TYPE_FALSE, line_elem[1])
        elif line_type_str.group() == "\\branch":
            return (DiagramElement.TYPE_BRANCH, line_elem[1])
        elif line_type_str.group() == "\\data":
            return (DiagramElement.TYPE_DATA, line_elem[1])
        else:
            # 該当しなければエラーとする
            print(f"{line_type_str.group()!r} is None")
            return (DiagramElement.TYPE_NORMAL, line)

    def get_line_io(self, line: str) -> InOutData:
        # \inと\outのパターンを抽出
        in_matches = re.finditer(r"\\in\s+(\w+)", line)  # マッチした全ての文字列をリストに格納
        out_matches = re.finditer(r"\\out\s+(\w+)", line)

        # データを対応するリストに格納
        in_data = [DataInfo(name=match.group(1)) for match in in_matches]  # マッチオブジェクトの2番目の要素を順に取り出したリストを連結
        out_data = [DataInfo(name=match.group(1)) for match in out_matches]

        # \inと\out要素を取り除いた行を取得
        cleaned_text = re.sub(r"\\(?:in|out)(?:\s+\w+)?", "", line).strip()

        return InOutData(in_data, out_data), cleaned_text

    def __set_pair_line_level(self) -> list[tuple]:
        pair_line_level: list[tuple] = []
        for line in self.lines:
            line_level = self.get_line_level(line)
            if self.LEVEL_MIN > line_level:
                continue

            line_type, line_org = self.get_line_type(line)
            inout_data, cleaned_text = self.get_line_io(line_org)

            pair = (line_level, cleaned_text, line_type, inout_data)  # ☆
            pair_line_level.append(pair)

        return pair_line_level

    def __set_data_line(self, pair_line_level_list: list[tuple]) -> list[tuple]:
        # データのみのリスト生成
        data_line_list: list[tuple] = []
        for pair_line_level in pair_line_level_list:
            if pair_line_level[2] == DiagramElement.TYPE_DATA:
                data_line_list.append(pair_line_level)

        return data_line_list

    def __set_process_line(self, pair_line_level_list: list[tuple]) -> list[tuple]:
        # 処理のみのリスト生成
        process_line_list: list[tuple] = []
        for pair_line_level in pair_line_level_list:
            if pair_line_level[2] != DiagramElement.TYPE_DATA:
                process_line_list.append(pair_line_level)

        return process_line_list

    def get_pair_line_level(self) -> list[tuple]:
        return self.pair_line_level

    def create_data_info_list(self) -> list[LineInfo]:
        line_info_list: list[LineInfo] = []

        for pair_line in self.data_line:
            line_info = LineInfo()
            line_info.no = len(line_info_list)
            line_info.level = pair_line[0]
            line_info.text = pair_line[1]
            line_info.category = pair_line[2]

            # 同じレベルで1つ前の番号を見つける
            for search_no in range(len(line_info_list) - 1, 0, -1):
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

    def create_process_info_list(self) -> list[LineInfo]:
        line_info_list: list[LineInfo] = []

        for pair_line in self.process_line:
            line_info = LineInfo()
            line_info.no = len(line_info_list)
            line_info.level = pair_line[0]
            line_info.text = pair_line[1]
            line_info.category = pair_line[2]
            line_info.iodata = pair_line[3]

            # 同じレベルで1つ前の番号を見つける
            for search_no in range(len(line_info_list) - 1, 0, -1):
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
