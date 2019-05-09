import os
import unittest
from typing import List

from lib.BarType import BarType
from lib.KeyType import KeyType
from lib.theory.Note import Note
from lib.theory.NoteModifier import NoteModifier
from lib.theory.Rest import Rest
from lib.theory.RestModifier import RestModifier
from lib.theory.Writeable import Writeable
from lib.Writer import Writer


class WriterTests(unittest.TestCase):
    def setUp(self):
        self.writer = Writer('test')

    # region Data appending utils

    def test_init(self):
        self.assertEqual('test', self.writer.filename)
        self.assertEqual(0, len(self.writer.lines))

    def test_line(self):
        self.writer.line('test')
        self.assertIn('test', self.writer.lines)

        self.writer.line('test', indent=1)
        self.assertIn('\ttest', self.writer.lines)
        self.assertEqual('\ttest', self.writer.lines[1])

    def test_command(self):
        self.writer.command('test')
        self.assertIn('\\test', self.writer.lines)

        self.writer.command('test', indent=1)
        self.assertIn('\t\\test', self.writer.lines)

    def test_block_start(self):
        self.writer.block_start()
        self.assertIn('{', self.writer.lines)

        self.writer.block_start('test')
        self.assertIn('\\test {', self.writer.lines)

    def test_block_end(self):
        self.writer.block_end()
        self.assertIn('}', self.writer.lines)

    # endregion

    # region Other utils

    def test_get_indent(self):
        for i in range(5):
            expected = '\t' * i
            actual = self.writer.get_indent(i)
            self.assertEqual(expected, actual)

    def test_get_bar(self):
        bar = BarType.DOUBLE_WIDE
        self.assertEqual('\\bar ".."', self.writer.get_bar(bar))

    # endregion

    # region Lilypond file parts

    def test_header(self):
        self.writer.header('a5')
        self.assertIn('\t#(set-paper-size "a5")', self.writer.lines)
        self.assertNotIn('\t\t\\Score', self.writer.lines)

    def test_header_without_bar_numbers(self):
        self.writer.header(show_bar_numbers=False)
        self.assertIn('\t#(set-paper-size "a4")', self.writer.lines)
        self.assertIn('\t\t\\remove "Bar_number_engraver"', self.writer.lines)

    def test_time_signature(self):
        self.writer.time_signature(3, 4)
        self.assertIn('\\time 3/4', self.writer.lines)

    def test_key_signature(self):
        self.writer.key_signature('c', KeyType.MAJOR)
        self.assertIn('\\key c \\major', self.writer.lines)

    # endregion

    # region File operations

    def test_set_source_dir(self):
        self.writer.set_source_dir('test/source')
        self.assertEqual('test/source', self.writer.source_dir)

    def test_set_source_dir_with_trailing_slash(self):
        self.writer.set_source_dir('test/source/')
        self.assertEqual('test/source', self.writer.source_dir)

    def test_set_compiled_dir(self):
        self.writer.set_compiled_dir('test/compiled')
        self.assertEqual('test/compiled', self.writer.compiled_dir)

    def test_set_compiled_dir_with_trailing_slash(self):
        self.writer.set_compiled_dir('test/compiled/')
        self.assertEqual('test/compiled', self.writer.compiled_dir)

    def test_export(self):
        self.writer.header()
        self.writer.block_start()
        self.writer.key_signature('c', KeyType.MAJOR, indent=1)
        self.writer.line("c' d' e' f' | g' a' b' r", indent=1)
        self.writer.block_end()

        self.writer.export()
        self.assertTrue(os.path.exists('{}/{}.ly'.format(self.writer.source_dir, self.writer.filename)))

        output_file = open('{}/{}.ly'.format(self.writer.source_dir, self.writer.filename))
        expected_file = open('expected/test_1.ly')

        self.assertEqual(expected_file.readlines(), output_file.readlines())

        output_file.close()
        expected_file.close()

        # Cleanup after test
        os.remove('{}/{}.ly'.format(self.writer.source_dir, self.writer.filename))
        os.removedirs(self.writer.source_dir)

    def test_compile(self):
        self.writer.header()
        self.writer.block_start()
        self.writer.key_signature('c', KeyType.MAJOR, indent=1)
        self.writer.line("c' d' e' f' | g' a' b' r", indent=1)
        self.writer.block_end()

        self.writer.export()
        self.writer.compile()

        self.assertTrue(os.path.exists('{}/{}.pdf'.format(self.writer.compiled_dir, self.writer.filename)))

        # Cleanup
        os.remove('{}/{}.ly'.format(self.writer.source_dir, self.writer.filename))
        os.remove('{}/{}.pdf'.format(self.writer.compiled_dir, self.writer.filename))
        os.removedirs(self.writer.source_dir)
        os.removedirs(self.writer.compiled_dir)

    def test_compile_without_source(self):
        self.writer.header()

        with self.assertRaises(NotADirectoryError):
            self.writer.compile()

        self.writer.export()
        os.remove('{}/{}.ly'.format(self.writer.source_dir, self.writer.filename))

        with self.assertRaises(FileNotFoundError):
            self.writer.compile()

        os.removedirs(self.writer.source_dir)

    def test_compile_invalid_extension(self):
        self.writer.header()
        self.writer.export()

        with self.assertRaises(AttributeError):
            self.writer.compile('jpg')

        # Cleanup
        os.remove('{}/{}.ly'.format(self.writer.source_dir, self.writer.filename))
        os.removedirs(self.writer.source_dir)

    # endregion

    def test_parse(self):
        bars: List[List[Writeable]] = [
            [Note('c'), Note('d'), Note('e'), Note('f')],
            [Note('c', base_duration=2), Note('d', base_duration=4, modifiers=[NoteModifier.DOT]),
             Note('e', base_duration=8)],

            [Rest(), Rest(2), Rest(8, [RestModifier.DOT]), Rest(16)],
            [Rest(), Note('c'), Rest(), Note('c')],

            [Note('c', base_duration=2), Note('d', base_duration=2, modifiers=[NoteModifier.TIE])],
            [Note('d', base_duration=2), Rest(), Note('c', base_duration=8), Rest(8)]
        ]

        self.writer.header()
        self.writer.block_start()
        self.writer.parse(bars)
        self.writer.block_end()

        self.writer.export()

        output_file = open(f'{self.writer.source_dir}/{self.writer.filename}.ly')
        expected_file = open('expected/test_parse.ly')

        self.assertEqual(expected_file.readlines(), output_file.readlines())

        output_file.close()
        expected_file.close()

        # Cleanup
        os.remove('{}/{}.ly'.format(self.writer.source_dir, self.writer.filename))
        os.removedirs(self.writer.source_dir)


if __name__ == '__main__':
    unittest.main()
