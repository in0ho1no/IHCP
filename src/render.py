from dataclasses import dataclass


@dataclass
class DiagramElement:
    TYPE_NORMAL = 0

    MARGIN = 15

    CIRCLE_R = 9
    FIGURE_WIDTH = CIRCLE_R * 2
    FIGURE_HEIGHT = CIRCLE_R * 4

    SPACE_FIGURE_TO_TEXT = 15

    LEVEL_SHIFT = 30

    level: int = 0
    content: str = ""
    x: int = 0
    y: int = 0
    type: int = TYPE_NORMAL


class SVGRenderer:
    def __init__(self) -> None:
        pass

    def draw_text(self, svg: list[str], center_x: int, center_y: int, text: str) -> None:
        svg.append(f'<text x="{center_x}" y="{center_y}" text-anchor="left" dominant-baseline="middle">{text}</text>')

    def draw_figure_level_eq0(
        self,
        svg: list[str],
        center_x: int,
        center_y: int,
        text: str = "",
    ) -> None:
        # 円の追加 中心
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{DiagramElement.CIRCLE_R}" fill="white" stroke="black"/>')

        # 垂直線の追加 上側
        svg.append(
            f'<line x1="{center_x}" y1="{center_y - DiagramElement.CIRCLE_R}" '
            f'x2="{center_x}" y2="{center_y - (DiagramElement.CIRCLE_R * 2)}" '
            f'stroke="black" marker-end="url(#arrowhead)"/>'
        )

        # 垂直線の追加 下側
        svg.append(
            f'<line x1="{center_x}" y1="{center_y + DiagramElement.CIRCLE_R}" '
            f'x2="{center_x}" y2="{center_y + (DiagramElement.CIRCLE_R * 2)}" '
            f'stroke="black" marker-end="url(#arrowhead)"/>'
        )

        # 水平線の追加 上側
        svg.append(
            f'<line x1="{center_x - DiagramElement.CIRCLE_R}" y1="{center_y + (DiagramElement.CIRCLE_R * 2)}" '
            f'x2="{center_x + DiagramElement.CIRCLE_R}" y2="{center_y + (DiagramElement.CIRCLE_R * 2)}" '
            f'stroke="black" marker-end="url(#arrowhead)"/>'
        )

        # 水平線の追加 下側
        svg.append(
            f'<line x1="{center_x - DiagramElement.CIRCLE_R}" y1="{center_y - (DiagramElement.CIRCLE_R * 2)}" '
            f'x2="{center_x + DiagramElement.CIRCLE_R}" y2="{center_y - (DiagramElement.CIRCLE_R * 2)}" '
            f'stroke="black" marker-end="url(#arrowhead)"/>'
        )

        # テキストの描画
        if text != "":
            self.draw_text(svg, center_x + DiagramElement.CIRCLE_R + DiagramElement.SPACE_FIGURE_TO_TEXT, center_y, text)

    def draw_figure_level_gt0(self, svg: list[str], center_x: int, center_y: int, text: str = "") -> None:
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{DiagramElement.CIRCLE_R}" fill="white" stroke="black"/>')

        # テキストの描画
        if text != "":
            self.draw_text(svg, center_x + DiagramElement.CIRCLE_R + DiagramElement.SPACE_FIGURE_TO_TEXT, center_y, text)

    def render(self, line_pairs: list[tuple]) -> str:
        """パースされた要素をSVGとして描画"""
        svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600" style="background-color: #AFC0B1">']

        start_x = 30
        start_y = 30

        # 要素の配置を計算
        elements: list[DiagramElement] = []
        for i, line_pair in enumerate(line_pairs):
            element = DiagramElement()
            element.level = line_pair[0]

            element.x = start_x + element.level * (DiagramElement.LEVEL_SHIFT)
            element.y = start_y + i * (DiagramElement.LEVEL_SHIFT)
            element.content = line_pair[1]
            element.type = DiagramElement.TYPE_NORMAL

            elements.append(element)

        # 図形要素を描画
        before_level = 0
        for element in elements:
            # 種別に応じた図形とテキストを描画
            if element.type == DiagramElement.TYPE_NORMAL:
                if element.level == 0:
                    self.draw_figure_level_eq0(svg, element.x, element.y, element.content)
                else:
                    self.draw_figure_level_gt0(svg, element.x, element.y, element.content)

            # 垂直線の追加
            if (before_level != 0) and (before_level == element.level):
                now_x = element.x
                now_y = element.y - DiagramElement.CIRCLE_R
                next_y = now_y - (DiagramElement.LEVEL_SHIFT - DiagramElement.CIRCLE_R * 2)
                svg.append(f'<line x1="{now_x}" y1="{now_y}" x2="{now_x}" y2="{next_y}" stroke="black" marker-end="url(#arrowhead)"/>')

            # 次の描画準備
            before_level = element.level

        svg.append("</svg>")
        return "\n".join(svg)
