import glob
import os
from typing import NamedTuple

from parse import DiagramParser
from parse_file import FileParse
from render import SVGRenderer


class HCPInfo(NamedTuple):
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

        # 描画
        renderer = SVGRenderer(parser.process_line_info_list, parser.data_line_info_list)
        svg_output = renderer.render()
        hcp_info_list.append(HCPInfo(section_name, section_lines, svg_output))

    return hcp_info_list


def main() -> None:
    input_folder = ".\\src\\input\\"
    hcp_file_list = glob.glob(input_folder + "**\\*.hcp", recursive=True)
    for hcp_file in hcp_file_list:
        # ファイルを読み込んでSVG画像として保存する
        hcp_info_list = convert_file2hcp_info_list(hcp_file)
        for hcp_info in hcp_info_list:
            # SVG画像として保存
            file_path = hcp_file.replace(input_folder, "")
            rename_path = "_".join(file_path.split("\\"))
            basename = os.path.basename(rename_path).split(".")[0]
            with open(f"./src/output/{basename}_{hcp_info.name}.svg", "w", encoding="utf-8") as f:
                f.write(hcp_info.svg_img)


if __name__ == "__main__":
    main()
