from dataclasses import dataclass


@dataclass
class DiagramElement:
    TYPE_NORMAL = 0

    MARGIN = 10

    CIRCLE_R = 9

    level: int = 0
    content: str = ""
    x: int = 0
    y: int = 0
    type: int = TYPE_NORMAL


class SVGRenderer:
    def __init__(self) -> None:
        pass

    def render(self, line_pairs: list[tuple]) -> str:
        """パースされた要素をSVGとして描画"""
        svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">']

        # 要素の配置を計算
        elements: list[DiagramElement] = []
        for i, line_pair in enumerate(line_pairs):
            element = DiagramElement()
            element.x = DiagramElement.MARGIN
            element.y = DiagramElement.MARGIN + i * (DiagramElement.CIRCLE_R * 3)
            element.level = line_pair[0]
            element.content = line_pair[1]
            element.type = DiagramElement.TYPE_NORMAL

            elements.append(element)

        # 図形要素を描画
        for element in elements:
            svg.append(f'<circle cx="{element.x}" cy="{element.y}" r="{DiagramElement.CIRCLE_R}" fill="white" stroke="black"/>')
            svg.append(
                f'<text x="{element.x + DiagramElement.CIRCLE_R + DiagramElement.MARGIN}" '
                f'y="{element.y}" '
                'text-anchor="left" dominant-baseline="middle">'
                f"{element.content}</text>"
            )

        svg.append("</svg>")
        return "\n".join(svg)
