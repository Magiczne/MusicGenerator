from typing import Dict, List, Optional, Tuple, Union
import copy
import termcolor
import math
import random
import numpy as np

from lib.theory.Interval import Interval
from lib.theory.OctaveType import OctaveType
from lib.theory.Note import Note
from lib.theory.Rest import Rest
from lib.theory.Writeable import Writeable
from lib.theory.NoteModifier import NoteModifier
from lib.errors import InvalidBaseNoteDuration, NoNotesError, InvalidMetre, IntervalNotSupported


class Generator:
    shortest_note_duration: int = 16

    correct_note_lengths: List[int] = [2 ** i for i in range(7)]
    correct_metre_rhythmic_values: List[int] = [8, 4, 2]

    def __init__(self):
        # Parametry rytmu
        self.metre: Tuple[int, int] = (4, 4)
        self.bar_count: int = 4

        # Parametry melodii
        self.start_note: Note = Note('c', OctaveType.LINE_1)
        self.end_note: Note = Note('c', OctaveType.LINE_1)
        self.ambitus: Dict[str, Note] = {
            'lowest': Note('c', OctaveType.SMALL),
            'highest': Note('c', OctaveType.LINE_4)
        }
        self.rest_probability: float = 0.5
        self.max_consecutive_rests = math.inf

        # Parametry występowania interwałów i nut w obrębie oktawy
        self.intervals_probability: List[int] = [8, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]
        self.notes_probability: List[int] = [9, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8]

        # Wygenerowane dane
        self.generated_data: List[Writeable] = []

        # Zmienne pomocnicze
        self._consecutive_rests = 0

    # region Static

    @staticmethod
    def get_available_note_lengths(longest_duration: Optional[int] = None):
        """
        Zwraca listę dostępnych wartości rytmicznych na podstawie maksymalnej długości nuty podanej w ilości
        lib.Generator.shortest_note_duration

        Args:
            longest_duration:   Najdłuższa możliwa wartośc rytmiczna, która może wystąpić podana w ilości
                                lib.Generator.shortest_note_duration.
                                Jeśli nie podano, skrypt zakłada że nuta o każdej długości jest dozwolona.
        """
        if longest_duration is None:
            longest_duration = Generator.shortest_note_duration

        return [
            i for i in Generator.correct_note_lengths
            if Generator.shortest_note_duration / i <= longest_duration and i <= Generator.shortest_note_duration
        ]

    @staticmethod
    def set_shortest_note_duration(duration: int):
        """
        Ustaw najkrótszą dozwoloną wartość rytmiczną

        Args:
            duration:   Wartość rytmiczna
        """
        if duration not in Generator.correct_note_lengths:
            raise InvalidBaseNoteDuration(duration)

        Generator.shortest_note_duration = duration

    # endregion

    # region Setters

    def set_metre(self, n: int, m: int):
        """
        Ustaw metrum

        Args:
            n:  Liczba nut
            m:  Wartość rytmiczna nut
        """
        if m in self.correct_metre_rhythmic_values:
            self.metre = (n, m)
        else:
            raise InvalidMetre((n, m))

        return self

    def set_bar_count(self, bar_count: int):
        """
        Ustaw ilość taktów do wygenerowania

        Args:
            bar_count:  Ilość taktów
        """
        if bar_count >= 1:
            self.bar_count = bar_count
        else:
            raise ValueError('Bar count has to be larger than 0')

        return self

    # TODO: Check czy się mieści w ambitusie
    def set_start_note(self, note: Note):
        """
        Ustaw nutę początkową dla generowanej melodii

        Args:
            note:   Nuta początkowa
        """
        self.start_note = note
        return self

    def set_end_note(self, note: Note):
        """
        Ustaw nutę końcową dla generowanej melodii

        Args:
            note:   Nuta końcowa
        """
        self.end_note = note
        return self

    # TODO: Sprawdzić czy ambitus się nie odwrócił
    def set_ambitus(self, lowest: Optional[Note] = None, highest: Optional[Note] = None):
        """
        Ustaw ambitus generowanej melodii

        Args:
             lowest:    Najniższa możliwa do wystąpienia
             highest:   Najwyższa nuta możliwa do wystąpienia
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

    def set_max_consecutive_rests(self, count: Optional[int]):
        """
        Ustaw maksymalną liczbę pauz możliwych do wystąpienia po sobie

        Args:
            count:  Ilość pauz lub None jeśli pomijamy limit
        """
        if count is None:
            self.max_consecutive_rests = math.inf
        else:
            self.max_consecutive_rests = count

        return self

    def set_interval_probability(self, interval: str, probability: int):
        """
        Ustaw prawdopodobieństwo wystąpienia dla konkretnego interwału. Wartości prawdopodobieństw mają sumować się
        do 100, więc wartość tego prawdopodobieństwa też powinna być wybrana w taki sposób.

        Args:
            interval:       Nazwa interwału
            probability:    Prawdopodobieństwo wystąpienia
        """
        if interval in Interval.names():
            idx = Interval.names().index(interval)
            self.intervals_probability[idx] = probability
        else:
            raise IntervalNotSupported(interval)

        return self

    def set_intervals_probability(self, probabilities: List[int]):
        """
        Ustaw wartości prawdopodobieństwa wystąpienia dla wszystkich interwałów. Wartości muszą sumować się do 100.

        Args:
            probabilities:  Lista prawdopodobieństw

        Raises:
            ValueError:     Jeśli prawdopodobieństwa nie sumują się do 100, lub jeśli długośc listy nie odpowiada
                            ilości wszystkich dostępnych interwałów
        """
        if len(probabilities) != len(Interval.names()):
            raise ValueError('You have not specified probabilities for all intervals')

        if sum(probabilities) != 100:
            raise ValueError('Probabilities does not sum to 100')

        self.intervals_probability = probabilities

        return self

    def set_notes_probability(self, probabilities: List[int]):
        """
        Ustaw wartości prawdopodobieństwa wystąpienia dla nut w obrębie oktawy. Wartości muszą się sumować do 100

        Args:
             probabilities: Lista prawdopodobieństw

        Raises:
            ValueError:     Jeśli prawdopodobieństwa nie sumują się do 100, lub jeśli długośc listy nie odpowiada
                            ilości dźwieków dostępnych w ramach oktawy
        """
        if len(probabilities) != 12:
            raise ValueError('You have not specified probabilities for all notes')

        if sum(probabilities) != 100:
            raise ValueError('Probabilities does not sum to 100')

        self.notes_probability = probabilities

        return self

    # endregion

    # region Utility methods

    def get_next_writeable(self, longest_duration: int) -> Writeable:
        """
        Wygeneruj losowy element (nutę lub pauzę) ograniczony poprzez maksymalną wartość rytmiczną,
        która może wystąpić.
        UWAGA: Ta metoda będzie działać poprawnie tylko wtedy jeśli w kontenerze self.generated_data
        znajduje się conajmniej jedna nuta!

        Args:
            longest_duration:       Najkrótsza możliwa do wystąpienia wartość rytmiczna, podana w ilości
                                    shortest_note_duration

        Raises:
            TypeError:      Gdy ostatnim elementem nie jest nuta
        """
        generate_rest = np.random.choice([True, False], p=[self.rest_probability, 1 - self.rest_probability])

        if generate_rest and self._consecutive_rests < self.max_consecutive_rests:
            self._consecutive_rests += 1
            return Rest.random(longest_duration=longest_duration)
        else:
            self._consecutive_rests = 0

            last_note_idx = self.get_last_note_idx()
            last_note = self.generated_data[last_note_idx]

            if not isinstance(last_note, Note):
                raise TypeError

            # Losujemy do momentu, aż któraś z nut nie będzie się mieścić w naszym przedziale
            while True:
                # Wybieramy losowy interwał i tworzymy dwie nuty, jedną w górę drugą w dół o wylosowany interwał
                interval = np.random.choice(Interval.names(), p=self.get_normalized_intervals_probability())
                next_note_up = last_note + Interval(interval)
                next_note_down = last_note - Interval(interval)

                # Sprawdzamy czy nuty się mieszczą się w zadanym przez użytkownika
                up_in_ambitus = next_note_up.between(self.ambitus['lowest'], self.ambitus['highest'])
                down_in_ambitus = next_note_down.between(self.ambitus['lowest'], self.ambitus['highest'])

                if up_in_ambitus and down_in_ambitus:
                    # Jeśli obie z nut które zostały wygenerowane mieszczą się w ambitusie to korzystamy z
                    # prawdopodobieństw wystąpienia dźwieków w ramach oktawy
                    up_probability = self.notes_probability[next_note_up.get_id() % 12]
                    down_probability = self.notes_probability[next_note_down.get_id() % 12]

                    up_normalized_probability = up_probability / (up_probability + down_probability)
                    probabilities = [up_normalized_probability, 1 - up_normalized_probability]

                    elem = np.random.choice([next_note_up, next_note_down], p=probabilities)
                    break
                elif up_in_ambitus:
                    elem = next_note_up
                    break
                elif down_in_ambitus:
                    elem = next_note_down
                    break

            note_template = Note.random(longest_duration=longest_duration)
            note_template.note = elem.note
            note_template.octave = elem.octave

            return note_template

    def get_last_note_idx(self) -> int:
        """
        Pobierz indeks ostatniej nuty w liście wygenerowanych elementów

        Returns:
            Indeks jeśli znaleziono nutę

        Raises:
            NoNotesError:   When there are no notes in the generated data
        """
        for i, item in enumerate(reversed(self.generated_data)):
            if isinstance(item, Note):
                return len(self.generated_data) - i - 1

        raise NoNotesError

    def get_length_to_fill(self) -> int:
        """
        Pobierz ile nut o bazowej wartości rytmicznej równej self.shortest_note_duration zmieści musimy wygenerować
        """
        return self.bar_count * self.metre[0] * (self.shortest_note_duration // self.metre[1])

    def get_normalized_intervals_probability(self) -> List[float]:
        """
        Zwróć listę prawdopodobieństw znormalizowanych do jedynki

        Returns:
            Lista prawdopodobieństw znormalizowanych do jedynki
        """
        return [item / 100 for item in self.intervals_probability]

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
        print(duration, self.shortest_note_duration, base_duration)
        divided: List[Writeable] = []
        
        if base_duration.is_integer():
                print("elo")
                if NoteModifier.DOT in elem.modifiers:
                    elem.remove_modifier(NoteModifier.DOT)

                if NoteModifier.DOUBLE_DOT in elem.modifiers:
                    elem.remove_modifier(NoteModifier.DOUBLE_DOT)    
                elem.base_duration = int(base_duration)
                divided.append(elem)
                print(divided)
                duration -= self.shortest_note_duration / base_duration
                print(duration)
        else:
            while duration > 0:
                elem_2 = copy.deepcopy(elem)
                # ile podstawowych długości zmieści się w takcie
                closest_whole = max([val for val in Generator.correct_note_lengths if val <= duration])
                print(closest_whole)
                # przeliczenie jaka to nuta
                closest_whole_base = self.shortest_note_duration // closest_whole
                print(closest_whole_base)
                elem_2.base_duration = int(closest_whole_base)
                divided.append(elem_2)
                #zmieniamy wartość pozostałą do wypełnienia
                print(divided)
                duration -= int(elem_2.get_duration(self.shortest_note_duration))
                print(duration)
                # sprawdzamy czy jakiś element został już wpisany do taktu i czy należy dodać do niego kropkę
                # lub podwójną kropkę 
                if duration == divided[-1].get_duration(self.shortest_note_duration) * 0.5:
                    modifier_duration = divided[-1].get_duration(self.shortest_note_duration) * 0.5
                    divided[-1].add_modifier(NoteModifier.DOT)
                    duration -= int(modifier_duration)
                
                if duration >= divided[-1].get_duration(self.shortest_note_duration) * 0.75:
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
        notes_split: List[List[Writeable]] = [[] for _ in range(self.bar_count)] # list of empty lists to fill
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
                value_filled = 0
                for elem in data[1]:
                    value_filled += elem.get_duration(self.shortest_note_duration)
                value_to_fill = (self.get_length_to_fill() / self.bar_count) - value_filled 
                notes_split[bar_nr] = data[1] 

        return notes_split

    def group_bars(self, bars: List[List[Writeable]]) -> List[List[Writeable]]:
        """
        Pogrupuj nuty w taktach zgodnie z zasadami grupowania

        Args:
            bars:   Lista taktów do pogrupowania

        Returns:
            Pogrupowana lista taktów
        """
        # TODO: Implementacja grupowania nut wewnątrz taktów według zasad grupowania zależnie od metrum
        pass

    def generate(self, group: bool = False) -> Union[List[Writeable], List[List[Writeable]]]:
        """
        Wygeneruj listę nut bazując na ustalonych parametrach.

        Args:
            group:  Jeżeli True to zwrócona melodia będzie już pogrupowana zgodnie z zasadami muzyki i rozbita na takty
        """
        # Resetujemy wygenerowane dane
        self.generated_data = []

        # Długośc którą mamy wygenerować podaną w ilości najkrótszej wartości rytmicznej, która może wystąpić
        length_to_fill = self.get_length_to_fill()

        # Generujemy pierwszą nutę a następnie podmieniamy jej wysokość na tą, którą wybrał użytkownik wybierając
        # nutę początkową
        start_note = Note.random(self.shortest_note_duration)
        start_note.note = self.start_note.note
        start_note.octave = self.start_note.octave
        self.generated_data.append(start_note)
        length_to_fill -= start_note.get_duration(self.shortest_note_duration)

        # Generujemy elementy dopóki w takcie znajduje się miejsce
        while length_to_fill > 0:
            writeable = self.get_next_writeable(length_to_fill)
            length_to_fill -= writeable.get_duration(self.shortest_note_duration)
            self.generated_data.append(writeable)

        # Znajdujemy ostatnią nutę i podmieniamy jej wysokość, tak aby zgadzało się to z wyborem użytkownika
        try:
            last_note_idx = self.get_last_note_idx()
            self.generated_data[last_note_idx].note = self.end_note.note
            self.generated_data[last_note_idx].octave = self.end_note.octave
        except NoNotesError:
            print(termcolor.colored('The are no notes in the generated file! Something went wrong?', 'red'))

        if group:
            bars = self.split_to_bars(self.generated_data)
            return self.group_bars(bars)
        else:
            return self.generated_data
