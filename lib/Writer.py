from typing import List, Optional
import os

from lib.theory import Note, OctaveType
from lib.BarType import BarType
from lib.KeyType import KeyType
from lib.theory.Writeable import Writeable


class Writer:
    def __init__(self, filename: str):
        self.filename: str = filename
        self.lines: List[str] = []

        self.source_dir = 'output/source'
        self.compiled_dir = 'output/compiled'

        # Zakresy dla kluczy.
        # Cały zakres nutowy [Note('c', OctaveType.DOUBLE_CONTRA), Note('b', OctaveType.LINE_6)] powinien być
        # Obsłużony
        self.clef_ranges = {
            'F': (Note('c', OctaveType.DOUBLE_CONTRA), Note('f', OctaveType.SMALL)),
            'G': (Note('fis', OctaveType.SMALL), Note('b', OctaveType.LINE_6))
        }

    # region Data appending utils

    def blank(self):
        """Dodaj pustą linię"""
        self.lines.append('')

    def line(self, data: str, indent: int = 0):
        """
        Dodaj linię z zawartością

        Args:
            data:   Zawartość linii
            indent: Rozmiar wcięcia
        """
        indent_str = self.get_indent(indent)
        self.lines.append('{}{}'.format(indent_str, data))

    def command(self, data: str, indent: int = 0):
        """
        Dodaj linię komendy (zaczynającą się znakiem '\')

        Args:
            data:   Zawartość komendy
            indent: Rozmiar wcięcia
        """
        indent_str = self.get_indent(indent)
        self.lines.append('{}\\{}'.format(indent_str, data))

    def block_start(self, name: Optional[str] = None, indent: int = 0):
        """
        Dodaj rozpoczęcie bloku

        Args:
            name:   Opcjonalna nazwa bloku
            indent: Rozmiar wcięcia
        """
        if name is None:
            self.line('{', indent)
        else:
            self.command('{} {{'.format(name), indent)

    def block_end(self, indent: int = 0):
        """
        Dodaj zakończenie bloku

        Args:
             indent: Rozmiar wcięcia
        """
        self.line('}', indent)

    # endregion

    # region Other utils

    @staticmethod
    def get_indent(indent: int) -> str:
        """
        Pobierz tekstową reprezentację wcięcia

        Args:
            indent: Rozmiar wcięcia
        """
        return '' if indent <= 0 else '\t' * indent

    @staticmethod
    def get_bar(bar_type: BarType) -> str:
        """
        Pobierz reprezentację tekstową wybranej kreski taktowej

        Args:
             bar_type:  Rodzaj kreski taktowej
        """
        return '\\bar "{}"'.format(bar_type.value)

    # endregion

    # region Lilypond file parts

    def header(self, paper_size: str = 'a4', show_bar_numbers: bool = True):
        """
        Wygeneruj typowy nagłówek pliku lilypond

        Args:
            paper_size:         Rozmiar papieru
            show_bar_numbers:   Jeśli True na wygenerowanych nutach będzie widoczna numeracja taktów
        """
        self.command('version "2.18.2"')
        self.blank()
        self.block_start('paper')
        self.line('#(set-paper-size "{}")'.format(paper_size), indent=1)
        self.block_end()
        self.blank()

        if not show_bar_numbers:
            self.block_start('layout')
            self.line('indent = 0\\in', indent=1)
            self.line('ragged-last = ##f', indent=1)
            self.command('context {', indent=1)
            self.command('Score', indent=2)
            self.command('remove "Bar_number_engraver"', indent=2)
            self.block_end(indent=1)
            self.block_end()
            self.blank()

    def time_signature(self, n: int, m: int, indent: int = 0):
        """
        Dodaj metrum

        Args:
            n:      Liczba nut
            m:      Wartość rytmiczna nut
            indent: Rozmiar wcięcia
        """
        self.command('time {}/{}'.format(n, m), indent)

    def key_signature(self, key: str, key_type: KeyType, indent: int = 0):
        """
        Dodaj oznaczenie tonacji

        Args:
            key:        Tonacja
            key_type:   Rodzaj tonacji (molowa / durowa)
            indent:     Rozmiar wcięcia
        """
        self.command('key {} \\{}'.format(key, key_type.value), indent)

    def clef(self, clef: str, indent: int = 0):
        """
        Dodaj klucz do danych wyjściowych

        Args:
            clef:   Rodzaj klucza
            indent:     Rozmiar wcięcia
        """
        self.command(f'clef {clef}', indent)

    # endregion

    # region File operations

    def set_source_dir(self, source_dir: str):
        """
        Ustaw folder na pliki źródłowe lilypond

        Args:
            source_dir:     Ścieżka do folderu
        """
        self.source_dir = source_dir.rstrip('/')

    def set_compiled_dir(self, compiled_dir: str):
        """
        Ustaw folder na pliki docelowe

        Args:
            compiled_dir:   Ścieżka do folderu
        """
        self.compiled_dir = compiled_dir.rstrip('/')

    def export(self):
        """Wyeksportuj dane do pliku lilypond"""
        if not os.path.isdir(self.source_dir):
            os.makedirs(self.source_dir, exist_ok=True)

        content: str = '\n'.join(self.lines)
        f = open('{}/{}.ly'.format(self.source_dir, self.filename), 'w+')
        f.write(content)
        f.close()

    def compile(self, ext: str = 'pdf'):
        """Kompiluj plik źródłowy do wybranego rodzaju pliku"""
        if ext not in ['pdf', 'png', 'ps']:
            raise AttributeError('Extension is not supported. Choose from pdf, png or ps')

        if not os.path.isdir(self.source_dir):
            raise NotADirectoryError

        if not os.path.exists('{}/{}.ly'.format(self.source_dir, self.filename)):
            raise FileNotFoundError

        if not os.path.isdir(self.compiled_dir):
            os.makedirs(self.compiled_dir, exist_ok=True)

        os.system(f'lilypond --format={ext} -o {self.compiled_dir} {self.source_dir}/{self.filename}.ly')

    # endregion

    def parse(self, bars: List[List[Writeable]], indent: int = 1):
        """
        Przetwórz takty i dodaj je do danych wyjściowych

        Args:
            bars:   Lista taktów
            indent:     Rozmiar wcięcia
        """
        for i, bar in enumerate(bars):
            elements = list(map(lambda elem: isinstance(elem, Note), bar))

            # Jeśli takt zawiera jakąś nutę, to sprawdzamy, czy ta nuta się mieści w przedziałach dla kluczy
            # i ustawiamy klucz na taki, który najbardziej pasuje
            try:
                first_note_idx = elements.index(True)
                first_note = bar[first_note_idx]

                assert isinstance(first_note, Note)

                for clef, clef_range in self.clef_ranges.items():
                    if first_note.between(clef_range[0], clef_range[1]):
                        self.clef(clef, indent=indent)
                        break
            except ValueError:
                pass

            notes = ' '.join([str(item) for item in bar])
            notes += ' |' if i != len(bars) - 1 else f' {self.get_bar(BarType.DOUBLE_NARROW_WIDE)}'
            self.line(notes, indent=indent)
