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
