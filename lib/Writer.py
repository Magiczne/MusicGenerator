from typing import List, Optional
import os

from lib.BarType import BarType
from lib.KeyType import KeyType
from lib.theory.Writeable import Writeable


class Writer:
    def __init__(self, filename: str):
        self.filename: str = filename
        self.lines: List[str] = []

        self.source_dir = 'output/source'
        self.compiled_dir = 'output/compiled'

    # region Data appending utils

    def blank(self):
        """Add blank line to the output file"""
        self.lines.append('')

    def line(self, data: str, indent: int = 0):
        """
        Add line with content to the output data

        Args:
            data:   Line data
            indent: Number of tabs indentation
        """
        indent_str = self.get_indent(indent)
        self.lines.append('{}{}'.format(indent_str, data))

    def command(self, data: str, indent: int = 0):
        """
        Add command line to the output data (starting with the '\' character)

        Args:
             data:      Command data
             indent:    Number of tabs indentation
        """
        indent_str = self.get_indent(indent)
        self.lines.append('{}\\{}'.format(indent_str, data))

    def block_start(self, name: Optional[str] = None, indent: int = 0):
        """
        Add block start with optional block name to the output data

        Args:
            name:   Optional block name
            indent: Number of tabs indentation
        """
        if name is None:
            self.line('{', indent)
        else:
            self.command('{} {{'.format(name), indent)

    def block_end(self, indent: int = 0):
        """
        Add block end to the output data

        Args:
             indent:    Number of tabs indentation
        """
        self.line('}', indent)

    # endregion

    # region Other utils

    @staticmethod
    def get_indent(indent: int) -> str:
        """
        Get indentation in string format

        Args:
            indent:     Number of tabs indentation

        Returns:
            String with number of specified tabs
        """
        return '' if indent <= 0 else '\t' * indent

    @staticmethod
    def get_bar(bar_type: BarType) -> str:
        """
        Get string value for bar based on type

        Args:
             bar_type:  Bar type

        Returns:
            String representation of bar type
        """
        return '\\bar "{}"'.format(bar_type.value)

    # endregion

    # region Lilypond file parts

    def header(self, paper_size: str = 'a4', show_bar_numbers: bool = True):
        """
        Add typical lilypond header to the output data. You can specify paper size and disable bar numbers

        Args:
            paper_size:         Paper size
            show_bar_numbers:   Determine if bar numbers should be shown
        """
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
        """
        Add time signature to the output data

        Args:
            n:          Number of notes
            m:          Note rytmical value
            indent:     Number of tabs indentation
        """
        self.command('time {}/{}'.format(n, m), indent)

    def key_signature(self, key: str, key_type: KeyType, indent: int = 0):
        """
        Add key signature to the output data

        Args:
            key:        Key primary note
            key_type:   Key type (minor/major)
            indent:     Number of tabs indentation
        """
        self.command('key {} \\{}'.format(key, key_type.value), indent)

    # endregion

    # region File operations

    def set_source_dir(self, source_dir: str):
        """
        Set directory for generated lilypond sources

        Args:
            source_dir:     Directory path
        """
        self.source_dir = source_dir.rstrip('/')

    def set_compiled_dir(self, compiled_dir: str):
        """
        Set directory for compiled lilypond files

        Args:
            compiled_dir:   Directory path
        """
        self.compiled_dir = compiled_dir.rstrip('/')

    def export(self):
        """Export lilypond file"""
        if not os.path.isdir(self.source_dir):
            os.makedirs(self.source_dir, exist_ok=True)

        content: str = '\n'.join(self.lines)
        f = open('{}/{}.ly'.format(self.source_dir, self.filename), 'w+')
        f.write(content)
        f.close()

    def compile(self):
        """Compile lilypond file to pdf"""
        if not os.path.isdir(self.source_dir):
            raise NotADirectoryError

        if not os.path.exists('{}/{}.ly'.format(self.source_dir, self.filename)):
            raise FileNotFoundError

        if not os.path.isdir(self.compiled_dir):
            os.makedirs(self.compiled_dir, exist_ok=True)

        os.system('lilypond -o {} {}/{}.ly'.format(self.compiled_dir, self.source_dir, self.filename))

    # endregion

    def parse(self, bars: List[List[Writeable]]):
        """
        Parse list of bars and place it into the output data.

        Args:
            bars:   List of bars containing notes to parse into output data
        """
        for i, bar in enumerate(bars):
            notes = ' '.join([str(item) for item in bar])
            notes += ' |' if i != len(bars) - 1 else f' {self.get_bar(BarType.DOUBLE_NARROW_WIDE)}'
            self.line(notes, indent=1)
