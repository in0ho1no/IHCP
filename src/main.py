from parse import SimpleDiagramParser
from render import SVGRenderer


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
    line_pairs = parser.get_pair_line_level()
    print(line_pairs)

    renderer = SVGRenderer()
    svg_output = renderer.render(line_pairs)

    # SVGファイルとして保存
    with open("output.svg", "w", encoding="utf-8") as f:
        f.write(svg_output)


if __name__ == "__main__":
    main()
