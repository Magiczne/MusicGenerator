from .OctaveType import OctaveType
from .Note import Note


class Generator:
    def __init__(self):
        # Parametry rytmu
        self.metre = (4, 4)
        self.bar_count = 4
        self.shortest_note_duration = 16

        # Parametry melodii
        self.start_note = 'c'
        self.end_note = 'c'
        self.ambitus = {
            'lowest': Note('c', OctaveType.SMALL),
            'highest': Note('c', OctaveType.LINE_1)
        }

        # Parametry występowania interwałów
        # TODO: Czy chodziło o tylko te interwały, czy o taką rozszerzoną opcję: http://i.imgur.com/tEkJT3i.png
        self.intervals = ['1cz', '2m', '2w', '3m', '4cz', '4zw', '5cz', '6m', '6w', '7m', '7w', '8cz']
        self.probability = [1 / len(self.intervals) for _ in self.intervals]

    # region Setters

    def set_metre(self, n, m):
        self.metre = (n, m)
        return self

    def set_bar_count(self, bar_count):
        # TODO: Set bar count
        return self

    def set_shortest_note_duration(self, duration):
        # TODO: Set
        return self

    def set_start_note(self, note):
        # TODO: Set & Walidacja czy poprawna nuta
        return self

    def set_end_note(self, note):
        # TODO: Set & Walidacja czy poprawna nuta
        return self

    def set_ambitus(self, lowest, highest):
        # TODO: Sprawdzenie czy lowest, highest przy podaniu jest instancją Note
        # TODO: Ustawienie ambitusu, może opcjonalne parametry, aby ustawiać tylko dół albo tylko górę
        return self

    def set_interval_probability(self, interval, probability):
        # TODO: Ustawienie prawdopodobieństwa wystąpienia konkretnego interwału
        return self

    def set_intervals_probability(self, probabilities):
        # TODO: Walidacja czy podano odpowiednio długą listę i czy suma wartości równa się 1
        # TODO: Ustawienie wszystkich prawdopodobieństw na raz
        return self

    # endregion

    def generate(self):
        # TODO: Implementacja generacji na podstawie wszystkich parametrów
        pass
