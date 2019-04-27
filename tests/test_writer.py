import lib
import os
import unittest


class WriterTests(unittest.TestCase):
    def setUp(self):
        self.writer = lib.Writer('test')

    # region Data appending utils

    def test_init(self):
        self.assertEqual(self.writer.filename, 'test')
        self.assertEqual(len(self.writer.lines), 0)

    def test_line(self):
        self.writer.line('test')
        self.assertIn('test', self.writer.lines)

        self.writer.line('test', indent=1)
        self.assertIn('\ttest', self.writer.lines)
        self.assertEqual(self.writer.lines[1], '\ttest')

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
        bar = lib.BarType.DOUBLE_WIDE
        self.assertEqual(self.writer.get_bar(bar), '\\bar ".."')

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
        self.writer.key_signature('c', lib.KeyType.MAJOR)
        self.assertIn('\\key c \\major', self.writer.lines)

    # endregion

    # region File operations

    def test_set_source_dir(self):
        self.writer.set_source_dir('test/source')
        self.assertEqual(self.writer.source_dir, 'test/source')

    def test_set_source_dir_with_trailing_slash(self):
        self.writer.set_source_dir('test/source/')
        self.assertEqual(self.writer.source_dir, 'test/source')

    def test_set_compiled_dir(self):
        self.writer.set_compiled_dir('test/compiled')
        self.assertEqual(self.writer.compiled_dir, 'test/compiled')

    def test_set_compiled_dir_with_trailing_slash(self):
        self.writer.set_compiled_dir('test/compiled/')
        self.assertEqual(self.writer.compiled_dir, 'test/compiled')

    def test_export(self):
        self.writer.header()
        self.writer.block_start()
        self.writer.key_signature('c', lib.KeyType.MAJOR, indent=1)
        self.writer.line("c' d' e' f' | g' a' b' r", indent=1)
        self.writer.block_end()

        self.writer.export()
        self.assertTrue(os.path.exists('{}/{}.ly'.format(self.writer.source_dir, self.writer.filename)))

        output_file = open('{}/{}.ly'.format(self.writer.source_dir, self.writer.filename))
        expected_file = open('expected/test_1.ly')

        self.assertEqual(output_file.readlines(), expected_file.readlines())

        output_file.close()
        expected_file.close()

        # Cleanup after test
        os.remove('{}/{}.ly'.format(self.writer.source_dir, self.writer.filename))
        os.removedirs(self.writer.source_dir)

    def test_compile(self):
        self.writer.header()
        self.writer.block_start()
        self.writer.key_signature('c', lib.KeyType.MAJOR, indent=1)
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

    # endregion

    def test_parse(self):
        # TODO
        pass
