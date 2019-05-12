from lib.Generator import Generator
from lib.Writer import Writer
from lib.theory.Note import Note
from lib.theory.OctaveType import OctaveType


def main():
    generator = Generator()
    writer = Writer('generated')

    generator.set_metre(4, 4) \
        .set_bar_count(100) \
        .set_start_note(Note('c', OctaveType.SMALL)) \
        .set_end_note(Note('c', OctaveType.SMALL)) \
        .set_ambitus(lowest=Note('c', OctaveType.SMALL), highest=Note('c', OctaveType.LINE_2)) \
        .set_rest_probability(0.1) \
        .set_max_consecutive_rests(1) \
        .set_intervals_probability([8, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]) \
        .set_notes_probability([9, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8]) \
        .set_durations_probability([14, 14, 14, 14, 14, 15, 15]) \
        .set_shortest_note_duration(32)

    writer.from_generator(generator, midi=True)
    writer.export()
    writer.compile(ext='pdf')


if __name__ == '__main__':
    main()
