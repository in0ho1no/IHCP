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


@dataclass
class DataInfo:
    name: str
    connect_line: Process2Data | None = None


@dataclass
class InOutData:
    in_data_list: list[DataInfo]
    out_data_list: list[DataInfo]


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

    data_color: str = "black"

    def __post_init__(self) -> None:
        if self.level is None:
            self.level = LineLevel()

        if self.type is None:
            self.type = LineTypeFormat()


@dataclass
class DiagramElement:
    MARGIN = 15

    CIRCLE_R = 9
    FIGURE_WIDTH = CIRCLE_R * 2
    FIGURE_HEIGHT = CIRCLE_R * 4

    SPACE_FIGURE_TO_TEXT = 10

    LEVEL_SHIFT = 30

    line_info: LineInfo

    x: int = 0
    y: int = 0

    end_x: int = 0


def get_string_bytes(string: str) -> int:
    count = 0
    for char in string:
        # ASCII文字(1バイト文字)
        if ord(char) < 128:
            count += 1
        # それ以外(2バイト文字)
        else:
            count += 2
    return count
