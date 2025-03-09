from dataclasses import dataclass
from enum import Enum, auto


@dataclass
class LineTypeFormat:
    """行の種別とその形式を表す"""

    type_value: int = 0
    type_format: str = ""


class LineTypeEnum(Enum):
    """行の種別を表す列挙型"""

    NORMAL = auto()
    FORK = auto()
    REPEAT = auto()
    MOD = auto()
    RETURN = auto()
    TRUE = auto()
    FALSE = auto()
    BRANCH = auto()
    DATA = auto()
    MODULE = auto()


@dataclass
class LineTypeDefine:
    """行の種別定義を管理する"""

    # 種別と形式のマッピング
    _TYPE_FORMATS = {
        LineTypeEnum.NORMAL: LineTypeFormat(0, ""),
        LineTypeEnum.FORK: LineTypeFormat(1, "\\fork"),
        LineTypeEnum.REPEAT: LineTypeFormat(2, "\\repeat"),
        LineTypeEnum.MOD: LineTypeFormat(3, "\\mod"),
        LineTypeEnum.RETURN: LineTypeFormat(4, "\\return"),
        LineTypeEnum.TRUE: LineTypeFormat(5, "\\true"),
        LineTypeEnum.FALSE: LineTypeFormat(6, "\\false"),
        LineTypeEnum.BRANCH: LineTypeFormat(7, "\\branch"),
        LineTypeEnum.DATA: LineTypeFormat(8, "\\data"),
        LineTypeEnum.MODULE: LineTypeFormat(9, "\\module"),
    }

    # 形式から種別へのマッピングを構築
    _FORMAT_TO_TYPE = {
        format_obj.type_format: enum_type for enum_type, format_obj in _TYPE_FORMATS.items() if format_obj.type_format
    }  # 空文字列は除外

    @classmethod
    def get_format_by_type(cls, type_enum: LineTypeEnum) -> LineTypeFormat:
        """種別に対応する形式情報を取得する"""
        return cls._TYPE_FORMATS[type_enum]

    @classmethod
    def get_type_by_format(cls, format_str: str) -> LineTypeEnum | None:
        """形式文字列に対応する種別を取得する

        NORMALは種別を特定しようがないのでNoneを返す(初回構築時にマッピングに含めていない)
        """
        return cls._FORMAT_TO_TYPE.get(format_str)

    @classmethod
    def get_all_formats(cls) -> list[LineTypeFormat]:
        """すべての形式情報のリストを取得する"""
        return list(cls._TYPE_FORMATS.values())


class LineType:
    @classmethod
    def get_line_type(cls, line: str) -> tuple[LineTypeFormat, str]:
        """与えられた行の種別を取得する

        想定しない種別の場合はエラーを返す

        Args:
            line (str): 種別を取得したい行

        Returns:
            int: タブの数(半角空白なら4文字)をレベルとして返す
        """
        # 空行は無視する
        strip_line = line.strip()
        if strip_line is None:
            return (LineTypeDefine.get_format_by_type(LineTypeEnum.NORMAL), line)

        # 種別指定が区切られていない行は無視する
        if " " not in strip_line:
            return (LineTypeDefine.get_format_by_type(LineTypeEnum.NORMAL), line)

        # 行の先頭要素と残りの文字列を保持する
        first_elem, *rest = strip_line.split(" ", maxsplit=1)
        remainder = rest[0] if rest else ""

        # 種別指定のない行は無視する
        if not first_elem.startswith("\\"):
            return (LineTypeDefine.get_format_by_type(LineTypeEnum.NORMAL), line)

        # 先頭要素と一致した種別を返す
        line_type_enum = LineTypeDefine.get_type_by_format(first_elem)
        if line_type_enum:
            return LineTypeDefine.get_format_by_type(line_type_enum), remainder

        # 一致する種別無し
        return (LineTypeDefine.get_format_by_type(LineTypeEnum.NORMAL), line)
