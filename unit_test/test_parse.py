import pytest

from src.parse import SimpleDiagramParser


@pytest.fixture
def parser() -> SimpleDiagramParser:
    """テスト用のパーサーインスタンスを生成するフィクスチャ"""
    return SimpleDiagramParser([])


class TestCreateIndentPattern:
    """create_indent_patternメソッドのテストクラス"""

    def test_valid_tab_count(self, parser: SimpleDiagramParser) -> None:
        """正常なtab_countでパターンが正しく生成されることを確認"""
        pattern = parser.create_indent_pattern(1)
        assert "^(?:[ ]{4}|\t{1})\\S.*$" == pattern

    def test_zero_tab_count(self, parser: SimpleDiagramParser) -> None:
        """tab_count=0でパターンが正しく生成されることを確認"""
        pattern = parser.create_indent_pattern(0)
        assert "^(?:[ ]{0}|\t{0})\\S.*$" == pattern

    def test_negative_tab_count(self, parser: SimpleDiagramParser) -> None:
        """負のtab_countで例外が発生することを確認"""
        with pytest.raises(ValueError, match="tab_count must be non-negative"):
            parser.create_indent_pattern(-1)


class TestGetLineLevel:
    """get_line_levelメソッドのテストクラス"""

    @pytest.mark.parametrize(
        "input_line,expected_level",
        [
            ("No indent", 0),  # インデントなし
            ("    First level", 1),  # 4スペース
            ("\tFirst level", 1),  # 1タブ
            ("        Second level", 2),  # 8スペース
            ("\t\tSecond level", 2),  # 2タブ
        ],
    )
    def test_valid_indentation(self, parser: SimpleDiagramParser, input_line: str, expected_level: int) -> None:
        """正常なインデントのテスト"""
        assert parser.get_line_level(input_line) == expected_level

    @pytest.mark.parametrize(
        "input_line",
        [
            "",  # 空文字列
            "   ",  # スペースのみ
            "\t  ",  # タブとスペース
            "\n",  # 改行のみ
        ],
    )
    def test_empty_lines(self, parser: SimpleDiagramParser, input_line: str) -> None:
        """空行のテスト"""
        assert parser.get_line_level(input_line) == SimpleDiagramParser.LEVEL_NONE

    @pytest.mark.parametrize(
        "input_line",
        [
            "   Wrong indent",  # 3スペース（4の倍数でない）
            "\t    Mixed",  # タブとスペースの混在
            "\t\t\t\t\t\t\t\t\tTooManySpaces",  # レベルMAX以上のスペース
        ],
    )
    def test_invalid_indentation(self, parser: SimpleDiagramParser, input_line: str) -> None:
        """不正なインデントのテスト"""
        assert parser.get_line_level(input_line) == SimpleDiagramParser.LEVEL_ERROR


class TestParserInitialization:
    """パーサーの初期化テスト"""

    def test_initialization(self) -> None:
        """正常な初期化のテスト"""
        test_data = ["line1", "line2"]
        parser = SimpleDiagramParser(test_data)
        assert parser.text_data == test_data

    def test_empty_initialization(self) -> None:
        """空リストでの初期化テスト"""
        parser = SimpleDiagramParser([])
        assert parser.text_data == []


class TestConstants:
    """定数値の検証テスト"""

    def test_constant_values(self) -> None:
        """各定数が期待値と一致することを確認"""
        assert SimpleDiagramParser.LEVEL_MIN == 0
        assert SimpleDiagramParser.LEVEL_MAX == 9
        assert SimpleDiagramParser.LEVEL_ERROR == -1
        assert SimpleDiagramParser.LEVEL_NONE == -2
        assert SimpleDiagramParser.TAB2SPACE == 4
