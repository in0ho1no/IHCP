import glob

from parse import SimpleDiagramParser
from render import SVGRenderer


def main() -> None:
    # 入力テキスト ファイルから読み込む際もrawデータで読むこと
    # HCPファイル読み込み
    hcp_file_list = glob.glob(r"./src/input/*.hcp")
    for hcp_file in hcp_file_list:
        with open(hcp_file, encoding="utf-8") as f:
            input_text = f.read()

        # パースと描画
        parser = SimpleDiagramParser(input_text)

        renderer = SVGRenderer(parser.process_line_info_list, parser.data_line_info_list)
        svg_output = renderer.render()

        # SVGファイルとして保存
        with open(r"./src/output/output.svg", "w", encoding="utf-8") as f:
            f.write(svg_output)


if __name__ == "__main__":
    main()
