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

        # 処理部とデータ部のリストを保持
        self.process_line_info_list = self.create_process_info_list()
        self.data_line_info_list = self.create_data_info_list()

        # 処理部とデータ部の最小レベルを保持
        self.process_level_min = self.get_level_min(self.process_line_info_list)
        self.data_level_min = self.get_level_min(self.data_line_info_list)

        # 処理部のみに記載されたin/outをdata部の情報として追加
        self.merge_iodata_dataline()

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
    def __remove_duplicate_from_list(original_list: list[LineInfo]) -> list[LineInfo]:
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

    def create_process_info_list(self) -> list[LineInfo]:
        """処理部の情報をリストにして返す

        Returns:
            list[LineInfo]:処理部の情報リスト
        """
        process_line_info_list = self.__categorize_line_info_process()
        process_lines = process_line_info_list.copy()
        self.__assign_line_relationships(process_lines)
        return process_lines

    def create_data_info_list(self) -> list[LineInfo]:
        """データ部の情報をリストにして返す

        Returns:
            list[LineInfo]: データ部の情報リスト
        """
        data_line_info_list = self.__categorize_line_info_data()
        data_lines = self.__remove_duplicate_from_list(data_line_info_list)
        self.__assign_line_relationships(data_lines)
        return data_lines

    @staticmethod
    def get_level_min(info_list: list[LineInfo]) -> int:
        """リスト内の最小レベルを取得する

        Args:
            info_list (list[LineInfo]): 最小レベルを取得したいリスト

        Returns:
            int: リスト内の最小レベル
        """
        level_min: int = LineLevel.LEVEL_MAX
        for info in info_list:
            level_min = min(level_min, info.level.value)

        return level_min

    def __create_io_data_info_list(self) -> list[LineInfo]:
        """処理部のin/outからdataの情報リストを作成する

        Returns:
            list[LineInfo]: 作成したdataの情報リスト
        """

        def create_data_info(data_name: str) -> LineInfo:
            """データ名に基づいて、データ部に相当する情報を作成する

            Args:
                data_name (str): データ名

            Returns:
                LineInfo: 作成したdataの情報
            """
            data_info = LineInfo()
            data_info.text_org = data_name
            data_info.level.value = self.data_level_min
            data_info.type = LineTypeDefine.get_format_by_type(LineTypeEnum.DATA)
            data_info.text_typeless = data_name
            data_info.text_clean = data_name
            return data_info

        io_data_info_list: list[LineInfo] = []
        for process_line_info in self.process_line_info_list:
            # \inを\data情報化
            for in_data in process_line_info.iodata.in_data_list:
                io_data_info = create_data_info(in_data.name)
                io_data_info_list.append(io_data_info)

            # \outを\data情報化
            for out_data in process_line_info.iodata.out_data_list:
                io_data_info = create_data_info(out_data.name)
                io_data_info_list.append(io_data_info)

        return io_data_info_list

    def __append_iodata_to_orgdata(self, io_data_list: list[LineInfo]) -> None:
        """入出力データリストのデータをデータ部のリストへ追加する

        Args:
            io_data_list (list[LineInfo]): 入出力データのリスト
        """
        for io_data in io_data_list:
            # データ部のリストからデータ部の名前だけのリストを用意する
            # データ部のリストは都度更新する想定なので、名前だけリストも繰り返し文の中で都度生成する。
            data_info_name_list = [data_info.text_clean for data_info in self.data_line_info_list]

            # 名前だけリストに存在しないデータをデータ部のリストへ追加する
            if io_data.text_clean not in data_info_name_list:
                self.data_line_info_list.append(io_data)

    def merge_iodata_dataline(self) -> None:
        """処理部のみに記載されたin/outをdata部の情報として追加する"""
        io_data_info_liset = self.__create_io_data_info_list()
        self.__append_iodata_to_orgdata(io_data_info_liset)
