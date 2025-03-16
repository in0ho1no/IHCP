# IHCP

本ツールは、テキスト形式で記載されたHCPチャートを、SVG画像として描画する

## 実例

例えば、以下のような内容をexample.hcpファイルとして保存しておく。

```
\module example

\data データ1-1
\data データ1-2

処理開始 \in データ1-1 \out データ1-2
    入力に応じた処理を行う
        \fork フラグが有効 \in データ1-1
            \true フラグが有効である
                成功を返す \out データ1-2
            \false フラグが無効である
                失敗を返す \out データ1-2
```

本ツールにてexample.hcpファイルを読み込むと、下図のように描画される。

![実例](./docs/images/example.png)
