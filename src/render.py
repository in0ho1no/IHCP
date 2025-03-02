from define import Coordinate, DiagramElement, Line, LineInfo, Process2Data
from draw_svg import DrawFigure, DrawSvg
from line_type import LineTypeDefine, LineTypeEnum


class SVGRenderer:
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

    def __init__(self) -> None:
        # svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" style="background-color: #AFC0B1">']
        self.svg: list[str] = []
        self.draw_svg = DrawSvg()
        self.draw_fig = DrawFigure(self.draw_svg)

    def render(self, process_info_list: list[LineInfo], data_info_list: list[LineInfo]) -> str:
        """パースされた要素をSVGとして描画"""
        # ヘッダは最後に挿入する

        start_x = 30
        start_y = 30

        # 処理部の配置計算
        process_elements: list[DiagramElement] = []
        for line_info in process_info_list:
            element = DiagramElement(line_info)
            element.x = start_x + element.line_info.level * (DiagramElement.LEVEL_SHIFT)
            element.y = start_y + len(process_elements) * (DiagramElement.LEVEL_SHIFT)
            process_elements.append(element)

        # 処理部を描画
        total_height = 0
        total_width = 0
        process_width = 0
        for element in process_elements:
            # 種別に応じた図形とテキストを描画
            element.end_x = self.draw_fig.draw_figure_method(self.svg, element)

            # ステップ間の垂直線の追加
            if element.line_info.before_no != LineInfo.DEFAULT_VALUE:
                bef_elem = process_elements[element.line_info.before_no]
                # 直前のレベルまで線を引く
                self.draw_svg.draw_line_v(
                    self.svg,
                    element.x,
                    (bef_elem.y + DrawSvg.CIRCLE_R),
                    (element.y - DrawSvg.CIRCLE_R) - (bef_elem.y + DrawSvg.CIRCLE_R),
                )
                print(
                    f"{element.x=}, {bef_elem.y=}, {bef_elem.y=} - {element.y=}, "
                    f"{element.line_info.no=}, {element.line_info.before_no=}, {element.line_info.next_no=}"
                    f"{element.line_info.text_clean}, "
                )

            # 始点の追加
            if element.line_info.level == 0:
                self.draw_svg.draw_figure_level_start(self.svg, element.x, element.y)

            # 終端の追加
            if element.line_info.next_no == LineInfo.DEFAULT_VALUE:
                if element.line_info.type.type_value == LineTypeDefine.get_format_by_type(LineTypeEnum.RETURN).type_value:
                    # \returnは図として終端を描画する
                    pass
                else:
                    self.draw_svg.draw_figure_level_end(self.svg, element.x, element.y)

            # レベル下げの追加
            if (element.line_info.level > 0) and (element.line_info.before_no == LineInfo.DEFAULT_VALUE):
                self.draw_svg.draw_figure_level_step(self.svg, element.x, element.y)

            # 画像全体の高さを決定する
            if total_height < element.y:
                total_height = element.y

            # 画像全体の幅を決定する
            if process_width < element.end_x:
                process_width = element.end_x
                total_width = process_width

        # 処理の入出力線を描画する
        offset = 0
        exit_width = 0
        color_cnt = 0
        for element in process_elements:
            if element.line_info.iodata is None:
                continue

            for in_data in element.line_info.iodata.in_data_list:
                print(in_data, element.x, element.y)
                # 水平線の追加
                line = Line()
                line.start = Coordinate(element.end_x + 10, element.y - 5)
                line.end = Coordinate(process_width + offset, element.y - 5)

                connect_line = Process2Data()
                connect_line.exit_from_process = line
                connect_line.color = self.color_table[color_cnt]
                in_data.connect_line = connect_line

                self.draw_svg.draw_arrow_l(
                    self.svg,
                    in_data.connect_line.exit_from_process.start.x,
                    in_data.connect_line.exit_from_process.start.y,
                    in_data.connect_line.exit_from_process.line_width(),
                    in_data.connect_line.color,
                )
                color_cnt = color_cnt + 1 if color_cnt + 1 < len(self.color_table) else 0
                offset += 10
                if exit_width < line.end.x:
                    exit_width = line.end.x
                    total_width = exit_width

            for out_data in element.line_info.iodata.out_data_list:
                print(out_data, element.x, element.y)
                # 水平線の追加
                line = Line()
                line.start = Coordinate(element.end_x + 10, element.y + 5)
                line.end = Coordinate(process_width + offset, element.y + 5)

                connect_line = Process2Data()
                connect_line.exit_from_process = line
                connect_line.color = self.color_table[color_cnt]
                out_data.connect_line = connect_line

                self.draw_svg.draw_line_h(
                    self.svg,
                    out_data.connect_line.exit_from_process.start.x,
                    out_data.connect_line.exit_from_process.start.y,
                    out_data.connect_line.exit_from_process.line_width(),
                    out_data.connect_line.color,
                )
                color_cnt = color_cnt + 1 if color_cnt + 1 < len(self.color_table) else 0
                offset += 10
                if exit_width < line.end.x:
                    exit_width = line.end.x
                    total_width = exit_width

        # データ部の座標決定
        data_start_x = exit_width + 30
        data_start_y = start_y
        data_elements: list[DiagramElement] = []
        for line_info in data_info_list:
            if line_info.type.type_value != LineTypeDefine.get_format_by_type(LineTypeEnum.DATA).type_value:
                continue

            element = DiagramElement(line_info)

            element.x = data_start_x + element.line_info.level * (DiagramElement.LEVEL_SHIFT)
            element.y = data_start_y + len(data_elements) * (DiagramElement.LEVEL_SHIFT)

            data_elements.append(element)

        # データ部の図形要素を描画
        for data_element in data_elements:
            # 種別に応じた図形とテキストを描画
            data_name = data_element.line_info.text_clean
            end_x = self.draw_svg.draw_figure_data(self.svg, data_element.x, data_element.y, data_name)

            for process_element in process_elements:
                for in_data in process_element.line_info.iodata.in_data_list:
                    # 同じデータ名をつなぐ
                    if data_name != in_data.name:
                        continue

                    # 水平線の追加
                    line = Line()
                    line.start = Coordinate(
                        in_data.connect_line.exit_from_process.end.x,
                        data_element.y - 5,
                    )
                    line.end = Coordinate(
                        data_element.x - DrawSvg.CIRCLE_R,
                        data_element.y - 5,
                    )
                    in_data.connect_line.enter_to_data = line

                    self.draw_svg.draw_line_h(
                        self.svg,
                        in_data.connect_line.enter_to_data.start.x,
                        in_data.connect_line.enter_to_data.start.y,
                        in_data.connect_line.enter_to_data.line_width(),
                        in_data.connect_line.color,
                    )

                for out_data in process_element.line_info.iodata.out_data_list:
                    # 同じデータ名をつなぐ
                    if data_name != out_data.name:
                        continue

                    # 水平線の追加
                    line = Line()
                    line.start = Coordinate(
                        out_data.connect_line.exit_from_process.end.x,
                        data_element.y + 5,
                    )
                    line.end = Coordinate(
                        data_element.x - DrawSvg.CIRCLE_R,
                        data_element.y + 5,
                    )
                    out_data.connect_line.enter_to_data = line

                    self.draw_svg.draw_arrow_r(
                        self.svg,
                        out_data.connect_line.enter_to_data.start.x,
                        out_data.connect_line.enter_to_data.start.y,
                        out_data.connect_line.enter_to_data.line_width(),
                        out_data.connect_line.color,
                    )

            # 画像全体の高さを決定する
            if total_height < data_element.y:
                total_height = data_element.y

            # 画像全体の幅を決定する
            if total_width < end_x:
                total_width = end_x

        # 入出力の線を結ぶ
        for process_element in process_elements:
            for in_data in process_element.line_info.iodata.in_data_list:
                if in_data.connect_line.enter_to_data is None:
                    continue

                start_y = in_data.connect_line.enter_to_data.start.y
                end_y = in_data.connect_line.exit_from_process.end.y
                if start_y > end_y:
                    start_y = in_data.connect_line.exit_from_process.end.y
                    end_y = in_data.connect_line.enter_to_data.start.y

                line = Line()
                line.start = Coordinate(in_data.connect_line.enter_to_data.start.x, start_y)
                line.end = Coordinate(in_data.connect_line.enter_to_data.start.x, end_y)
                in_data.connect_line.between_prcess_data = line

                self.draw_svg.draw_line_v(
                    self.svg,
                    in_data.connect_line.between_prcess_data.start.x,
                    in_data.connect_line.between_prcess_data.start.y,
                    in_data.connect_line.between_prcess_data.line_height(),
                    in_data.connect_line.color,
                )

            for out_data in process_element.line_info.iodata.out_data_list:
                if out_data.connect_line.enter_to_data is None:
                    continue

                start_y = out_data.connect_line.enter_to_data.start.y
                end_y = out_data.connect_line.exit_from_process.end.y
                if start_y > end_y:
                    start_y = out_data.connect_line.exit_from_process.end.y
                    end_y = out_data.connect_line.enter_to_data.start.y

                line = Line()
                line.start = Coordinate(out_data.connect_line.enter_to_data.start.x, start_y)
                line.end = Coordinate(out_data.connect_line.enter_to_data.start.x, end_y)
                out_data.connect_line.between_prcess_data = line

                self.draw_svg.draw_line_v(
                    self.svg,
                    out_data.connect_line.between_prcess_data.start.x,
                    out_data.connect_line.between_prcess_data.start.y,
                    out_data.connect_line.between_prcess_data.line_height(),
                    out_data.connect_line.color,
                )

        self.svg.insert(
            0, f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{total_height + 50}" style="background-color: #808d81">'
        )
        self.svg.append("</svg>")
        return "\n".join(self.svg)
