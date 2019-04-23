from typing import List, Optional
import os

from .BarType import BarType
from .KeyType import KeyType
from .Note import Note


class Writer:
    def __init__(self, filename: str):
        self.filename: str = filename
        self.lines: List[str] = []

    # region Data appending utils

    def blank(self):
        self.lines.append('')

    def line(self, data: str, indent: int = 0):
        indent_str = self.get_indent(indent)
        self.lines.append('{}{}'.format(indent_str, data))

    def command(self, data: str, indent: int = 0):
        indent_str = self.get_indent(indent)
        self.lines.append('{}\\{}'.format(indent_str, data))

    def block_start(self, name: Optional[str], indent: int = 0):
        if name is None:
            self.line('{', indent)
        else:
            self.command('{} {{'.format(name), indent)

    def block_end(self, indent: int = 0):
        self.line('}', indent)

    # endregion

    # region Other utils

    @staticmethod
    def get_indent(indent: int) -> str:
        return '' if indent <= 0 else '\t' * indent

    @staticmethod
    def get_bar(bar_type: BarType):
        return '\\bar "{}"'.format(bar_type.value)

    # endregion

    # region Lilypond file parts

    def header(self, paper_size: str = 'a4', show_bar_numbers: bool = True):
        self.command('version "2.18.2"')
        self.blank()
        self.block_start('paper')
        self.line('#(set-paper-size "{}")'.format(paper_size), indent=1)
        self.block_end()
        self.blank()

        if not show_bar_numbers:
            self.block_start('layout')
            self.line('indent = 0\in', indent=1)
            self.line('ragged-last = ##f', indent=1)
            self.command('context {', indent=1)
            self.command('Score', indent=2)
            self.command('remove "Bar_number_engraver"', indent=2)
            self.block_end(indent=1)
            self.block_end()
            self.blank()

    def time_signature(self, n: int, m: int, indent: int = 0):
        self.command('time {}/{}'.format(n, m), indent)

    def key_signature(self, key: str, key_type: KeyType, indent: int = 0):
        self.command('key {} \\{}'.format(key, key_type.value), indent)

    # endregion

    # region File operations

    def export(self):
        content: str = '\n'.join(self.lines)
        f = open('output/source/{}.ly'.format(self.filename), 'w+')
        f.write(content)
        f.close()

    def compile(self):
        os.system('lilypond -o output/compiled output/source/{}.ly'.format(self.filename))

    # endregion

    def parse(self, bars: List[List[Note]]):
        # TODO: Parsowanie listy nut i wrzucanie ich do listy self.data
        pass
