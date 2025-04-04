from line_type import LineTypeDefine, LineTypeEnum


class FileParse:
    def __init__(self) -> None:
        pass

    @staticmethod
    def read_file(file_path: str) -> str:
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

    @staticmethod
    def convert_text2lines(text: str) -> list[str]:
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

    @staticmethod
    def get_module_sections(text_lines: list[str]) -> list[tuple[str, list[str]]]:
        """
        モジュールごとのセクションを取得する

        Args:
            text_lines (list): 取得対象のテキスト行

        Returns:
            list: (モジュール名, セクション行のリスト) のタプルのリスト
        """

        # モジュール名と開始行を保持
        module_start_idx = []
        module_names = []
        for line_num, text_line in enumerate(text_lines):
            if not text_line.strip().startswith(LineTypeDefine.get_format_by_type(LineTypeEnum.MODULE).type_format):
                # モジュール以外の行は無視
                continue

            # 開始位置を保持
            module_start_idx.append(line_num + 1)

            # モジュール名を取得
            split_texts = text_line.strip().split(maxsplit=1)
            module_name = split_texts[1] if len(split_texts) > 1 else "モジュール名無し"
            module_names.append(module_name)

        # モジュールセクションを抽出
        module_sections = []
        for i, start_idx in enumerate(module_start_idx):
            # 次のモジュールの開始位置、またはファイルの終わりまでを取得
            end_idx = module_start_idx[i + 1] - 1 if i + 1 < len(module_start_idx) else len(text_lines) + 1
            section_lines = text_lines[start_idx:end_idx]
            module_sections.append((module_names[i], section_lines))

        return module_sections
