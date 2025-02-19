from define import DiagramElement, LineInfo


class SVGRenderer:
    def __init__(self) -> None:
        pass

    def draw_text(self, svg: list[str], center_x: int, center_y: int, text: str) -> None:
        svg.append(f'<text x="{center_x}" y="{center_y}" text-anchor="left" dominant-baseline="middle">{text}</text>')

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

    def draw_figure_level_eq0(
        self,
        svg: list[str],
        center_x: int,
        center_y: int,
        text: str = "",
    ) -> None:
        # 円の追加 中心
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{DiagramElement.CIRCLE_R}" fill="white" stroke="black"/>')

        # 垂直線の追加 上下
        self.draw_line_v(svg, center_x, center_y - DiagramElement.CIRCLE_R * 2, DiagramElement.CIRCLE_R)
        self.draw_line_v(svg, center_x, center_y + DiagramElement.CIRCLE_R, DiagramElement.CIRCLE_R)

        # 水平線の追加 上下
        self.draw_line_h(svg, (center_x - DiagramElement.CIRCLE_R), center_y - (DiagramElement.CIRCLE_R * 2), (DiagramElement.CIRCLE_R * 2))
        self.draw_line_h(svg, (center_x - DiagramElement.CIRCLE_R), center_y + (DiagramElement.CIRCLE_R * 2), (DiagramElement.CIRCLE_R * 2))

        # テキストの描画
        if text != "":
            self.draw_text(svg, center_x + DiagramElement.CIRCLE_R + DiagramElement.SPACE_FIGURE_TO_TEXT, center_y, text)

    def draw_figure_level_gt0(self, svg: list[str], center_x: int, center_y: int, text: str = "") -> None:
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{DiagramElement.CIRCLE_R}" fill="white" stroke="black"/>')

        # テキストの描画
        if text != "":
            self.draw_text(svg, center_x + DiagramElement.CIRCLE_R + DiagramElement.SPACE_FIGURE_TO_TEXT, center_y, text)

    def render(self, line_info_list: list[LineInfo]) -> str:
        """パースされた要素をSVGとして描画"""
        svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" style="background-color: #AFC0B1">']

        start_x = 30
        start_y = 30

        # 要素の配置を計算
        elements: list[DiagramElement] = []
        for i, line_info in enumerate(line_info_list):
            element = DiagramElement(line_info)

            element.x = start_x + element.line_info.level * (DiagramElement.LEVEL_SHIFT)
            element.y = start_y + i * (DiagramElement.LEVEL_SHIFT)
            element.type = DiagramElement.TYPE_NORMAL

            elements.append(element)

        # 図形要素を描画
        for element in elements:
            # 種別に応じた図形とテキストを描画
            if element.type == DiagramElement.TYPE_NORMAL:
                if element.line_info.level == 0:
                    self.draw_figure_level_eq0(svg, element.x, element.y, element.line_info.text)
                else:
                    self.draw_figure_level_gt0(svg, element.x, element.y, element.line_info.text)

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
                self.draw_figure_level_end(svg, element.x, element.y)

        svg.append("</svg>")
        return "\n".join(svg)
