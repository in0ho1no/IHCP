import re

from define import DataInfo, DiagramElement, InOutData, LineInfo


class SimpleDiagramParser:
    def __init__(self, text_data: str) -> None:
        self.line_info_list: list[LineInfo] = self.convert_text2lines(text_data)
        self.update_line_level()

        self.pair_line_level: list[tuple] = self.__set_pair_line_level()
        self.data_line: list[tuple] = self.__set_data_line(self.pair_line_level)
        self.process_line: list[tuple] = self.__set_process_line(self.pair_line_level)

    def convert_text2lines(self, text: str) -> list[LineInfo]:
        """テキストデータから空行を除いた文字列リストを保持する

        Args:
            text (str): 変換元のテキストデータ

        Returns:
            list[str]: 空行を除いた文字列リスト
        """
        line_info_list: list[LineInfo] = []
        for text_line in text.strip().split("\n"):
            # 空行は無視する
            strip_line = text_line.strip()
            if len(strip_line) == 0:
                continue

            line_info = LineInfo()
            line_info.text = text_line
            line_info_list.append(line_info)

        return line_info_list

    def update_line_level(self) -> None:
        for line_info in self.line_info_list:
            line_info.level.set_line_level(line_info.text)

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
            # 重複は弾きたい
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
        for line_info in self.line_info_list:
            line_type, line_org = self.get_line_type(line_info.text)
            inout_data, cleaned_text = self.get_line_io(line_org)

            pair = (line_info.level.lv, cleaned_text, line_type, inout_data)  # ☆
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
