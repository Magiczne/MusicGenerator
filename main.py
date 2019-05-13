from lib.Generator import Generator
from lib.Writer import Writer
from lib.theory.Note import Note
from lib.theory.OctaveType import OctaveType


def main():
    generator = Generator()

    # set_metre przyjmuje każde metrum, którego wartością rytmiczną jest półnuta, ćwierćnuta, ósemka lub szesnastka
    # ilość nut w metrum jest dowolna jeśli tylko większa od 1

    # set_bar_count przyjmuje liczbę taktów, którą chcemy wygenerować

    # set_start_note oraz set_end_note ustalają nuty początkowe i końcowe i przyjmują tylko nuty które znajdują się w
    # ambitusie, który można ustawić za pomocą metody set_ambitus

    # set_rest_probability ustawia prawdopodobieństwa wystąpienia pauzy. Podawana wartość musi być znormalizowana do 1
    # prawdopodobieństwo wystąpienia nuty będzie wynosiło 1 - p, gdzie p to podana wartość

    # set_max_consecutive_rests ustala ile maksymalnie pauz może nastąpić po sobie (UWAGA! W nutach niepogrupowanych)
    # po dzieleniu na takty i grupowaniu, może pojawić się większa liczba pauz

    # set_intervals_probability, set_notes_probability, set_durations_probability to metody, które umożliwiają
    # ustawienie prawdopodobieństw wystąpienia odpowiednio:
    # 1. Konkretnych interwałów - lista interwałów to: [1cz, 2m, 2w, 3m, 3w, 4cz, 4zw, 5zm, 5cz, 6m, 6w, 7m, 7w, 8cz]
    # 2. Konkretnych nut w obrębie oktawy (12 dźwięków począwszy od c do b) - wykorzystywane w algorytmie generującym
    #    gdy nuty wygenerowane po wylosowaniu interwału obie mieszczą się w zadanym ambitusie. Wtedy wykorzystywane jest
    #    prawdopodobieństwo ich wystąpienia podczas losowania, która z nich trafi do końcowej melodii
    # 3. Konkretnych wartości rytmicznych - kolejno: [cała nuta, półnuta, ... aż do 64]
    # Prawdopodobieństwa podawane do tych funkcji muszą być znormalizowane do 100, a każda pojedyncza wartość musi być
    # liczbą całkowitą.

    # set_shortest_note_duration - ustala jaką najkrótszą wartość rytmiczną chcemy zobaczyć w nutach.
    # Skrypt obsługuje aktualnie aż do 64, ale wystarczy zmienić zakres w pliku Generator.py zmiennej
    # correct_note_lengths, aby skrypt pozwolił na wykorzystanie 128, lub innych nut, ponieważ obliczenia są pisane
    # uniwersalnie.

    generator\
        .set_metre(4, 4) \
        .set_bar_count(100) \
        .set_start_note(Note('c', OctaveType.SMALL)) \
        .set_end_note(Note('c', OctaveType.SMALL)) \
        .set_ambitus(lowest=Note('c', OctaveType.SMALL), highest=Note('c', OctaveType.LINE_2)) \
        .set_rest_probability(0.1) \
        .set_max_consecutive_rests(1) \
        .set_intervals_probability([8, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]) \
        .set_notes_probability([9, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8]) \
        .set_durations_probability([14, 14, 14, 14, 14, 15, 15]) \
        .set_shortest_note_duration(16)

    # w konstruktorze należy podać nazwę pliku, pod którą będą generowane pliki lilyponda oraz pliki wynikowe
    # można zmienić wiele innych parametrów, wtedy odsyłam do pliku Writer.py
    writer = Writer('generated')

    # from_generator - na podstawie obiektu generatora z określonymi parametrami przetwarza dane, które później mogą
    # zostać wyeksportowane do pliku lilyponda
    writer.from_generator(generator, midi=True)

    # export - eksportuje plik lilyponda
    writer.export()

    # compile - uruchamia lilyponda z odpowiednimi parametrami, tak aby powstał plik wynikowy, dozwolone rozszerzenia
    # to pdf, png oraz ps (tak jak zezwala lilypond)
    writer.compile(ext='png')


if __name__ == '__main__':
    main()
