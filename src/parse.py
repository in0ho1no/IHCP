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

        # 処理部に記載されたin/outをdata部として追加しておく
        user_data_list: list[LineInfo] = []
        for process_line_info in self.process_line_info_list:
            for in_data in process_line_info.iodata.in_data_list:
                user_data = LineInfo()
                user_data.text_org = in_data.name
                user_data.level.value = self.data_level_min
                user_data.type = LineTypeDefine.get_format_by_type(LineTypeEnum.DATA)
                user_data.text_typeless = in_data.name
                user_data.text_clean = in_data.name
                user_data_list.append(user_data)

            for out_data in process_line_info.iodata.out_data_list:
                user_data = LineInfo()
                user_data.text_org = out_data.name
                user_data.level.value = self.data_level_min
                user_data.type = LineTypeDefine.get_format_by_type(LineTypeEnum.DATA)
                user_data.text_typeless = out_data.name
                user_data.text_clean = out_data.name
                user_data_list.append(user_data)

        for user_data in user_data_list:
            append_flg = True
            for line_info in self.data_line_info_list:
                if user_data.text_typeless == line_info.text_typeless:
                    append_flg = False
                    break

            if append_flg is True:
                self.data_line_info_list.append(user_data)

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

    @staticmethod
    def remove_duplicate_from_list(original_list: list[LineInfo]) -> list[LineInfo]:
        """リストから重複した要素を除外する

        Args:
            original_list (list[LineInfo]): 除外前のリスト

        Returns:
            list[LineInfo]: 除外後のリスト
        """
        removed_duplicate_list: list[LineInfo] = []
        check_name_list: list[str] = []  # 重複チェックを効率化するための名前用リスト
        for original in original_list:
            # 未登録の名前だけを新規リストへ登録する
            if original.text_clean not in check_name_list:
                removed_duplicate_list.append(original)
                check_name_list.append(original.text_clean)

        return removed_duplicate_list

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
        removed_duplicate_list = self.remove_duplicate_from_list(data_line_info_list)
        data_lines = removed_duplicate_list.copy()
        self.__assign_line_relationships(data_lines)
        return data_lines

    @staticmethod
    def get_level_min(info_list: list[LineInfo]) -> int:
        level_min: int = LineLevel.LEVEL_MAX
        for info in info_list:
            level_min = min(level_min, info.level.value)

        return level_min
