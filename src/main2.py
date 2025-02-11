import re
from dataclasses import dataclass
from typing import List, Tuple

from parse import SimpleDiagramParser


@dataclass
class DiagramElement:
    type: str
    content: str
    x: int = 0
    y: int = 0
    width: int = 100
    height: int = 50


class SVGRenderer:
    def __init__(self, parser: SimpleDiagramParser):
        self.parser = parser

    def render(self) -> str:
        """パースされた要素をSVGとして描画"""
        svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="800" height="600">']

        # 要素の配置を計算（簡単な例として横一列に配置）
        for i, element in enumerate(self.parser.elements):
            element.x = 100 + i * 150
            element.y = 100

        # 図形要素を描画
        for element in self.parser.elements:
            svg.append(f'<rect x="{element.x}" y="{element.y}" width="{element.width}" height="{element.height}" fill="white" stroke="black"/>')
            svg.append(
                f'<text x="{element.x + element.width / 2}" '
                f'y="{element.y + element.height / 2}" '
                'text-anchor="middle" dominant-baseline="middle">'
                f"{element.content}</text>"
            )

        # 接続線を描画
        for start, end in self.parser.connections:
            start_idx = int(start[-1]) - 1  # 簡易的なインデックス取得
            end_idx = int(end[-1]) - 1
            start_element = self.parser.elements[start_idx]
            end_element = self.parser.elements[end_idx]

            svg.append(
                f'<line x1="{start_element.x + start_element.width}" '
                f'y1="{start_element.y + start_element.height / 2}" '
                f'x2="{end_element.x}" '
                f'y2="{end_element.y + end_element.height / 2}" '
                'stroke="black" marker-end="url(#arrowhead)"/>'
            )

        svg.append("</svg>")
        return "\n".join(svg)


def main() -> None:
    # 入力テキスト
    input_text = """
必要な情報を揃える
    排他を取得
    DBから取得
    排他を解放
"""

    # パースと描画
    parser = SimpleDiagramParser(input_text)
    print(parser.get_pair_line_level())

    # renderer = SVGRenderer(parser)
    # svg_output = renderer.render()

    # # SVGファイルとして保存
    # with open("output.svg", "w") as f:
    #     f.write(svg_output)


if __name__ == "__main__":
    main()
