from define import LineInfo
from parse import SimpleDiagramParser
from render import SVGRenderer


def main() -> None:
    # 入力テキスト ファイルから読み込む際もrawデータで読むこと
    input_text = r"""
処理開始
    必要な情報を揃える
        排他を取得
        DBから取得
        排他を解放
    データ更新
        更新が必要か判定する
    更新に伴った処理
        機能Aの実行
            機能Aの前処理
            機能Aの本処理
                \fork 条件を満足する
                    \true 条件を満足した
                        \mod 関数を呼び出す
                    \false 条件を満足しなかった
                        何もしない
            機能Aの後処理
        機能Bの実行
            機能Bの前処理
            機能Bの後処理
    処理終了
        戻り値を返す
            \return TRUE(成功値) 固定

"""

    # パースと描画
    parser = SimpleDiagramParser(input_text)
    line_pairs = parser.get_pair_line_level()
    print(line_pairs)
    line_info_list = parser.create_line_info_list()

    renderer = SVGRenderer()
    svg_output = renderer.render(line_info_list)

    # SVGファイルとして保存
    with open("output.svg", "w", encoding="utf-8") as f:
        f.write(svg_output)


if __name__ == "__main__":
    main()
