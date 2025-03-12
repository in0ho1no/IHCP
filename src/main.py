import glob
import os

from define import ParseInfo, ParseInfo4Render
from parse import DiagramParser
from parse_file import FileParse
from render import SVGRenderer


def convert_file2svg_tuple_list(file_path: str) -> list[tuple[str, str]]:
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
    svg_tuple_list = []
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
        svg_tuple_list.append((section_name, svg_output))

    return svg_tuple_list


def main() -> None:
    input_folder = ".\\src\\input\\"
    hcp_file_list = glob.glob(input_folder + "**\\*.hcp", recursive=True)
    for hcp_file in hcp_file_list:
        # ファイルを読み込んでSVG画像として保存する
        svg_tuple_list = convert_file2svg_tuple_list(hcp_file)
        for svg_tuple in svg_tuple_list:
            # SVG画像として保存
            file_path = hcp_file.replace(input_folder, "")
            rename_path = "_".join(file_path.split("\\"))
            basename = os.path.basename(rename_path).split(".")[0]
            with open(f"./src/output/{basename}_{svg_tuple[0]}.svg", "w", encoding="utf-8") as f:
                f.write(svg_tuple[1])


if __name__ == "__main__":
    main()
