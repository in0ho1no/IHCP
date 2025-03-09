import glob
import os

from parse import DiagramParser
from parse_file import FileParse
from render import SVGRenderer


def main() -> None:
    input_folder = ".\\src\\input\\"
    hcp_file_list = glob.glob(input_folder + "**\\*.hcp", recursive=True)
    for hcp_file in hcp_file_list:
        # ファイル読み込み
        file_parser = FileParse()
        file_text = file_parser.read_file(hcp_file)
        file_lines = file_parser.convert_text2lines(file_text)

        # パース
        parser = DiagramParser(file_lines)

        # 描画
        renderer = SVGRenderer(parser.process_line_info_list, parser.data_line_info_list)
        svg_output = renderer.render()

        # SVGファイルとして保存
        file_path = hcp_file.replace(input_folder, "")
        rename_path = "_".join(file_path.split("\\"))
        basename = os.path.basename(rename_path).split(".")[0]
        with open(f"./src/output/{basename}.svg", "w", encoding="utf-8") as f:
            f.write(svg_output)


if __name__ == "__main__":
    main()
