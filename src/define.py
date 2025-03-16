from dataclasses import dataclass
from typing import NamedTuple

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
    between_process_data: Line | None = None
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


class ParseInfo(NamedTuple):
    line_info_list: list[LineInfo]
    level_min: int


class ParseInfo4Render(NamedTuple):
    process_parse_info: ParseInfo
    data_parse_info: ParseInfo


@dataclass
class DiagramElement:
    LEVEL_SHIFT = 30

    line_info: LineInfo

    x: int = 0
    y: int = 0

    end_x: int = 0
