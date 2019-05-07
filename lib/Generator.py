from typing import Dict, List, Optional, Tuple, Union
import copy
# import termcolor
import sys

from lib.theory.OctaveType import OctaveType
from lib.theory.Note import Note
from lib.theory.Rest import Rest
from lib.theory.Writeable import Writeable
from lib.theory.NoteModifier import NoteModifier
from lib.errors import InvalidNoteDuration, NoNotesError


class Generator:
    shortest_note_duration: int = 16

    correct_note_lengths: List[int] = [2 ** i for i in range(7)]
    correct_metre_rhythmic_values: List[int] = [8, 4, 2]

    def __init__(self):
        # Parametry rytmu
        self.metre: Tuple[int, int] = (4, 4)
        self.bar_count: int = 4

        # Parametry melodii
        self.start_note: Note = Note('c', OctaveType.SMALL)
        self.end_note: Note = Note('c', OctaveType.LINE_1)
        self.ambitus: Dict[str, Note] = {
            'lowest': Note('c', OctaveType.SMALL),
            'highest': Note('c', OctaveType.LINE_1)
        }
        self.rest_probability = 0.5

        # Parametry występowania interwałów
        self.intervals: List[str] = [
            '1cz', '2m', '2w', '3m', '3w', '4cz', '4zw', '5zmn', '5cz', '6m', '6w', '7m', '7w', '8cz'
        ]
        self.probability: List[int] = [8, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]

        # Wygenerowane dane
        self.generated_data: List[Writeable] = []

    # region Static

    @staticmethod
    def get_available_note_lengths(shortest_duration: Optional[int] = None):
        if shortest_duration is None:
            shortest_duration = Generator.shortest_note_duration

        if shortest_duration not in Generator.correct_note_lengths:
            raise InvalidNoteDuration(shortest_duration)

        return [i for i in Generator.correct_note_lengths if i <= shortest_duration]

    @staticmethod
    def set_shortest_note_duration(duration: int):
        """
        Set shortest note duration

        Args:
            duration:   Shortest note duration
        """
        if duration in Generator.correct_note_lengths:
            Generator.shortest_note_duration = duration
        else:
            raise InvalidNoteDuration(duration)

    # endregion

    # region Setters

    def set_metre(self, n: int, m: int):
        """
        Set metre

        Args:
            n:  Number of notes
            m:  Note rhythmic value
        """
        if m in self.correct_metre_rhythmic_values:
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

    def set_rest_probability(self, probability: float):
        """
        Ustaw prawdopodobieństwo wystąpienia pauzy. Musi się zawierać w przedziale [0, 1]

        Args:
            probability:    Prawdopodobieństwo wystąpienia pauzy

        Raises:
            ValueError:     Gdy prawdopodobieństwo nie zawiera się w przedziale [0, 1]
        """
        if probability < 0 or probability > 1:
            raise ValueError

        self.rest_probability = probability

        return self

    def set_interval_probability(self, interval: str, probability: int):
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

    def set_intervals_probability(self, probabilities: List[int]):
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

    def get_last_note_idx(self) -> int:
        """
        Get the index of a last note in the set of writeable objects

        Returns:
            Index if found
            -1 if not found

        Raises:
            NoNotesError:   When there are no notes in the generated data
        """
        for i, item in enumerate(reversed(self.generated_data)):
            if isinstance(item, Note):
                return len(self.generated_data) - i - 1

        raise NoNotesError

    def get_length_to_fill(self) -> int:
        """
        Get how many of the shortest_note_duration we have to generate

        Returns:
            Number of shortest_note_duration notes that we have to fill
        """
        return self.bar_count * self.metre[0] * (self.shortest_note_duration // self.metre[1])

    # endregion

    def divide_element(self, elem: Writeable, duration: int) -> List[Writeable]:
        """
        Podział elementu i dodanie do niego kropek, jeśli jest to konieczne

        Args:
            elem: Element do podziału
            duration: Długość miejsca w takcie, którą należy wypełnić 

        Returns:
            Lista nut mieszcząca się w takcie o podanej długości 
        """
        base_duration = self.shortest_note_duration / duration
        divided: List[Writeable] = []
        
        if base_duration.is_integer():
                elem.base_duration = int(base_duration)
                divided.append(elem)
                duration -= base_duration
        else:
            while duration > 0:
                elem_2 = copy.deepcopy(elem)
                # ile podstawowych długości zmieści się w takcie
                closest_whole = max([val for val in Generator.correct_note_lengths if val <= duration])
                # przeliczenie jaka to nuta
                closest_whole_base = self.shortest_note_duration // closest_whole
                elem_2.base_duration = int(closest_whole_base)
                divided.append(elem_2)
                #zmieniamy wartość pozostałą do wypełnienia
                duration -= int(elem_2.get_duration(self.shortest_note_duration))
                # sprawdzamy czy jakiś element został już wpisany do taktu i czy należy dodać do niego kropkę
                # lub podwójną kropkę 
                if duration == divided[-1].get_duration(self.shortest_note_duration) * 0.5:
                    modifier_duration = divided[-1].get_duration(self.shortest_note_duration) * 0.5
                    divided[-1].add_modifier(NoteModifier.DOT)
                    duration -= int(modifier_duration)
                
                if duration == divided[-1].get_duration(self.shortest_note_duration) * 0.75:
                    modifier_duration = divided[-1].get_duration(self.shortest_note_duration) * 0.75
                    divided[-1].add_modifier(NoteModifier.DOUBLE_DOT) 
                    duration -= int(modifier_duration)

        return divided             

    def split_note(self, elem: Writeable, first_duration: int) -> Tuple[List[Writeable], List[Writeable]]:
        """
        Podział obiektu (nuty lub pauzy) na granicy kreski taktowej. 

        Args:
            elem: Element do podziału
            first_duration: Długość miejsca pozostałego w pierwszym takcie, wyrażona za pomocą ilości nut o 
                            najmniejszej mdozwolonej wartości (shortest_note_duration)

        Returns:
            Krotka dwuelementowa. Pierwszym elementem jest lista obiektów, która ma się pojawić w pierwszym takcie. 
            Drugim elementem jest lista obiektów, która ma się pojawić w drugim takcie.   
        """
        second_duration = elem.get_duration(self.shortest_note_duration) - first_duration
        
        # kopiujemy parametry nuty aby móc później przypisać odpowiednią wartość do drugiego taktu
        elem_2 = copy.deepcopy(elem)
        first_bar: List[Writeable] = self.divide_element(elem, first_duration)
        second_bar: List[Writeable] = self.divide_element(elem_2, second_duration)

        # jeśli elementy są nutami łączymy je łukami
        for elem in first_bar:
            if isinstance(elem, Note):
                elem.add_modifier(NoteModifier.TIE)

        for elem in second_bar:
            if isinstance(elem, Note):
                elem.add_modifier(NoteModifier.TIE)        

        # usuwamy łuk z ostatniej nuty
        if NoteModifier.TIE in second_bar[-1].modifiers:
            second_bar[-1].remove_modifier(NoteModifier.TIE)                 
        return  (first_bar, second_bar)  


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
        base_duration = self.shortest_note_duration
        bar_nr = 0  # number of currently filled bar
        for note in notes:
            note_duration = note.get_duration(base_duration)
            if note_duration <= value_to_fill:  # how much of a bar will the note take
                notes_split[bar_nr].append(note)
                value_to_fill -= note_duration
            elif value_to_fill == 0:
                bar_nr += 1
                value_to_fill = (self.get_length_to_fill() / self.bar_count) - note_duration
                notes_split[bar_nr].append(note)
            else:
                data: Tuple[List[Writeable], List[Writeable]] = self.split_note(note, value_to_fill)

                notes_split[bar_nr].extend(data[0])
                bar_nr += 1
                print(bar_nr)
                print(data[1])
                notes_split[bar_nr] = data[1]

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
        start_note = Note.random(self.shortest_note_duration)
        start_note.note = self.start_note.note
        start_note.octave = self.start_note.octave
        self.generated_data.append(start_note)
        length_to_fill -= start_note.get_duration(self.shortest_note_duration)

        # Generate all other objects
        while length_to_fill > 0:
            # Generate random writeable with specified maximum length
            writeable = self.get_random_writeable(length_to_fill)
            length_to_fill -= writeable.get_duration(self.shortest_note_duration)
            self.generated_data.append(writeable)

        # Find the last generated note and replace note and octave values
        try:
            last_note_idx = self.get_last_note_idx()
            self.generated_data[last_note_idx].note = self.end_note.note
            self.generated_data[last_note_idx].octave = self.end_note.octave
        except NoNotesError:
            # print(termcolor.colored('The are no notes in the generated file! Something went wrong?', 'red'))
            pass

        if group:
            bars = self.split_to_bars(self.generated_data)
            return self.group_bars(bars)
        else:
            return self.generated_data
