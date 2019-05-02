from typing import Dict, List, Optional, Tuple, Union
import copy

from lib.OctaveType import OctaveType
from lib.Note import Note
from lib.Rest import Rest
from lib.Writeable import Writeable
from lib.NoteModifier import NoteModifier


class Generator:
    available_note_lengths: List[int] = [2 ** i for i in range(7)]
    available_metre_rhythmic_values: List[int] = [8, 4, 2]

    def __init__(self):
        # Parametry rytmu
        self.metre: Tuple[int, int] = (4, 4)
        self.bar_count: int = 4
        self.shortest_note_duration: int = 4

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

        # Wygenerowane dane
        self.generated_data: List[Writeable] = []

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
        if duration in self.available_note_lengths:
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

    # region Utility methods

    def get_random_writeable(self, max_duration: int) -> Writeable:
        """
        Generate random writeable object (Note or Rest)

        Args:
            max_duration:   Maximal duration for the writeable object

        Returns:
             Writeable object
        """
        # TODO: Wygeneruj losowo nutę lub pauzę o określonej maksymalnej długości
        # TODO: Kurdebele to jest najcięższa funkcja XD
        # Trzeba pamiętać aby wykorzystać self.get_last_note_idx do tworzenia nuty po wylosowaniu interwału
        # (Od czegoś trzeba ten interwał stworzyć)

        # Tak na prawdę najpierw trzeba wybrać czy stworzymy nutę czy pauzę
        # Jeśli pauzę to nie ma problemu, tylko generujemy długośc (ewentualne kropki)
        # Jeśli nutę to losujemy interwał i na podstawie tego interwału generujemy następną nutę razem z długością,
        # gdyż wysokość i oktawa będzię określona przez wybrany interwał.
        # Należy też sprawdzać czy wylosowany interwał mieści się w ambitusie ustalonym przez użytkownika
        # Dodatkowo należy pamiętać że interwały mogą być w dwie strony (w dół i w górę) i też należy to wylosować

        # PRZEMYSLEC
        # 1. Jak zapobiec dużej ilości pauz następujących po sobie
        pass

    def get_random_note(self, note: Optional[str] = None, octave: Optional[OctaveType] = None) -> Note:
        """
        Generate random note, optionally overriding some parameters

        Args:
            note:       Note pitch to be overridden in final return object
            octave:     Note octave to be overridden in final return object

        Returns:
            Note object
        """
        # TODO: Wygeneruj losową nutę i zastąp odpowiednie wartości jeśli podano je w parametrach
        # Tak na prawdę sprowadza się to do wygenerowania losowej nuty z mieszczącej się w ambitusie
        pass

    def get_last_note_idx(self) -> int:
        """
        Get the index of a last note in the set of writeable objects

        Returns:
            Index if found
            -1 if not found
        """
        # TODO: Znajdź ostatni obiekty typu Note w liście i zwróć jego indeks lub -1 jeśli nie znaleziono
        # Lista danych to self.generated_data
        pass

    def get_length_to_fill(self) -> int:
        """
        Get how many of the shortest_note_duration we have to generate

        Returns:
            Number of shortest_note_duration notes that we have to fill
        """
        return self.bar_count * self.metre[0] * (self.shortest_note_duration // self.metre[1])

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
        notes_split: List[List[Writeable]] = [[] for _ in range(self.bar_count)]  # list of empty lists to fill
        value_to_fill = self.get_length_to_fill() / self.bar_count  # total value to fill in a bar
        bar_nr = 0  # number of currently filled bar
        for note in notes:
            if note.get_duration(self.shortest_note_duration) <= value_to_fill:  # how much of a bar will the note take
                notes_split[bar_nr].append(note)
                value_to_fill -= note.get_duration(self.shortest_note_duration)
            else:
                note_2 = copy.deepcopy(note)
                note.base_duration = value_to_fill
                if isinstance(note, Note):
                    note.add_modifier(NoteModifier.TIE)
                    notes_split[bar_nr].append(note)
                    note_2.base_duration -= value_to_fill
                elif isinstance(note, Rest):
                    notes_split[bar_nr].append(note)
                    note_2.base_duration -= value_to_fill
                else:
                    raise TypeError
                bar_nr += 1
                notes_split[bar_nr].append(note_2)
                value_to_fill = self.get_length_to_fill() / self.bar_count

        # TODO: Implementacja pogrupowania nut w takty, złamanie odpowiednich nut łukiem, etc...
        return notes_split

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

    def generate(self, group: bool = False) -> Union[List[Writeable], List[List[Writeable]]]:
        """
        Generate list of notes based on previously set parameters

        Args:
            group:  If true returned notes will be split into bars and grouped according to the music rules

        Returns:
            List of generated notes
        """

        # Cleanup generated data
        self.generated_data = []

        # Number of the shortest notes to be filled
        length_to_fill = self.get_length_to_fill()

        # User have specified start note, so we start from it only randomizing duration
        start_note = self.get_random_note(self.start_note.note, self.start_note.octave)
        self.generated_data.append(start_note)
        length_to_fill -= start_note.get_duration(self.shortest_note_duration)

        # Generate all other objects
        while length_to_fill > 0:
            # Generate random writeable with specified maximum length
            writeable = self.get_random_writeable(length_to_fill)
            length_to_fill -= writeable.get_duration(self.shortest_note_duration)
            self.generated_data.append(writeable)

        # Find the last generated note and replace note and octave values
        last_note_idx = self.get_last_note_idx()
        if last_note_idx != -1:
            self.generated_data[last_note_idx].note = self.end_note.note
            self.generated_data[last_note_idx].octave = self.end_note.octave

        if group:
            bars = self.split_to_bars(self.generated_data)
            return self.group_bars(bars)
        else:
            return self.generated_data
