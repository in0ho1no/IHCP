from typing import NamedTuple

from define import ParseInfo, ParseInfo4Render
from parse import DiagramParser
from parse_file import FileParse
from render import SVGRenderer


class HCPInfo(NamedTuple):
    """hcpに関する情報

    Attributes:
        name(str): モジュール名
        raw_text(list[str]): svgへ変換する基の生文字列
        svg_img(str): hcpファイルをパースしてレンダリングしたsvg画像の文字列
    """

    name: str
    raw_text: list[str]
    svg_img: str


def convert_file2hcp_info_list(file_path: str) -> list[HCPInfo]:
    """ファイルからモジュール単位のSVG情報を取得する

    Args:
        file_path (str): 読み込むファイルパス

    Returns:
        list[tuple[str, str]]: モジュール名とモジュールのSVGから成るタプルのリスト
    """
    # ファイル読み込み
    file_parser = FileParse()
    file_text = file_parser.read_file(file_path)
    file_lines = file_parser.convert_text2lines(file_text)

    # モジュールごとに処理する
    hcp_info_list: list[HCPInfo] = []
    module_sections = file_parser.get_module_sections(file_lines)
    for module_section in module_sections:
        section_name = module_section[0]
        section_lines = module_section[1]

        # パース
        parser = DiagramParser(section_lines)
        parse_info_4_render = ParseInfo4Render(
            ParseInfo(parser.process_line_info_list, parser.process_level_min),
            ParseInfo(parser.data_line_info_list, parser.data_level_min),
        )

        # 描画
        renderer = SVGRenderer(section_name, parse_info_4_render)
        svg_output = renderer.render()
        hcp_info_list.append(HCPInfo(section_name, section_lines, svg_output))

    return hcp_info_list
