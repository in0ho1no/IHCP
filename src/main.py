import glob
import os

from define import read_file
from parse import SimpleDiagramParser
from render import SVGRenderer


def main() -> None:
    hcp_file_list = glob.glob(r"./src/input/*.hcp")
    for hcp_file in hcp_file_list:
        # ファイル読み込み
        input_text = read_file(hcp_file)

        # パース
        parser = SimpleDiagramParser(input_text)

        # 描画
        renderer = SVGRenderer(parser.process_line_info_list, parser.data_line_info_list)
        svg_output = renderer.render()

        # SVGファイルとして保存
        basename = os.path.basename(hcp_file).split(".")[0]
        with open(f"./src/output/{basename}.svg", "w", encoding="utf-8") as f:
            f.write(svg_output)


if __name__ == "__main__":
    main()
