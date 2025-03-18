import math
from collections.abc import Callable

from define import DiagramElement
from line_type import LineTypeDefine, LineTypeEnum


class DrawSvg:
    CIRCLE_R = 9
    ARROW_HEAD = 8

    SPACE_FIGURE_TO_TEXT = 10
    TEXT_MARGIN = 15

    @classmethod
    def get_string_bytes(cls, string: str) -> int:
        count = 0
        for char in string:
            # ASCII文字(1バイト文字)
            if ord(char) < 128:
                count += 1
            # それ以外(2バイト文字)
            else:
                count += 2
        return count

    def get_text_width(self, text: str) -> int:
        text_bytes = self.get_string_bytes(text.strip())
        half_bytes = int((text_bytes + 2 - 1) // 2)
        text_width = half_bytes * 15  # デフォルトの文字幅は16px
        return text_width

    def draw_text(self, svg: list[str], center_x: int, center_y: int, text: str, font_size: int = 100, rotate: int = 0) -> int:
        svg.append(
            f'<text x="{center_x}" y="{center_y}" '
            f'text-anchor="start" dominant-baseline="middle" '
            f'font-family="Consolas, Meiryo UI, Courier New, monospace" '
            f'font-size="{font_size}%" rotate="{rotate}">{text}</text>'
        )
        text_width = int(self.get_text_width(text) * (font_size / 100))
        return text_width

    def draw_string(self, svg: list[str], center_x: int, center_y: int, text: str, font_size: int = 100, rotate: int = 0) -> int:
        if text != "":
            figure_2_text_space = self.CIRCLE_R + self.SPACE_FIGURE_TO_TEXT
            text_width = self.draw_text(svg, center_x + figure_2_text_space, center_y, text, font_size, rotate)
        else:
            figure_2_text_space = self.CIRCLE_R
            text_width = 0

        # 終端位置を返す
        end_x = center_x + figure_2_text_space + text_width + DrawSvg.TEXT_MARGIN
        return end_x

    @staticmethod
    def draw_line(svg: list[str], x1: int, y1: int, x2: int, y2: int, color: str = "black") -> None:
        svg.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}"/>')

    def draw_line_h(self, svg: list[str], center_x: int, center_y: int, length: int, color: str = "black") -> None:
        self.draw_line(svg, x1=center_x, y1=center_y, x2=(center_x + length), y2=center_y, color=color)

    def draw_line_v(self, svg: list[str], center_x: int, center_y: int, length: int, color: str = "black") -> None:
        self.draw_line(svg, x1=center_x, y1=center_y, x2=center_x, y2=(center_y + length), color=color)

    def draw_arrow_r(self, svg: list[str], center_x: int, center_y: int, length: int, color: str = "black") -> None:
        end_x = center_x + length
        self.draw_line(svg, x1=center_x, y1=center_y, x2=end_x, y2=center_y, color=color)
        arrow_hed = self.ARROW_HEAD
        svg.append(
            f'<path d="M {end_x} {center_y} '
            f'L {end_x - arrow_hed} {center_y - int(arrow_hed / 2)} L {end_x - arrow_hed} {center_y + int(arrow_hed / 2)}" '
            f'stroke="{color}" fill="{color}" />'
        )

    def draw_arrow_l(self, svg: list[str], center_x: int, center_y: int, length: int, color: str = "black") -> None:
        end_x = center_x + length
        self.draw_line(svg, x1=center_x, y1=center_y, x2=end_x, y2=center_y, color=color)
        arrow_hed = self.ARROW_HEAD
        svg.append(
            f'<path d="M {center_x} {center_y} '
            f'L {center_x + arrow_hed} {center_y - int(arrow_hed / 2)} L {center_x + arrow_hed} {center_y + int(arrow_hed / 2)}" '
            f'stroke="{color}" fill="{color}" />'
        )

    def draw_figure_level_start(self, svg: list[str], center_x: int, center_y: int) -> None:
        # 垂直線の追加 上
        self.draw_line_v(svg, center_x, center_y - self.CIRCLE_R * 2, self.CIRCLE_R)
        # 水平線の追加 上
        self.draw_line_h(svg, (center_x - self.CIRCLE_R), center_y - (self.CIRCLE_R * 2), (self.CIRCLE_R * 2))

    def draw_figure_level_end(self, svg: list[str], center_x: int, center_y: int) -> None:
        # 垂直線の追加 下
        self.draw_line_v(svg, center_x, center_y + self.CIRCLE_R, self.CIRCLE_R)
        # 水平線の追加 下
        self.draw_line_h(svg, (center_x - self.CIRCLE_R), center_y + (self.CIRCLE_R * 2), (self.CIRCLE_R * 2))

    def draw_figure_level_step(self, svg: list[str], center_x: int, center_y: int) -> None:
        # 垂直線の追加 上
        self.draw_line_v(svg, center_x, center_y - self.CIRCLE_R * 2, self.CIRCLE_R)
        # 水平線の追加 上
        self.draw_line_h(svg, (center_x - self.CIRCLE_R * 2), center_y - (self.CIRCLE_R * 2), (self.CIRCLE_R * 2))
        # 垂直線の追加 上
        self.draw_line_v(svg, (center_x - self.CIRCLE_R * 2), center_y - self.CIRCLE_R * 4, self.CIRCLE_R * 2)

    def draw_figure_normal(self, svg: list[str], center_x: int, center_y: int, text: str = "") -> int:
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{self.CIRCLE_R}" fill="white" stroke="black"/>')

        # 文字列の描画
        end_x = self.draw_string(svg, center_x, center_y, text)

        # 終端位置を返す
        return end_x

    @staticmethod
    def __get_vertices_polygon(
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
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{self.CIRCLE_R}" fill="white" stroke="black"/>')

        # 正三角形の描画
        vertices = self.__get_vertices_polygon(3, center_x, center_y, self.CIRCLE_R - 2, rotation)
        svg.append(
            f'<polygon points="{vertices[0][0]} {vertices[0][1]} {vertices[1][0]} {vertices[1][1]} {vertices[2][0]} {vertices[2][1]}" '
            f'fill="white" stroke="black"/>'
        )

        # 文字列の描画
        end_x = self.draw_string(svg, center_x, center_y, text)

        # 終端位置を返す
        return end_x

    def draw_figure_repeat(
        self,
        svg: list[str],
        center_x: int,
        center_y: int,
        text: str = "",
    ) -> int:
        # 円の描画
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{self.CIRCLE_R}" fill="white" stroke="black"/>')

        # 記号の描画
        self.draw_text(svg, center_x + 8, center_y - 1, "↻", rotate=240)

        # 文字列の描画
        end_x = self.draw_string(svg, center_x, center_y, text)

        # 終端位置を返す
        return end_x

    def draw_figure_mod(self, svg: list[str], center_x: int, center_y: int, text: str = "") -> int:
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{self.CIRCLE_R}" fill="white" stroke="black"/>')
        svg.append(f'<circle cx="{center_x}" cy="{center_y}" r="{int(self.CIRCLE_R / 2)}" fill="white" stroke="black"/>')

        # 文字列の描画
        end_x = self.draw_string(svg, center_x, center_y, text)

        # 終端位置を返す
        return end_x

    def draw_figure_return(
        self,
        svg: list[str],
        center_x: int,
        center_y: int,
        text: str = "",
    ) -> int:
        # 垂直線の追加 上
        self.draw_line_v(svg, center_x, center_y - self.CIRCLE_R, self.CIRCLE_R)

        # 正三角形の描画
        vertices = self.__get_vertices_polygon(3, center_x, center_y, self.CIRCLE_R, (math.pi / 2))
        svg.append(
            f'<polygon points="{vertices[0][0]} {vertices[0][1]} {vertices[1][0]} {vertices[1][1]} {vertices[2][0]} {vertices[2][1]}" '
            f'fill="white" stroke="black"/>'
        )

        # 水平線の追加 下
        self.draw_line_h(svg, (center_x - self.CIRCLE_R), center_y + self.CIRCLE_R, (self.CIRCLE_R * 2))

        # 文字列の描画
        end_x = self.draw_string(svg, center_x, center_y, text)

        # 終端位置を返す
        return end_x

    def __draw_figure_cond(self, svg: list[str], center_x: int, center_y: int, text: str = "") -> int:
        # 垂直線の追加
        self.draw_line_v(svg, center_x, center_y - self.CIRCLE_R, self.CIRCLE_R * 2)

        self.draw_arrow_r(svg, center_x, center_y - self.CIRCLE_R, 15)

        # テキストの描画
        figure_2_text_space = self.CIRCLE_R + self.SPACE_FIGURE_TO_TEXT
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
            f'<rect x="{center_x - self.CIRCLE_R}" y="{center_y - self.CIRCLE_R}" '
            f'width="{self.CIRCLE_R * 2}" height="{self.CIRCLE_R * 2}" fill="white" stroke="black"/>'
        )

        # 文字列の描画
        end_x = self.draw_string(svg, center_x, center_y, text)

        # 終端位置を返す
        return end_x

    @staticmethod
    def draw_figure_data_func_in(svg: list[str], center_x: int, center_y: int) -> None:
        svg.append(
            f'<path d="M {center_x - DrawSvg.CIRCLE_R} {center_y} '  # 描画開始位置指定
            f"L {center_x} {center_y - DrawSvg.CIRCLE_R} "  # 上弦描画
            f"L {center_x} {center_y + DrawSvg.CIRCLE_R} "  # 縦線描画
            f'Z" '  # パスを閉じる
            f'stroke="black" fill="fuchsia" />'
        )

    @staticmethod
    def draw_figure_data_func_out(svg: list[str], center_x: int, center_y: int) -> None:
        svg.append(
            f'<path d="M {center_x + DrawSvg.CIRCLE_R} {center_y} '  # 描画開始位置指定
            f"L {center_x} {center_y - DrawSvg.CIRCLE_R} "  # 上弦描画
            f"L {center_x} {center_y + DrawSvg.CIRCLE_R} "  # 縦線描画
            f'Z" '  # パスを閉じる
            f'stroke="black" fill="aqua" />'
        )


class DrawFigure:
    """図形描画を管理するクラス"""

    def __init__(self, draw_svg: DrawSvg):
        """
        初期化メソッド

        Args:
            draw_svg: SVG描画オブジェクト
        """
        self.draw_svg = draw_svg

        # 種別値と描画メソッドのマッピングテーブルを構築
        self._figure_method_map: dict[int, Callable] = {
            LineTypeDefine.get_format_by_type(LineTypeEnum.NORMAL).type_value: self.draw_svg.draw_figure_normal,
            LineTypeDefine.get_format_by_type(LineTypeEnum.FORK).type_value: self.draw_svg.draw_figure_fork,
            LineTypeDefine.get_format_by_type(LineTypeEnum.REPEAT).type_value: self.draw_svg.draw_figure_repeat,
            LineTypeDefine.get_format_by_type(LineTypeEnum.MOD).type_value: self.draw_svg.draw_figure_mod,
            LineTypeDefine.get_format_by_type(LineTypeEnum.RETURN).type_value: self.draw_svg.draw_figure_return,
            LineTypeDefine.get_format_by_type(LineTypeEnum.TRUE).type_value: self.draw_svg.draw_figure_true,
            LineTypeDefine.get_format_by_type(LineTypeEnum.FALSE).type_value: self.draw_svg.draw_figure_false,
            LineTypeDefine.get_format_by_type(LineTypeEnum.BRANCH).type_value: self.draw_svg.draw_figure_branch,
            LineTypeDefine.get_format_by_type(LineTypeEnum.DATA).type_value: self.draw_svg.draw_figure_data,
        }

    def draw_figure_method(self, svg: list[str], element: DiagramElement) -> int:
        """
        要素の種別に応じた図形を描画する

        Args:
            svg: SVGオブジェクト
            element: 描画要素情報

        Returns:
            int: 描画した図形の終端X座標
        """
        # 要素の種別に対応するメソッドを取得
        draw_method = self._figure_method_map.get(element.line_info.type.type_value)

        # メソッドが見つかれば実行する
        if draw_method:
            return int(draw_method(svg, element.x, element.y, element.line_info.text_clean))
        return 0
