from typing import List
import os

from .Note import Note


class Writer:
    def __init__(self, filename: str):
        self.filename: str = filename
        self.data: List[str] = []

    def parse(self, bars: List[List[Note]]):
        # TODO: Parsowanie listy nut i wrzucanie ich do listy self.data
        pass

    # region File operations

    def export(self):
        content: str = '\n'.join(self.data)
        f = open('output/source/{}.ly'.format(self.filename), 'w+')
        f.write(content)
        f.close()

    def compile(self):
        os.system('lilypond -o output/compiled output/source/{}.ly'.format(self.filename))

    # endregion
