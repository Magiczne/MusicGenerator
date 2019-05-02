from lib.Generator import Generator
from lib.Writer import Writer
from lib.Note import Note
from lib.OctaveType import OctaveType


def main():
    generator = Generator()
    writer = Writer('generated')

    generator.set_bar_count(10)\
        .set_shortest_note_duration(16)\
        .set_metre(4, 4)\
        .set_ambitus(lowest=Note('c', OctaveType.SMALL), highest=Note('c', OctaveType.LINE_2))\
        .set_start_note(Note('c', OctaveType.SMALL))\
        .set_end_note(Note('c', OctaveType.SMALL))\
        .set_intervals_probability([50, 0, 0, 50, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

    notes = generator.generate(group=True)

    writer.parse(notes)
    writer.export()
    writer.compile()


if __name__ == '__main__':
    main()