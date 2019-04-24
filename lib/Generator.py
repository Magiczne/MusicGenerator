from typing import Dict, List, Optional, Tuple

from .OctaveType import OctaveType
from .Note import Note


class Generator:
    def __init__(self):
        # Parametry rytmu
        self.metre: Tuple[int, int] = (4, 4)
        self.bar_count: int = 4
        self.shortest_note_duration: int = 16

        # Parametry melodii
        self.start_note: Note = Note('c', OctaveType.SMALL)
        self.end_note: Note = Note('c', OctaveType.LINE_1)
        self.ambitus: Dict[str, Note] = {
            'lowest': Note('c', OctaveType.SMALL),
            'highest': Note('c', OctaveType.LINE_1)
        }

        # Parametry występowania interwałów
        # TODO: Czy chodziło o tylko te interwały, czy o taką rozszerzoną opcję: http://i.imgur.com/tEkJT3i.png
        self.intervals: List[str] = ['1cz', '2m', '2w', '3m', '4cz', '4zw', '5cz', '6m', '6w', '7m', '7w', '8cz']
        self.probability: List[float] = [1 / len(self.intervals) for _ in self.intervals]

    # region Setters

    def set_metre(self, n: int, m: int):
        """
        Set metre

        Args:
            n:  Number of notes
            m:  Note rytmical value
        """
        self.metre = (n, m)
        return self

    def set_bar_count(self, bar_count: int):
        """
        Set bar count

        Args:
            bar_count:  Bar count
        """
        # TODO: Set bar count
        return self

    def set_shortest_note_duration(self, duration: int):
        """
        Set shortest note duration

        Args:
            duration:   Shortest note duration
        """
        # TODO: Set
        return self

    def set_start_note(self, note: Note):
        """
        Set note on which script will start generating notes

        Args:
            note:   Starting note
        """
        # TODO: Set & Walidacja czy poprawna nuta
        return self

    def set_end_note(self, note: Note):
        """
        Set note on which script will finish generating notes

        Args:
            note:   Finishing note
        """
        # TODO: Set & Walidacja czy poprawna nuta
        return self

    def set_ambitus(self, lowest: Optional[Note] = None, highest: Optional[Note] = None):
        """
        Set ambitus

        Args:
             lowest:    Optional value for lowest note
             highest:   Optional value for highest note
        """
        # TODO: Sprawdzenie czy lowest, highest przy podaniu jest instancją Note
        # TODO: Ustawienie ambitusu, może opcjonalne parametry, aby ustawiać tylko dół albo tylko górę
        return self

    def set_interval_probability(self, interval: str, probability: float):
        """
        Set probability for specified interval

        Args:
            interval:       Interval name
            probability:    Probability for specified interval
        """
        # TODO: Ustawienie prawdopodobieństwa wystąpienia konkretnego interwału
        return self

    def set_intervals_probability(self, probabilities: List[float]):
        """
        Set probabilities for all intervals at once

        Args:
            probabilities:  List of probabilities. All values should be summed to 1
        """
        # TODO: Walidacja czy podano odpowiednio długą listę i czy suma wartości równa się 1
        # TODO: Ustawienie wszystkich prawdopodobieństw na raz
        return self

    # endregion

    def split_to_bars(self, notes: List[Note]) -> List[List[Note]]:
        """
        Split given list of notes into bars. Notes that overlap between bars will be split
        and then connected with a ligature.

        Args:
            notes:  List of notes

        Returns:
            List of bars of notes
        """
        # TODO: Sprawdzenie czy parametr notes jest listą nut
        # TODO: Implementacja pogrupowania nut w takty, złamanie odpowiednich nut łukiem, etc...
        pass

    def group_bars(self, bars: List[List[Note]]) -> List[List[Note]]:
        """
        Perform grouping on each bar of notes according to the musical grouping rules

        Args:
            bars:   List of bars of notes

        Returns:
            Grouped list of bars of notes
        """
        # TODO: Implementacja grupowania nut wewnątrz taktów według zasad grupowania zależnie od metrum
        pass

    def generate(self) -> List[Note]:
        """
        Generate list of notes based on previously set parameters.

        Returns:
            List of generated notes
        """
        # TODO: Generacja nut na podstawie parametrów podanych wsześniej przez użytkownika
        # TODO: Przekazanie wygenerowanej listy nut do funkcji dzieljącej na takty (split_to_bars)
        # TODO: Przekazanie pogrupowanej listy taktów do funkcji grupującej nuty wewnątrz taktów (group_in_bars)
        pass
