import math

from define import Coordinate, DiagramElement, Line, LineInfo, Process2Data, get_string_bytes
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
        pass

    def get_text_width(self, text: str) -> int:
        text_bytes = get_string_bytes(text.strip())
        half_bytes = int((text_bytes + 2 - 1) // 2)
        text_width = half_bytes * 16  # デフォルトの文字幅は16px
        return text_width

    def draw_text(self, svg: list[str], center_x: int, center_y: int, text: str, font_size: int = 100, rotate: int = 0) -> int:
        svg.append(
            f'<text x="{center_x}" y="{center_y}" '
            f'text-anchor="left" dominant-baseline="middle" '
            f'font-size="{font_size}%" rotate="{rotate}">{text}</text>'
        )
        text_width = self.get_text_width(text)
        return text_width

    def draw_line_h(self, svg: list[str], center_x: int, center_y: int, length: int, color: str = "black") -> None:
        svg.append(f'<line x1="{center_x}" y1="{center_y}" x2="{center_x + length}" y2="{center_y}" stroke="{color}"/>')

    def draw_line_v(self, svg: list[str], center_x: int, center_y: int, length: int, color: str = "black") -> None:
        svg.append(f'<line x1="{center_x}" y1="{center_y}" x2="{center_x}" y2="{center_y + length}" stroke="{color}"/>')

    def draw_arrow_r(self, svg: list[str], center_x: int, center_y: int, length: int, color: str = "black") -> None:
        end_x = center_x + length
        svg.append(f'<line x1="{center_x}" y1="{center_y}" x2="{end_x}" y2="{center_y}" stroke="{color}"/>')
        arrow_hed = 8
        svg.append(
            f'<path d="M {end_x} {center_y} '
            f'L {end_x - arrow_hed} {center_y - int(arrow_hed / 2)} L {end_x - arrow_hed} {center_y + int(arrow_hed / 2)}" '
            f'stroke="{color}" fill="{color}" />'
        )

    def draw_arrow_l(self, svg: list[str], center_x: int, center_y: int, length: int, color: str = "black") -> None:
        end_x = center_x + length
        svg.append(f'<line x1="{center_x}" y1="{center_y}" x2="{end_x}" y2="{center_y}" stroke="{color}"/>')
        arrow_hed = 8
        svg.append(
            f'<path d="M {center_x} {center_y} '
            f'L {center_x + arrow_hed} {center_y - int(arrow_hed / 2)} L {center_x + arrow_hed} {center_y + int(arrow_hed / 2)}" '
            f'stroke="{color}" fill="{color}" />'
        )

    def draw_figure_level_start(self, svg: list[str], center_x: int, center_y: int) -> None:
        # 垂直線の追加 上
        self.draw_line_v(svg, center_x, center_y - DiagramElement.CIRCLE_R * 2, DiagramElement.CIRCLE_R)

        # 水平線の追加 上
        self.draw_line_h(svg, (center_x - DiagramElement.CIRCLE_R), center_y - (DiagramElement.CIRCLE_R * 2), (DiagramElement.CIRCLE_R * 2))

    def draw_figure_level_end(self, svg: list[str], center_x: int, center_y: int) -> None:
        # 垂直線の追加 下
        self.draw_line_v(svg, center_x, center_y + DiagramElement.CIRCLE_R, DiagramElement.CIRCLE_R)

        # 水平線の追加 下
        self.draw_line_h(svg, (center_x - DiagramElement.CIRCLE_R), center_y + (DiagramElement.CIRCLE_R * 2), (DiagramElement.CIRCLE_R * 2))

    def draw_figure_level_step(self, svg: list[str], center_x: int, center_y: int) -> None:
        # 垂直線の追加 上
        self.draw_line_v(svg, center_x, center_y - DiagramElement.CIRCLE_R * 2, DiagramElement.CIRCLE_R)

        # 水平線の追加 上
        self.draw_line_h(svg, (center_x - DiagramElement.CIRCLE_R * 2), center_y - (DiagramElement.CIRCLE_R * 2), (DiagramElement.CIRCLE_R * 2))

        # 垂直線の追加 上
        self.draw_line_v(svg, (center_x - DiagramElement.CIRCLE_R * 2), center_y - DiagramElement.CIRCLE_R * 4, DiagramElement.CIRCLE_R * 2)

    def draw_figure_normal(self, svg: list[str], center_x: int, center_y: int, text: str = "") -> int:
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{DiagramElement.CIRCLE_R}" fill="white" stroke="black"/>')

        # テキストの描画
        if text != "":
            figure_2_text_space = int(DiagramElement.CIRCLE_R + DiagramElement.SPACE_FIGURE_TO_TEXT)
            text_width = self.draw_text(svg, center_x + figure_2_text_space, center_y, text)
        else:
            figure_2_text_space = DiagramElement.CIRCLE_R
            text_width = 0

        # 終端位置を返す
        end_x = center_x + figure_2_text_space + text_width
        return end_x

    def __get_vertices_polygon(
        self,
        num_of_vertex: int,
        center_x: int,
        center_y: int,
        radius: int,
        rotation: float = 0,
    ) -> list[tuple[int, int]]:
        """円に内接する正多角形の頂点座標を取得する

        Args:
            num_of_vertex (int): 頂点の数
            center_x (int): 円の中心となるX座標
            center_y (int): 円の中心となるY座標
            radius (int): 円の半径
            rotation (float, optional): 正多角形を回転させたい角度(ラジアン). Defaults to 0.

        Returns:
            list[tuple[int, int]]: 正多角形の頂点座標をタプル(x,y)のリストで返す
        """
        vertices = []
        for vertex in range(num_of_vertex):
            angle = rotation + vertex * (2 * math.pi / num_of_vertex)
            x = int(center_x + radius * math.cos(angle))
            y = int(center_y + radius * math.sin(angle))
            vertices.append((x, y))

        return vertices

    def draw_figure_fork(
        self,
        svg: list[str],
        center_x: int,
        center_y: int,
        text: str = "",
        rotation: int = 0,
    ) -> int:
        # 円の描画
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{DiagramElement.CIRCLE_R}" fill="white" stroke="black"/>')

        # 正三角形の描画
        vertices = self.__get_vertices_polygon(3, center_x, center_y, DiagramElement.CIRCLE_R - 2, 0)
        svg.append(
            f'<polygon points="{vertices[0][0]} {vertices[0][1]} {vertices[1][0]} {vertices[1][1]} {vertices[2][0]} {vertices[2][1]}" '
            f'fill="white" stroke="black"/>'
        )

        # テキストの描画
        if text != "":
            figure_2_text_space = int(DiagramElement.CIRCLE_R + DiagramElement.SPACE_FIGURE_TO_TEXT)
            text_width = self.draw_text(svg, center_x + figure_2_text_space, center_y, text)
        else:
            figure_2_text_space = DiagramElement.CIRCLE_R
            text_width = 0

        # 終端位置を返す
        end_x = center_x + figure_2_text_space + text_width
        return end_x

    def draw_figure_repeat(
        self,
        svg: list[str],
        center_x: int,
        center_y: int,
        text: str = "",
    ) -> int:
        # 円の描画
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{DiagramElement.CIRCLE_R}" fill="white" stroke="black"/>')

        self.draw_text(svg, center_x + 8, center_y - 1, "↻", rotate=240)

        # テキストの描画
        if text != "":
            figure_2_text_space = int(DiagramElement.CIRCLE_R + DiagramElement.SPACE_FIGURE_TO_TEXT)
            text_width = self.draw_text(svg, center_x + figure_2_text_space, center_y, text)
        else:
            figure_2_text_space = DiagramElement.CIRCLE_R
            text_width = 0

        # 終端位置を返す
        end_x = center_x + figure_2_text_space + text_width
        return end_x

    def draw_figure_mod(self, svg: list[str], center_x: int, center_y: int, text: str = "") -> int:
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{DiagramElement.CIRCLE_R}" fill="white" stroke="black"/>')
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{int(DiagramElement.CIRCLE_R / 2)}" fill="white" stroke="black"/>')

        # テキストの描画
        if text != "":
            figure_2_text_space = int(DiagramElement.CIRCLE_R + DiagramElement.SPACE_FIGURE_TO_TEXT)
            text_width = self.draw_text(svg, center_x + figure_2_text_space, center_y, text)
        else:
            figure_2_text_space = DiagramElement.CIRCLE_R
            text_width = 0

        # 終端位置を返す
        end_x = center_x + figure_2_text_space + text_width
        return end_x

    def draw_figure_return(
        self,
        svg: list[str],
        center_x: int,
        center_y: int,
        text: str = "",
    ) -> int:
        # 垂直線の追加 上
        self.draw_line_v(svg, center_x, center_y - DiagramElement.CIRCLE_R, DiagramElement.CIRCLE_R)

        # 正三角形の描画
        vertices = self.__get_vertices_polygon(3, center_x, center_y, DiagramElement.CIRCLE_R, (math.pi / 2))
        svg.append(
            f'<polygon points="{vertices[0][0]} {vertices[0][1]} {vertices[1][0]} {vertices[1][1]} {vertices[2][0]} {vertices[2][1]}" '
            f'fill="white" stroke="black"/>'
        )

        # 水平線の追加 下
        self.draw_line_h(svg, (center_x - DiagramElement.CIRCLE_R), center_y + DiagramElement.CIRCLE_R, (DiagramElement.CIRCLE_R * 2))

        # 脱出する階層数の指定
        if text != "":
            if text.isdecimal() is True:
                self.draw_text(svg, center_x - (len(text) * 2), center_y + 1, text, font_size=50)

        # 終端位置を返す
        figure_2_text_space = int(DiagramElement.CIRCLE_R)
        text_width = 0
        end_x = center_x + figure_2_text_space + text_width
        return end_x

    def __draw_figure_cond(self, svg: list[str], center_x: int, center_y: int, text: str = "") -> int:
        # 垂直線の追加
        self.draw_line_v(svg, center_x, center_y - DiagramElement.CIRCLE_R, DiagramElement.CIRCLE_R * 2)

        self.draw_arrow_r(svg, center_x, center_y - DiagramElement.CIRCLE_R, 15)

        # テキストの描画
        figure_2_text_space = int(DiagramElement.CIRCLE_R + DiagramElement.SPACE_FIGURE_TO_TEXT)
        text_width = self.draw_text(svg, center_x + figure_2_text_space, center_y, text)

        # 終端位置を返す
        end_x = center_x + figure_2_text_space + text_width
        return end_x

    def draw_figure_true(self, svg: list[str], center_x: int, center_y: int, text: str = "") -> int:
        text_cond = "(true) " + text
        end_x = self.__draw_figure_cond(svg, center_x, center_y, text_cond)
        return end_x

    def draw_figure_false(self, svg: list[str], center_x: int, center_y: int, text: str = "") -> int:
        text_cond = "(false) " + text
        end_x = self.__draw_figure_cond(svg, center_x, center_y, text_cond)
        return end_x

    def draw_figure_branch(self, svg: list[str], center_x: int, center_y: int, text: str = "") -> int:
        text_cond = "(" + text + ")"
        end_x = self.__draw_figure_cond(svg, center_x, center_y, text_cond)
        return end_x

    def draw_figure_data(self, svg: list[str], center_x: int, center_y: int, text: str = "") -> int:
        svg.append(
            f'<rect x="{center_x - DiagramElement.CIRCLE_R}" y="{center_y - DiagramElement.CIRCLE_R}" '
            f'width="{DiagramElement.CIRCLE_R * 2}" height="{DiagramElement.CIRCLE_R * 2}" fill="white" stroke="black"/>'
        )

        # テキストの描画
        if text != "":
            figure_2_text_space = int(DiagramElement.CIRCLE_R + DiagramElement.SPACE_FIGURE_TO_TEXT)
            text_width = self.draw_text(svg, center_x + figure_2_text_space, center_y, text)
        else:
            figure_2_text_space = DiagramElement.CIRCLE_R
            text_width = 0

        # 終端位置を返す
        end_x = center_x + figure_2_text_space + text_width
        return end_x

    def render(self, process_info_list: list[LineInfo], data_info_list: list[LineInfo]) -> str:
        """パースされた要素をSVGとして描画"""
        # ヘッダは最後に挿入する
        # svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" style="background-color: #AFC0B1">']
        svg: list[str] = []

        start_x = 30
        start_y = 30

        # 要素の配置を計算
        process_elements: list[DiagramElement] = []
        for line_info in process_info_list:
            element = DiagramElement(line_info)

            element.x = start_x + element.line_info.level * (DiagramElement.LEVEL_SHIFT)
            element.y = start_y + len(process_elements) * (DiagramElement.LEVEL_SHIFT)

            process_elements.append(element)

        # 図形要素を描画
        total_height = 0
        total_width = 0
        process_width = 0
        for element in process_elements:
            # 種別に応じた図形とテキストを描画
            if element.line_info.type.type_value == LineTypeDefine.get_format_by_type(LineTypeEnum.NORMAL).type_value:
                element.end_x = self.draw_figure_normal(svg, element.x, element.y, element.line_info.text_clean)
            elif element.line_info.type.type_value == LineTypeDefine.get_format_by_type(LineTypeEnum.FORK).type_value:
                element.end_x = self.draw_figure_fork(svg, element.x, element.y, element.line_info.text_clean)
            elif element.line_info.type.type_value == LineTypeDefine.get_format_by_type(LineTypeEnum.REPEAT).type_value:
                element.end_x = self.draw_figure_repeat(svg, element.x, element.y, element.line_info.text_clean)
            elif element.line_info.type.type_value == LineTypeDefine.get_format_by_type(LineTypeEnum.MOD).type_value:
                element.end_x = self.draw_figure_mod(svg, element.x, element.y, element.line_info.text_clean)
            elif element.line_info.type.type_value == LineTypeDefine.get_format_by_type(LineTypeEnum.RETURN).type_value:
                element.end_x = self.draw_figure_return(svg, element.x, element.y, element.line_info.text_clean)
            elif element.line_info.type.type_value == LineTypeDefine.get_format_by_type(LineTypeEnum.TRUE).type_value:
                element.end_x = self.draw_figure_true(svg, element.x, element.y, element.line_info.text_clean)
            elif element.line_info.type.type_value == LineTypeDefine.get_format_by_type(LineTypeEnum.FALSE).type_value:
                element.end_x = self.draw_figure_false(svg, element.x, element.y, element.line_info.text_clean)
            elif element.line_info.type.type_value == LineTypeDefine.get_format_by_type(LineTypeEnum.BRANCH).type_value:
                element.end_x = self.draw_figure_branch(svg, element.x, element.y, element.line_info.text_clean)
            else:
                element.end_x = 0

            # ステップ間の垂直線の追加
            if element.line_info.before_no != LineInfo.DEFAULT_VALUE:
                bef_elem = process_elements[element.line_info.before_no]
                # 直前のレベルまで線を引く
                self.draw_line_v(
                    svg,
                    element.x,
                    (bef_elem.y + DiagramElement.CIRCLE_R),
                    (element.y - DiagramElement.CIRCLE_R) - (bef_elem.y + DiagramElement.CIRCLE_R),
                )
                print(
                    f"{element.x=}, {bef_elem.y=}, {bef_elem.y=} - {element.y=}, "
                    f"{element.line_info.no=}, {element.line_info.before_no=}, {element.line_info.next_no=}"
                    f"{element.line_info.text_clean}, "
                )

            # 始点の追加
            if element.line_info.level == 0:
                self.draw_figure_level_start(svg, element.x, element.y)

            # 終端の追加
            if element.line_info.next_no == LineInfo.DEFAULT_VALUE:
                if element.line_info.type.type_value == LineTypeDefine.get_format_by_type(LineTypeEnum.RETURN).type_value:
                    # \returnは図として終端を描画する
                    pass
                else:
                    self.draw_figure_level_end(svg, element.x, element.y)

            # レベル下げの追加
            if (element.line_info.level > 0) and (element.line_info.before_no == LineInfo.DEFAULT_VALUE):
                self.draw_figure_level_step(svg, element.x, element.y)

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

                self.draw_arrow_l(
                    svg,
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

                self.draw_line_h(
                    svg,
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
        color_cnt = 0
        for data_element in data_elements:
            # 種別に応じた図形とテキストを描画
            data_name = data_element.line_info.text_clean
            end_x = self.draw_figure_data(svg, data_element.x, data_element.y, data_name)

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
                        data_element.x - DiagramElement.CIRCLE_R,
                        data_element.y - 5,
                    )
                    in_data.connect_line.enter_to_data = line

                    self.draw_line_h(
                        svg,
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
                        data_element.x - DiagramElement.CIRCLE_R,
                        data_element.y + 5,
                    )
                    out_data.connect_line.enter_to_data = line

                    self.draw_arrow_r(
                        svg,
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
        color_cnt = 0
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

                self.draw_line_v(
                    svg,
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

                self.draw_line_v(
                    svg,
                    out_data.connect_line.between_prcess_data.start.x,
                    out_data.connect_line.between_prcess_data.start.y,
                    out_data.connect_line.between_prcess_data.line_height(),
                    out_data.connect_line.color,
                )

        svg.insert(
            0, f'<svg xmlns="http://www.w3.org/2000/svg" width="{total_width}" height="{total_height + 50}" style="background-color: #808d81">'
        )
        svg.append("</svg>")
        return "\n".join(svg)
