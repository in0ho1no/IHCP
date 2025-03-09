class FileParse:
    def __init__(self) -> None:
        pass

    def read_file(self, file_path: str) -> str:
        """
        ファイルを読み込む

        UTF-8の読み込みに失敗した場合はShift-JISで読み込む

        Args:
            file_path: 読み込むファイルのパス

        Returns:
            str: ファイルの内容

        Raises:
            OSError: ファイル読み込みに失敗した場合
            ValueError: ファイルが空の場合
        """
        try:
            with open(file_path, "rb") as f:
                file_content = f.read()

            if not file_content:
                raise ValueError("ファイルが空です")

            try:
                return file_content.decode("utf-8")
            except UnicodeDecodeError as e_utf8:
                try:
                    return file_content.decode("shift_jis")
                except UnicodeDecodeError as e_shift_jis:
                    raise OSError(f"ファイルをUTF-8/Shift-JISのどちらでもデコードできません: {e_utf8!r}, {e_shift_jis!r}") from e_shift_jis

        except OSError as e:
            raise OSError(f"ファイルの読み込みに失敗しました: {e!r}") from e

    def convert_text2lines(self, text: str) -> list[str]:
        """テキストデータを不要な情報を除去した文字列リストに変換する

        以下取り除く
        - コメント("#"に続く文字列)
        - 空行

        Args:
            text (str): 変換元のテキストデータ

        Returns:
            list[str]: 不要な情報を除いた文字列リスト
        """

        output_lines: list[str] = []
        for text_line in text.strip().split("\n"):
            # コメントは削除する
            line_deleted_comment = text_line.split("#")[0]

            # 空行は無視する
            if len(line_deleted_comment.strip()) == 0:
                continue

            # 残った文字列をリストに追加する
            output_lines.append(line_deleted_comment)

        return output_lines
