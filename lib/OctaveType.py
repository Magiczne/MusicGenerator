from __future__ import annotations
from enum import Enum


class OctaveType(Enum):
    DOUBLE_CONTRA = ',,,,'
    SUB_CONTRA = ',,,'
    CONTRA = ',,'
    GREAT = ','
    SMALL = ''
    LINE_1 = '\''
    LINE_2 = '\'\'\''
    LINE_3 = '\'\'\'\''
    LINE_4 = '\'\'\'\'\''
    LINE_5 = '\'\'\'\'\'\''
    LINE_6 = '\'\'\'\'\'\'\''

    @staticmethod
    def get_id(octave_type: OctaveType) -> int:
        return {
            OctaveType.DOUBLE_CONTRA: 0,
            OctaveType.SUB_CONTRA: 1,
            OctaveType.CONTRA: 2,
            OctaveType.GREAT: 3,
            OctaveType.SMALL: 4,
            OctaveType.LINE_1: 5,
            OctaveType.LINE_2: 6,
            OctaveType.LINE_3: 7,
            OctaveType.LINE_4: 8,
            OctaveType.LINE_5: 9,
            OctaveType.LINE_6: 10,
        }[octave_type]

    @staticmethod
    def from_id(octave_id: int) -> OctaveType:
        if octave_id < 0:
            raise KeyError('You will not hear that! Too low!')

        if octave_id > 10:
            raise KeyError('You will not hear that! Too high!')

        return [
            OctaveType.DOUBLE_CONTRA,
            OctaveType.SUB_CONTRA,
            OctaveType.CONTRA,
            OctaveType.GREAT,
            OctaveType.SMALL,
            OctaveType.LINE_1,
            OctaveType.LINE_2,
            OctaveType.LINE_3,
            OctaveType.LINE_4,
            OctaveType.LINE_5,
            OctaveType.LINE_6,
        ][octave_id]

    @staticmethod
    def get_octave_down(octave_type: OctaveType) -> OctaveType:
        return OctaveType.from_id(OctaveType.get_id(octave_type) - 1)
