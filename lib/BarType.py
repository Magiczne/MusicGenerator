from enum import Enum


class BarType(Enum):
    SIMPLE_NARROW = '|'
    SIMPLE_WIDE = '.'
    DOUBLE_NARROW = '||'
    DOUBLE_NARROW_WIDE = '|.'
    DOUBLE_WIDE = '..'
    DOUBLE_WIDE_NARROW = '.|'
    TRIPLE_NARROW_WIDE_NARROW = '|.|'

    REP_START = '.|:'
    REP_END = ':|.'
    REP_BOTH_WIDE_WIDE = ':..:'
    REP_BOTH_NARROW_WIDE_NARROW = ':|.|:'
    REP_BOTH_NARROW_WIDE = ':|.:'
    REP_BOTH_WIDE_NARROW_WIDE = ':.|.:'
    REP_BRACKET_START = '[|:'
    REP_BRACKET_BOTH = ':|][|:'
    REP_BRACKET_END = ':|]'

    DOTTED = ';'
    DASHED = '!'

    TICK = '\''
