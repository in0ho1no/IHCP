import math

from define import DiagramElement, LineInfo


class SVGRenderer:
    def __init__(self) -> None:
        pass

    def draw_text(self, svg: list[str], center_x: int, center_y: int, text: str, font_size: int = 100) -> None:
        svg.append(f'<text x="{center_x}" y="{center_y}" text-anchor="left" dominant-baseline="middle" font-size="{font_size}%">{text}</text>')

    def draw_line_h(self, svg: list[str], center_x: int, center_y: int, length: int) -> None:
        svg.append(f'<line x1="{center_x}" y1="{center_y}" x2="{center_x + length}" y2="{center_y}" stroke="black" marker-end="url(#arrowhead)"/>')

    def draw_line_v(self, svg: list[str], center_x: int, center_y: int, length: int) -> None:
        svg.append(f'<line x1="{center_x}" y1="{center_y}" x2="{center_x}" y2="{center_y + length}" stroke="black" marker-end="url(#arrowhead)"/>')

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

    def draw_figure_normal(self, svg: list[str], center_x: int, center_y: int, text: str = "") -> None:
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{DiagramElement.CIRCLE_R}" fill="white" stroke="black"/>')

        # テキストの描画
        if text != "":
            self.draw_text(svg, center_x + DiagramElement.CIRCLE_R + DiagramElement.SPACE_FIGURE_TO_TEXT, center_y, text)

    def get_vertices_polygon(
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
    ) -> None:
        # 円の描画
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{DiagramElement.CIRCLE_R}" fill="white" stroke="black"/>')

        # 正三角形の描画
        vertices = self.get_vertices_polygon(3, center_x, center_y, DiagramElement.CIRCLE_R - 2, 0)
        svg.append(
            f'<polygon points="{vertices[0][0]} {vertices[0][1]} {vertices[1][0]} {vertices[1][1]} {vertices[2][0]} {vertices[2][1]}" '
            f'fill="white" stroke="black"/>'
        )

        # テキストの描画
        if text != "":
            self.draw_text(svg, center_x + DiagramElement.CIRCLE_R + DiagramElement.SPACE_FIGURE_TO_TEXT, center_y, text)

    def draw_figure_mod(self, svg: list[str], center_x: int, center_y: int, text: str = "") -> None:
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{DiagramElement.CIRCLE_R}" fill="white" stroke="black"/>')
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{int(DiagramElement.CIRCLE_R / 2)}" fill="white" stroke="black"/>')

        # テキストの描画
        if text != "":
            self.draw_text(svg, center_x + DiagramElement.CIRCLE_R + DiagramElement.SPACE_FIGURE_TO_TEXT, center_y, text)

    def draw_figure_return(
        self,
        svg: list[str],
        center_x: int,
        center_y: int,
        text: str = "",
    ) -> None:
        # 垂直線の追加 上
        self.draw_line_v(svg, center_x, center_y - DiagramElement.CIRCLE_R, DiagramElement.CIRCLE_R)

        # 正三角形の描画
        vertices = self.get_vertices_polygon(3, center_x, center_y, DiagramElement.CIRCLE_R, (math.pi / 2))
        svg.append(
            f'<polygon points="{vertices[0][0]} {vertices[0][1]} {vertices[1][0]} {vertices[1][1]} {vertices[2][0]} {vertices[2][1]}" '
            f'fill="white" stroke="black"/>'
        )

        # 水平線の追加 下
        self.draw_line_h(svg, (center_x - DiagramElement.CIRCLE_R), center_y + DiagramElement.CIRCLE_R, (DiagramElement.CIRCLE_R * 2))

        # 脱出する階層数の指定
        if text == "":
            return
        if text.isdecimal() is False:
            return
        self.draw_text(svg, center_x - (len(text) * 2), center_y + 1, text, font_size=50)

    def render(self, line_info_list: list[LineInfo]) -> str:
        """パースされた要素をSVGとして描画"""
        # ヘッダは最後に挿入する
        # svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" style="background-color: #AFC0B1">']
        svg: list[str] = []

        start_x = 30
        start_y = 30

        # 要素の配置を計算
        elements: list[DiagramElement] = []
        for i, line_info in enumerate(line_info_list):
            element = DiagramElement(line_info)

            element.x = start_x + element.line_info.level * (DiagramElement.LEVEL_SHIFT)
            element.y = start_y + i * (DiagramElement.LEVEL_SHIFT)

            elements.append(element)

        # 図形要素を描画
        total_height = 0
        for element in elements:
            # 種別に応じた図形とテキストを描画
            if element.line_info.category == DiagramElement.TYPE_NORMAL:
                self.draw_figure_normal(svg, element.x, element.y, element.line_info.text)
            elif element.line_info.category == DiagramElement.TYPE_FORK:
                self.draw_figure_fork(svg, element.x, element.y, element.line_info.text)
            elif element.line_info.category == DiagramElement.TYPE_MOD:
                self.draw_figure_mod(svg, element.x, element.y, element.line_info.text)
            elif element.line_info.category == DiagramElement.TYPE_RETURN:
                self.draw_figure_return(svg, element.x, element.y, element.line_info.text)

            # 垂直線の追加
            if element.line_info.before_no != LineInfo.DEFAULT_VALUE:
                bef_elem = elements[element.line_info.before_no]
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
                    f"{element.line_info.text}, "
                )

            # 始点の追加
            if element.line_info.level == 0:
                self.draw_figure_level_start(svg, element.x, element.y)

            # 終端の追加
            if element.line_info.next_no == LineInfo.DEFAULT_VALUE:
                if element.line_info.category == DiagramElement.TYPE_RETURN:
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

        svg.insert(0, f'<svg xmlns="http://www.w3.org/2000/svg" width="800" height="{total_height + 50}" style="background-color: #AFC0B1">')
        svg.append("</svg>")
        return "\n".join(svg)
