from typing import Dict, List, Optional, Tuple

from .OctaveType import OctaveType
from .Note import Note
from .Writeable import Writeable


class Generator:
    def __init__(self):
        # Parametry rytmu
        self.metre: Tuple[int, int] = (4, 4)
        self.bar_count: int = 4
        self.shortest_note_duration: int = 1

        self.available_metre_rhythmic_values: List[int] = [8, 4, 2]
        self.available_lengths: List[int] = [16, 8, 4, 2, 1]

        # Parametry melodii
        self.start_note: Note = Note('c', OctaveType.SMALL)
        self.end_note: Note = Note('c', OctaveType.LINE_1)
        self.ambitus: Dict[str, Note] = {
            'lowest': Note('c', OctaveType.SMALL),
            'highest': Note('c', OctaveType.LINE_1)
        }

        # Parametry występowania interwałów
        self.intervals: List[str] = [
            '1cz', '2m', '2w', '3m', '3w', '4cz', '4zw', '5zmn', '5cz', '6m', '6w', '7m', '7w', '8cz'
        ]
        self.probability: List[float] = [8, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]

    # region Setters

    def set_metre(self, n: int, m: int):
        """
        Set metre

        Args:
            n:  Number of notes
            m:  Note rhythmic value
        """
        if m in self.available_metre_rhythmic_values:
            self.metre = (n, m)
        else:
            raise ValueError()

        return self

    def set_bar_count(self, bar_count: int):
        """
        Set bar count

        Args:
            bar_count:  Bar count
        """
        if bar_count >= 1:
            self.bar_count = bar_count
        else:
            raise ValueError()

        return self

    def set_shortest_note_duration(self, duration: int):
        """
        Set shortest note duration

        Args:
            duration:   Shortest note duration
        """
        if duration in self.available_lengths:
            self.shortest_note_duration = duration
        else:
            raise ValueError()

        return self

    def set_start_note(self, note: Note):
        """
        Set note on which script will start generating notes

        Args:
            note:   Starting note
        """
        self.start_note = note
        return self

    def set_end_note(self, note: Note):
        """
        Set note on which script will finish generating notes

        Args:
            note:   Finishing note
        """
        self.end_note = note
        return self

    def set_ambitus(self, lowest: Optional[Note] = None, highest: Optional[Note] = None):
        """
        Set ambitus

        Args:
             lowest:    Optional value for lowest note
             highest:   Optional value for highest note
        """
        if lowest is not None:
            self.ambitus['lowest'] = lowest

        if highest is not None:
            self.ambitus['highest'] = highest

        return self

    def set_interval_probability(self, interval: str, probability: float):
        """
        Set probability for specified interval

        Args:
            interval:       Interval name
            probability:    Probability for specified interval
        """
        if interval in self.intervals:
            idx = self.intervals.index(interval)
            self.probability[idx] = probability
        else:
            raise KeyError    

        return self

    def set_intervals_probability(self, probabilities: List[float]):
        """
        Set probabilities for all intervals at once

        Args:
            probabilities:  List of probabilities. All values should be summed to 100
        """
        if len(probabilities) == len(self.intervals):
            if sum(probabilities) == 100:
                self.probability = probabilities
            else:
                raise ValueError 
        else:
            raise ValueError

        return self

    # endregion

    def split_to_bars(self, notes: List[Writeable]) -> List[List[Writeable]]:
        """
        Split given list of notes into bars. Notes that overlap between bars will be split
        and then connected with a ligature.

        Args:
            notes:  List of notes

        Returns:
            List of bars of notes
        """
        # TODO: Implementacja pogrupowania nut w takty, złamanie odpowiednich nut łukiem, etc...
        pass

    def group_bars(self, bars: List[List[Writeable]]) -> List[List[Writeable]]:
        """
        Perform grouping on each bar of notes according to the musical grouping rules

        Args:
            bars:   List of bars of notes

        Returns:
            Grouped list of bars of notes
        """
        # TODO: Implementacja grupowania nut wewnątrz taktów według zasad grupowania zależnie od metrum
        pass

    def generate(self) -> List[Writeable]:
        """
        Generate list of notes based on previously set parameters.

        Returns:
            List of generated notes
        """
        # TODO: Generacja nut na podstawie parametrów podanych wsześniej przez użytkownika
        # TODO: Przekazanie wygenerowanej listy nut do funkcji dzieljącej na takty (split_to_bars)
        # TODO: Przekazanie pogrupowanej listy taktów do funkcji grupującej nuty wewnątrz taktów (group_in_bars)
        pass
