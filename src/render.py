from define import Coordinate, DataInfo, DiagramElement, Line, LineInfo, Process2Data
from draw_svg import DrawFigure, DrawSvg
from line_type import LineTypeDefine, LineTypeEnum


class SVGRenderer:
    LINE_OFFSET = 10
    color_table = [
        "black",
        "red",
        "green",
        "blue",
        "yellow",
        "purple",
        "orange",
        "turquoise",
    ]

    def __init__(self, process_info_list: list[LineInfo], data_info_list: list[LineInfo]) -> None:
        # ヘッダは最後に挿入する
        # svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" style="background-color: #AFC0B1">']
        self.svg: list[str] = []

        self.draw_svg = DrawSvg()
        self.draw_fig = DrawFigure(self.draw_svg)

        self.process_info_list: list[LineInfo] = process_info_list
        self.data_info_list: list[LineInfo] = data_info_list

    def set_elements(self, start_x: int, start_y: int, line_info_list: list[LineInfo]) -> list[DiagramElement]:
        """各要素の配置を計算して保持する

        Args:
            start_x (int): 描画開始位置(X座標)
            start_y (int): 描画開始位置(Y座標)
            line_info_list (list[LineInfo]): 配置情報を更新したいリスト

        Returns:
            list[DiagramElement]: 配置情報を更新したリスト
        """
        element_list: list[DiagramElement] = []
        for line_info in line_info_list:
            element = DiagramElement(line_info)
            element.x = start_x + element.line_info.level * (DiagramElement.LEVEL_SHIFT)
            element.y = start_y + len(element_list) * (DiagramElement.LEVEL_SHIFT)
            element_list.append(element)

        return element_list

    def render_process(self) -> tuple[int, int]:
        """処理部を描画する

        Returns:
            tuple[int, int]: 処理部を描画した状態の画像サイズ(高さ, 幅)
        """
        process_height = 0
        process_width = 0
        for element in self.process_elements:
            # 種別に応じた図形とテキストを描画
            element.end_x = self.draw_fig.draw_figure_method(self.svg, element)

            # ステップ間の垂直線の追加
            if element.line_info.before_no != LineInfo.DEFAULT_VALUE:
                bef_elem = self.process_elements[element.line_info.before_no]
                # 直前のレベルまで線を引く
                self.draw_svg.draw_line_v(
                    self.svg,
                    element.x,
                    (bef_elem.y + DrawSvg.CIRCLE_R),
                    (element.y - DrawSvg.CIRCLE_R) - (bef_elem.y + DrawSvg.CIRCLE_R),
                )

            # 始点の追加
            if (element.line_info.before_no == LineInfo.DEFAULT_VALUE) and (element.line_info.level == 0):
                self.draw_svg.draw_figure_level_start(self.svg, element.x, element.y)

            # 終点の追加
            if element.line_info.next_no == LineInfo.DEFAULT_VALUE:
                if element.line_info.type.type_value == LineTypeDefine.get_format_by_type(LineTypeEnum.RETURN).type_value:
                    # \returnは図として終点を描画する
                    pass
                else:
                    self.draw_svg.draw_figure_level_end(self.svg, element.x, element.y)

            # レベル下げの追加
            if (element.line_info.level > 0) and (element.line_info.before_no == LineInfo.DEFAULT_VALUE):
                self.draw_svg.draw_figure_level_step(self.svg, element.x, element.y)

            # 処理部の高さと幅を更新する
            process_height = max(process_height, element.y)
            process_width = max(process_width, element.end_x)

        return process_height, process_width

    def render_line_exit_from_process(self, process_end_x: int) -> int:
        """処理部に対する入出力線を描画する

        Args:
            process_end_x (int): 入出力線の描画開始位置(X座標)

        Returns:
            int: 処理部の入出力線を描画した状態の画像幅
        """
        offset = 0
        exit_width = 0
        color_cnt = 0

        def process_io_line(element: DiagramElement, data_list: list[DataInfo], io: bool) -> None:
            """種別(入力・出力)に応じた線の描画

            Args:
                element (DiagramElement): 線を描画したい処理部
                data_list (list[DataInfo]): 描画したい種別のリスト
                is_input (bool): 種別の指定(入力: true, 出力: false)
            """
            nonlocal offset, exit_width, color_cnt

            for data in data_list:
                # 種別に応じた情報の更新
                if io is True:
                    y_offset = -5
                    draw_method = self.draw_svg.draw_arrow_l
                else:
                    y_offset = 5
                    draw_method = self.draw_svg.draw_line_h

                # 水平線の始点と終点を決定
                line = Line()
                line.start = Coordinate(element.end_x + 10, element.y + y_offset)
                line.end = Coordinate(process_end_x + offset, element.y + y_offset)

                # 水平線を保持
                connect_line = Process2Data()
                connect_line.exit_from_process = line
                data.connect_line = connect_line

                # 線の色を保持
                data.connect_line.color = self.color_table[color_cnt]
                color_cnt = (color_cnt + 1) % len(self.color_table)

                # 線を描画
                draw_method(
                    self.svg,
                    data.connect_line.exit_from_process.start.x,
                    data.connect_line.exit_from_process.start.y,
                    data.connect_line.exit_from_process.line_width(),
                    data.connect_line.color,
                )

                # 描画情報を更新
                offset += self.LINE_OFFSET
                exit_width = max(exit_width, line.end.x)

        for process_element in self.process_elements:
            # 入出力がなければ何もしない
            if process_element.line_info.iodata is None:
                continue

            # 関数への入出力は接続線で表現しない
            if process_element.line_info.level == 0:
                continue

            process_io_line(process_element, process_element.line_info.iodata.in_data_list, io=True)
            process_io_line(process_element, process_element.line_info.iodata.out_data_list, io=False)

        return exit_width

    def render_data(self) -> tuple[int, int]:
        """データ部を描画する

        Returns:
            tuple[int, int]: データ部を描画した状態の画像サイズ(高さ, 幅)
        """
        data_height = 0
        data_width = 0
        for data_element in self.data_elements:
            # 種別に応じた図形とテキストを描画
            end_x = self.draw_fig.draw_figure_method(self.svg, data_element)

            # データ部の高さと幅を更新する
            data_height = max(data_height, data_element.y)
            data_width = max(data_width, end_x)

        return data_height, data_width

    def render_line_enter_to_data(self) -> None:
        """データ部に対する入出力線を描画する"""

        def data_io_line(element: DiagramElement, data_list: list[DataInfo], io: bool) -> None:
            """種別(入力・出力)に応じた線の描画

            Args:
                element (DiagramElement): 線を描画したいデータ部
                data_list (list[DataInfo]): 描画したい種別のリスト
                y_offset (int): _description_
                is_input (bool): 種別の指定(入力: true, 出力: false)
            """
            for data in data_list:
                # 種別に応じた情報の更新
                if io is True:
                    y_offset = -5
                    draw_method = self.draw_svg.draw_line_h
                else:
                    y_offset = 5
                    draw_method = self.draw_svg.draw_arrow_r

                # 同じデータ名をつなぐ
                if element.line_info.text_clean != data.name:
                    continue

                # 水平線の始点と終点を決定
                line = Line()
                line.start = Coordinate(data.connect_line.exit_from_process.end.x, element.y + y_offset)
                line.end = Coordinate(element.x - DrawSvg.CIRCLE_R, element.y + y_offset)
                data.connect_line.enter_to_data = line

                # 線を描画
                draw_method(
                    self.svg,
                    data.connect_line.enter_to_data.start.x,
                    data.connect_line.enter_to_data.start.y,
                    data.connect_line.enter_to_data.line_width(),
                    data.connect_line.color,
                )

        for data_element in self.data_elements:
            # 処理部へ存在する入出力を基準に描画する
            for process_element in self.process_elements:
                # 関数への入出力は接続線で表現しない
                if process_element.line_info.level == 0:
                    continue

                data_io_line(data_element, process_element.line_info.iodata.in_data_list, io=True)
                data_io_line(data_element, process_element.line_info.iodata.out_data_list, io=False)

    def connect_process2data(self) -> None:
        """処理部とデータ部の入出力線を結ぶ"""

        def process2data(data_list: list[DataInfo]) -> None:
            """_summary_

            Args:
                data_list (list[DataInfo]): _description_
            """
            for data in data_list:
                # 画像の上部から下部に向かって描画するように更新
                start_y = min(data.connect_line.enter_to_data.start.y, data.connect_line.exit_from_process.end.y)
                end_y = max(data.connect_line.enter_to_data.start.y, data.connect_line.exit_from_process.end.y)

                # 垂直線の始点と終点を決定
                line = Line()
                line.start = Coordinate(data.connect_line.enter_to_data.start.x, start_y)
                line.end = Coordinate(data.connect_line.enter_to_data.start.x, end_y)
                data.connect_line.between_prcess_data = line

                # 線を描画
                self.draw_svg.draw_line_v(
                    self.svg,
                    data.connect_line.between_prcess_data.start.x,
                    data.connect_line.between_prcess_data.start.y,
                    data.connect_line.between_prcess_data.line_height(),
                    data.connect_line.color,
                )

        for process_element in self.process_elements:
            # 関数への入出力は接続線で表現しない
            if process_element.line_info.level == 0:
                continue

            process2data(process_element.line_info.iodata.in_data_list)
            process2data(process_element.line_info.iodata.out_data_list)

    def finish_svg(self, width: int, height: int) -> str:
        self.svg.insert(0, f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height + 50}" style="background-color: #808d81">')
        self.svg.append("</svg>")
        return "\n".join(self.svg)

    def render(self) -> str:
        """パースされた要素をSVGとして描画"""
        start_x = 30
        start_y = 30

        # 処理部を描画
        self.process_elements = self.set_elements(start_x, start_y, self.process_info_list)
        process_height, process_width = self.render_process()

        # 処理部からの水平線を描画
        exit_width = self.render_line_exit_from_process(process_width)

        # データ部を描画
        self.data_elements = self.set_elements(exit_width + 30, start_y, self.data_info_list)
        data_height, data_width = self.render_data()

        # データ部への水平線を描画
        self.render_line_enter_to_data()

        # 処理部とデータ部を結ぶ
        self.connect_process2data()

        # 描画終了
        total_width = data_width
        total_height = max(process_height, data_height)
        return self.finish_svg(total_width, total_height)
