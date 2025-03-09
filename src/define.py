from dataclasses import dataclass

from line_level import LineLevel
from line_type import LineTypeFormat


@dataclass
class Coordinate:
    x: int
    y: int


class Line:
    start: Coordinate
    end: Coordinate

    def line_width(self) -> int:
        return abs(self.start.x - self.end.x)

    def line_height(self) -> int:
        return abs(self.start.y - self.end.y)


@dataclass
class Process2Data:
    exit_from_process: Line | None = None
    between_prcess_data: Line | None = None
    enter_to_data: Line | None = None
    color: str = "black"


@dataclass
class DataInfo:
    name: str
    connect_line: Process2Data | None = None


@dataclass
class InOutData:
    in_data_list: list[DataInfo]
    out_data_list: list[DataInfo]
    process_level: int


@dataclass
class LineInfo:
    DEFAULT_VALUE = -1

    text_org: str = ""
    level: LineLevel | None = None

    type: LineTypeFormat | None = None
    text_typeless: str = ""

    iodata: InOutData | None = None
    text_clean: str = ""

    no: int = DEFAULT_VALUE
    next_no: int = DEFAULT_VALUE
    before_no: int = DEFAULT_VALUE

    def __post_init__(self) -> None:
        if self.level is None:
            self.level = LineLevel()

        if self.type is None:
            self.type = LineTypeFormat()


@dataclass
class DiagramElement:
    LEVEL_SHIFT = 30

    line_info: LineInfo

    x: int = 0
    y: int = 0

    end_x: int = 0


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
