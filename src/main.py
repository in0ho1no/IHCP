from parse import SimpleDiagramParser
from render import SVGRenderer


def main() -> None:
    # 入力テキスト ファイルから読み込む際もrawデータで読むこと
    input_text = r"""
\data データ1
    \data データ1-1
\data データ2
\data データ3
\data データ4
\data データ5
\data データ6
\data データ7

処理開始
    必要な情報を揃える
        排他を取得
        \repeat DBから取得 \in データ1 \out データ2
        排他を解放
    データ更新
        更新が必要か判定する \in データ2 \out データ3
    更新に伴った処理
        機能Aの実行
            機能Aの前処理 \in データ1-1
            機能Aの本処理
                \fork 条件を満足する  \in データ3 \out データ4
                    \true 条件を満足した
                        \mod 関数を呼び出す \out データ5
                        \fork 呼び出し結果に応じて分岐する \in データ5
                            \branch 成功したので出力有り
                                OK1
                            \branch 成功したが出力無し
                                OK2
                            \branch 失敗したが出力有り
                                NG1
                            \branch 失敗したので出力無し
                                NG2
                    \false 条件を満足しなかった
                        何もしない
                \return 9
            機能Aの後処理
        機能Bの実行
            機能Bの前処理
            機能Bの後処理
            \return 2
    処理終了
        戻り値を返す
            \return TRUE(成功値) 固定

"""

    # パースと描画
    parser = SimpleDiagramParser(input_text)

    renderer = SVGRenderer()
    svg_output = renderer.render(parser.process_line_info_list, parser.data_line_info_list)

    # SVGファイルとして保存
    with open(r"./src/output/output.svg", "w", encoding="utf-8") as f:
        f.write(svg_output)


if __name__ == "__main__":
    main()
