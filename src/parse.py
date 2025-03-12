import re

from define import DataInfo, InOutData, LineInfo
from line_level import LineLevel
from line_type import LineType, LineTypeDefine, LineTypeEnum


class DiagramParser:
    def __init__(self, text_lines: list[str]) -> None:
        self.line_info_list: list[LineInfo] = self.convert_lines2lineinfo(text_lines)
        self.update_line_level()
        self.update_line_type()
        self.update_line_io()

        self.process_line_info_list = self.create_process_info_list_no()
        self.data_line_info_list = self.create_data_info_list_no()

        self.process_level_min = self.get_level_min(self.process_line_info_list)
        self.data_level_min = self.get_level_min(self.data_line_info_list)

    @staticmethod
    def convert_lines2lineinfo(lines: list[str]) -> list[LineInfo]:
        """文字列リストを文字列情報リストに変換する

        Args:
            lines (list[str]): 文字列リスト

        Returns:
            list[LineInfo]: 文字列情報リスト
        """
        line_info_list: list[LineInfo] = []
        for line in lines:
            line_info = LineInfo()
            line_info.text_org = line
            line_info_list.append(line_info)

        return line_info_list

    def update_line_level(self) -> None:
        """処理部のレベルをインデントに応じて決定する"""
        for line_info in self.line_info_list:
            line_info.level.value = LineLevel.get_line_level(line_info.text_org)

    def update_line_type(self) -> None:
        """処理部の種別を決定する"""
        for line_info in self.line_info_list:
            line_info.type, line_info.text_typeless = LineType.get_line_type(line_info.text_org)

    def update_line_io(self) -> None:
        """処理部の入出力情報を決定する"""
        for line_info in self.line_info_list:
            # \inと\outのパターンを抽出
            in_matches = re.finditer(r"\\in\s+([\w\-()]+)", line_info.text_typeless)  # マッチした全ての文字列をリストに格納
            out_matches = re.finditer(r"\\out\s+([\w\-()]+)", line_info.text_typeless)

            # データを対応するリストに格納
            in_data = [DataInfo(name=match.group(1)) for match in in_matches]  # マッチオブジェクトの2番目の要素を順に取り出したリストを連結
            out_data = [DataInfo(name=match.group(1)) for match in out_matches]

            # \inと\out要素を取り除いた行を取得
            cleaned_text = re.sub(r"\\(?:in|out)(?:\s+[\w\-()]+)?", "", line_info.text_typeless).strip()

            line_info.iodata = InOutData(in_data, out_data, line_info.level.value)
            line_info.text_clean = cleaned_text

    def __categorize_line_info_process(self) -> list[LineInfo]:
        """処理のみのリスト生成

        Returns:
            list[LineInfo]: 処理のみのリスト
        """
        process_line_info_list: list[LineInfo] = []
        for line_info in self.line_info_list:
            if line_info.type.type_value != LineTypeDefine.get_format_by_type(LineTypeEnum.DATA).type_value:
                process_line_info_list.append(line_info)

        return process_line_info_list

    def __categorize_line_info_data(self) -> list[LineInfo]:
        """データのみのリスト生成

        Returns:
            list[LineInfo]: データのみのリスト
        """
        # データのみのリスト生成
        data_line_info_list: list[LineInfo] = []
        for line_info in self.line_info_list:
            if line_info.type.type_value == LineTypeDefine.get_format_by_type(LineTypeEnum.DATA).type_value:
                data_line_info_list.append(line_info)

        return data_line_info_list

    @staticmethod
    def __assign_line_relationships(line_info_list: list[LineInfo]) -> None:
        """各行のレベルに応じた前後関係を決定する

        Args:
            line_info_list (list[LineInfo]): 処理部のリストもしくはデータ部のリスト
        """
        for count, line_info in enumerate(line_info_list):
            line_info.no = count

            # 同じレベルで1つ前の番号を見つける
            for search_idx in range(count - 1, -1, -1):
                search_line = line_info_list[search_idx]

                if search_line.level.value == line_info.level.value:
                    # 1つ前の番号を保持する
                    line_info.before_no = search_line.no
                    # 同時に次の番号として保存する
                    search_line.next_no = line_info.no
                    break
                elif search_line.level.value < line_info.level.value:
                    # 自身よりレベルが小さいなら階層が変わる
                    break

    def create_process_info_list_no(self) -> list[LineInfo]:
        """処理の行のリストに番号を割り当てて返す

        Returns:
            list[LineInfo]: 番号が割り当てられた処理の行のリスト
        """
        process_line_info_list = self.__categorize_line_info_process()
        process_lines = process_line_info_list.copy()
        self.__assign_line_relationships(process_lines)
        return process_lines

    def create_data_info_list_no(self) -> list[LineInfo]:
        """データの行のリストに番号を割り当てて返す

        Returns:
            list[LineInfo]: 番号が割り当てられたデータの行のリスト
        """
        data_line_info_list = self.__categorize_line_info_data()
        data_lines = data_line_info_list.copy()
        self.__assign_line_relationships(data_lines)
        return data_lines

    @staticmethod
    def get_level_min(info_list: list[LineInfo]) -> int:
        level_min: int = LineLevel.LEVEL_MAX
        for info in info_list:
            level_min = min(level_min, info.level.value)

        return level_min
