from dataclasses import dataclass


@dataclass
class LineInfo:
    DEFAULT_VALUE = -1

    no: int = DEFAULT_VALUE
    level: int = DEFAULT_VALUE
    text: str = ""

    next_no: int = DEFAULT_VALUE
    before_no: int = DEFAULT_VALUE


@dataclass
class DiagramElement:
    TYPE_NORMAL = 0

    MARGIN = 15

    CIRCLE_R = 9
    FIGURE_WIDTH = CIRCLE_R * 2
    FIGURE_HEIGHT = CIRCLE_R * 4

    SPACE_FIGURE_TO_TEXT = 15

    LEVEL_SHIFT = 30

    line_info: LineInfo

    x: int = 0
    y: int = 0
    type: int = TYPE_NORMAL
