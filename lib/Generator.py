from typing import Dict, List, Optional, Tuple, Union
import copy
import termcolor
import math
import itertools
import numpy as np

from lib.theory.Interval import Interval
from lib.theory.OctaveType import OctaveType
from lib.theory.Note import Note
from lib.theory.Rest import Rest
from lib.theory.Writeable import Writeable
from lib.theory.NoteModifier import NoteModifier
from lib.theory.RestModifier import RestModifier
from lib.errors import InvalidBaseNoteDuration, NoNotesError, InvalidMetre, IntervalNotSupported, NoteOutsideAmbitus


class Generator:
    # Dozwolone wartości dla niektórych parametrów
    correct_note_lengths: List[int] = [2 ** i for i in range(7)]
    correct_metre_rhythmic_values: List[int] = [8, 4, 2]

    shortest_note_duration: int = 16

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

        # Prawdopodobieństwa wystąpień
        #   Interwałów
        #   Nut w obrębie oktawy
        #   Długości nut
        self.intervals_probability: List[int] = [8, 8, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7]
        self.notes_probability: List[int] = [9, 9, 9, 9, 8, 8, 8, 8, 8, 8, 8, 8]
        self.durations_probability: List[int] = [14, 14, 14, 14, 14, 15, 15]

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
            longest_duration:   Najdłuższa możliwa wartość rytmiczna, która może wystąpić podana w ilości
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

    def set_start_note(self, note: Note):
        """
        Ustaw nutę początkową dla generowanej melodii

        Args:
            note:   Nuta początkowa
        """
        if not note.between(self.ambitus['lowest'], self.ambitus['highest']):
            raise NoteOutsideAmbitus(note, self.ambitus['lowest'], self.ambitus['highest'])

        self.start_note = note
        return self

    def set_end_note(self, note: Note):
        """
        Ustaw nutę końcową dla generowanej melodii

        Args:
            note:   Nuta końcowa
        """
        if not note.between(self.ambitus['lowest'], self.ambitus['highest']):
            raise NoteOutsideAmbitus(note, self.ambitus['lowest'], self.ambitus['highest'])

        self.end_note = note
        return self

    def set_ambitus(self, lowest: Optional[Note] = None, highest: Optional[Note] = None):
        """
        Ustaw ambitus generowanej melodii

        Args:
             lowest:    Najniższa możliwa do wystąpienia
             highest:   Najwyższa nuta możliwa do wystąpienia
        """
        if lowest is not None:
            if lowest > self.ambitus['highest']:
                raise ValueError(f'Note is higher than current highest note')

            self.ambitus['lowest'] = lowest

        if highest is not None:
            if highest < self.ambitus['lowest']:
                raise ValueError('Note is lower than current lowest note')

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
            ValueError:     Jeśli prawdopodobieństwa nie sumują się do 100, lub jeśli długość listy nie odpowiada
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
            ValueError:     Jeśli prawdopodobieństwa nie sumują się do 100, lub jeśli długość listy nie odpowiada
                            ilości dźwięków dostępnych w ramach oktawy
        """
        if len(probabilities) != 12:
            raise ValueError('You have not specified probabilities for all notes')

        if sum(probabilities) != 100:
            raise ValueError('Probabilities does not sum to 100')

        self.notes_probability = probabilities

        return self

    def set_durations_probability(self, probabilities: List[int]):
        """
        Ustaw wartości prawdopodobieństwa wystąpienia dla wszystkich wartości rytmicznych. Muszą się sumować do 100

        Args:
            probabilities:  Lista prawdopodobieństw

        Raises:
            ValueError:     Jeśli prawdopodobieństwa nie sumują się do 100, lub jeśli długość listy nie odpowiada
                            ilości wszystkich dostępnych wartości rytmicznych
        """
        if len(probabilities) != len(Generator.correct_note_lengths):
            raise ValueError('You have not specified probabilities for all durations')

        if sum(probabilities) != 100:
            raise ValueError('Probabilities does not sum to 100')

        self.durations_probability = probabilities

        return self

    # endregion

    # region Random generation

    def get_random_duration(self, longest_duration: Optional[int] = None, uniform_distribution: bool = False):
        """
        Zwraca losową długość nuty na podstawie określonych prawdopodobieństw

        Args:
            longest_duration:       Najdłuższa możliwa wartość rytmiczna, która może wystąpić podana w ilości
                                    shortest_note_duration.
                                    Jeśli nie podano, skrypt zakłada że nuta o każdej długości jest dozwolona.
            uniform_distribution:   Jeśli prawda, każda długość ma identyczne prawdopodobieństwo wylosowania.
                                    W przeciwnym wypadku pod uwagę brane jest pole prawdopodobieństwa
        """
        available = Generator.get_available_note_lengths(longest_duration=longest_duration)

        if uniform_distribution:
            return np.random.choice(available)
        else:
            start_idx = Generator.correct_note_lengths.index(available[0])

            # Jako że wzięliśmy tylko fragment wystąpień, to musimy przeliczyć prawdopodobieństwa, tylko dla tych
            # kilku wartości rytmicznych
            p_available = self.durations_probability[start_idx:start_idx + len(available)]
            p_sum = sum(p_available)
            p = list(map(lambda dur: dur / p_sum, p_available))

            return np.random.choice(available, p=p)

    def get_random_note(self, longest_duration: Optional[int] = None) -> Note:
        """
        Wygeneruj nutę z losowymi parametrami o pewnej maksymalnej długości podanej w parametrze.

        Args:
            longest_duration:   Najdłuższa możliwa wartość rytmiczna, która może wystąpić podana w ilości
                                shortest_note_duration.
                                Jeśli nie podano, skrypt zakłada że nuta o każdej długości jest dozwolona.

        Returns:
            Nuta z losowymi parametrami o maksymalnej długości wynoszącej longest_duration
        """
        # Jeśli nie był podany parametr najdłuższej możliwej wartości rytmicznej, to zakładamy że nuta o każdej długości
        # jest dozwolona do wygenerowania
        if longest_duration is None:
            longest_duration = self.shortest_note_duration

        available_mods = []

        base_note = np.random.choice(Note.base_notes)
        octave = OctaveType.random()
        base_duration = self.get_random_duration(longest_duration=longest_duration)
        has_mod = np.random.choice([True, False])

        note = Note(note=base_note, octave=octave, base_duration=base_duration)

        # Jeśli długość nuty jest najkrótsza jaką możemy uzyskać, to nie możemy dodać modyfikatora wydłużającego,
        # gdyż kropka lub podwójna kropka doda mniejszą wartość rytmiczną
        if base_duration >= self.shortest_note_duration:
            has_mod = False

        # Jeśli dostępne miejsce jest większej lub równej długości niż potencjalna nuta z kropką, to do dostępnych
        # modyfikatorów możemy dodać przedłużenie w postaci kropki
        if longest_duration >= note.get_duration(self.shortest_note_duration) * 1.5:
            available_mods.append(NoteModifier.DOT)

        # Jeśli dostępne miejsce jest większej lub równej długości niż potencjalna nuta z podwójną kropką, to do
        # dostępnych modyfikatorów możemy dodać przedłużenie w postaci podwójnej kropki.
        # Sprawdzamy również, czy nie jest to przedostatnia dostępna wartość rytmiczna. Jeśli tak jest, to nie możemy
        # dodać podwójnej kropki, gdyż skutkowałoby to dodaniem nuty o połowę mniejszej wartości rytmicznej niż
        # dozwolona
        if longest_duration >= note.get_duration(self.shortest_note_duration) * 1.75 \
                and note.base_duration > 2 * self.shortest_note_duration:
            available_mods.append(NoteModifier.DOUBLE_DOT)

        if has_mod and len(available_mods) > 0:
            note.add_modifier(np.random.choice(available_mods))

        return note

    def get_random_rest(self, longest_duration: Optional[int] = None) -> Rest:
        """
        Wygeneruj pauzę z losowymi parametrami o maksymalnej długości podanej w parametrze

        Args:
            longest_duration:   Najdłuższa możliwa wartość rytmiczna, która może wystąpić podana w ilości
                                shortest_note_duration.
                                Jeśli nie podano, skrypt zakłada że nuta o każdej długości jest dozwolona.

        Returns:
            Pauza z losowymi parametrami o maksymalnej długości wynoszącej longest_duration
        """
        # Jeśli nie był podany parametr najdłuższej możliwej wartości rytmicznej, to zakładamy że nuta o każdej długości
        # jest dozwolona do wygenerowania
        if longest_duration is None:
            longest_duration = self.shortest_note_duration

        # Pobieramy listę dostępnych wartości rytmicznych i tworzymy listę dostępnych modyfikatorów
        available_mods = []

        base_duration = self.get_random_duration(longest_duration=longest_duration)
        has_mod = np.random.choice([True, False])

        rest = Rest(base_duration=base_duration)

        # Jeśli długość nuty jest najkrótsza jaką możemy uzyskać, to nie możemy dodać modyfikatora wydłużającego,
        # gdyż kropka lub podwójna kropka doda mniejszą wartość rytmiczną
        if base_duration >= self.shortest_note_duration:
            has_mod = False

        # Jeśli dostępne miejsce jest większej lub równej długości niż potencjalna pauza z kropką, to do dostępnych
        # modyfikatorów możemy dodać przedłużenie w postaci kropki
        if longest_duration >= rest.get_duration(self.shortest_note_duration) * 1.5:
            available_mods.append(RestModifier.DOT)

        # Jeśli dostępne miejsce jest większej lub równej długości niż potencjalna pauza z podwójną kropką, to do
        # dostępnych modyfikatorów możemy dodać przedłużenie w postaci podwójnej kropki.
        # Sprawdzamy również, czy nie jest to przedostatnia dostępna wartość rytmiczna. Jeśli tak jest, to nie możemy
        # dodać podwójnej kropki, gdyż skutkowałoby to dodaniem pauzy o połowę mniejszej wartości rytmicznej niż
        # dozwolona
        if longest_duration >= rest.get_duration(self.shortest_note_duration) * 1.75 \
                and rest.base_duration > 2 * self.shortest_note_duration:
            available_mods.append(RestModifier.DOUBLE_DOT)

        if has_mod and len(available_mods) > 0:
            rest.add_modifier(np.random.choice(available_mods))

        return rest

    # endregion

    # region Utility methods

    def get_next_writeable(self, longest_duration: int) -> Writeable:
        """
        Wygeneruj losowy element (nutę lub pauzę) ograniczony poprzez maksymalną wartość rytmiczną,
        która może wystąpić.
        UWAGA: Ta metoda będzie działać poprawnie tylko wtedy jeśli w kontenerze self.generated_data
        znajduje się co najmniej jedna nuta!

        Args:
            longest_duration:       Najkrótsza możliwa do wystąpienia wartość rytmiczna, podana w ilości
                                    shortest_note_duration

        Raises:
            TypeError:      Gdy ostatnim elementem nie jest nuta
        """
        generate_rest = np.random.choice([True, False], p=[self.rest_probability, 1 - self.rest_probability])

        if generate_rest and self._consecutive_rests < self.max_consecutive_rests:
            self._consecutive_rests += 1
            return self.get_random_rest(longest_duration=longest_duration)
        else:
            self._consecutive_rests = 0

            last_note_idx = self.get_last_note_idx()
            last_note = self.generated_data[last_note_idx]

            assert isinstance(last_note, Note)

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
                    # prawdopodobieństw wystąpienia dźwięków w ramach oktawy
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

            note_template = self.get_random_note(longest_duration=longest_duration)
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

    # region Grouping

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
            if isinstance(elem, Note):
                elem.remove_modifier(NoteModifier.DOT)
                elem.remove_modifier(NoteModifier.DOUBLE_DOT)
            elif isinstance(elem, Rest):
                elem.remove_modifier(RestModifier.DOT)
                elem.remove_modifier(RestModifier.DOUBLE_DOT)

            elem.base_duration = int(base_duration)
            divided.append(elem)
            duration -= self.shortest_note_duration / base_duration
        else:
            while duration > 0:
                elem_2 = copy.deepcopy(elem)

                if isinstance(elem_2, Note):
                    elem_2.remove_modifier(NoteModifier.DOT)
                    elem_2.remove_modifier(NoteModifier.DOUBLE_DOT)
                elif isinstance(elem_2, Rest):
                    elem_2.remove_modifier(RestModifier.DOT)
                    elem_2.remove_modifier(RestModifier.DOUBLE_DOT)

                # ile podstawowych długości zmieści się w takcie
                closest_whole = max([val for val in Generator.correct_note_lengths if val <= duration])
                # przeliczenie jaka to nuta
                closest_whole_base = self.shortest_note_duration // closest_whole
                elem_2.base_duration = int(closest_whole_base)
                
                # zmieniamy wartość pozostałą do wypełnienia
                duration -= int(elem_2.get_duration(self.shortest_note_duration))
                # sprawdzamy czy jakiś element został już wpisany do taktu i czy należy dodać do niego kropkę
                # lub podwójną kropkę
                if duration >= elem_2.get_duration(self.shortest_note_duration) * 0.75:
                    modifier_duration = elem_2.get_duration(self.shortest_note_duration) * 0.75
                    duration -= int(modifier_duration)
                   
                    if isinstance(elem_2, Note):
                        elem_2.add_modifier(NoteModifier.DOUBLE_DOT)
                    
                    if isinstance(elem_2, Rest):
                        elem_2.add_modifier(RestModifier.DOUBLE_DOT)
                    
                elif duration >= elem_2.get_duration(self.shortest_note_duration) * 0.5:
                    modifier_duration = elem_2.get_duration(self.shortest_note_duration) * 0.5
                    duration -= int(modifier_duration)

                    if isinstance(elem_2, Note):
                        elem_2.add_modifier(NoteModifier.DOT)
                    
                    if isinstance(elem_2, Rest):
                        elem_2.add_modifier(RestModifier.DOT)    
                    
                
                divided.append(elem_2)    

        return divided

    def split_note(self, elem: Writeable, first_duration: int) -> Tuple[List[Writeable], List[Writeable]]:
        """
        Podział obiektu (nuty lub pauzy) na granicy kreski taktowej.

        Args:
            elem: Element do podziału
            first_duration: Długość miejsca pozostałego w pierwszym takcie, wyrażona za pomocą ilości nut o
                            najmniejszej dozwolonej wartości (shortest_note_duration)

        Returns:
            Krotka dwuelementowa. Pierwszym elementem jest lista obiektów, która ma się pojawić w pierwszym takcie.
            Drugim elementem jest lista obiektów, która ma się pojawić w drugim takcie.
        """
        has_tie = isinstance(elem, Note) and NoteModifier.TIE in elem.modifiers

        second_duration = elem.get_duration(self.shortest_note_duration) - first_duration
        # kopiujemy parametry nuty aby móc później przypisać odpowiednią wartość do drugiego taktu
        elem_2 = copy.deepcopy(elem)
        first_bar: List[Writeable] = self.divide_element(elem, first_duration)
        second_bar: List[Writeable] = self.divide_element(elem_2, second_duration)

        # jeśli elementy są nutami łączymy je łukami
        if isinstance(elem, Note):
            for i in first_bar:
                assert isinstance(i, Note)
                i.add_modifier(NoteModifier.TIE)

            for i in second_bar:
                assert isinstance(i, Note)
                i.add_modifier(NoteModifier.TIE)

            # usuwamy łuk z ostatniej nuty, ale tylko jeśli go nie było    
            last_note = second_bar[-1]
            assert isinstance(last_note, Note)
            if NoteModifier.TIE in last_note.modifiers and not has_tie:
                last_note.remove_modifier(NoteModifier.TIE)

        return first_bar, second_bar

    def split_to_bars(self, notes: List[Writeable]) -> List[List[Writeable]]:
        """
        Dzieli listę elementów na takty. Elementy które nachodzą na dwa takty będą podzielone, a jeśli są nutami,
        to zostaną połączone łukiem

        Args:
            notes:  Lista nut
        """
        # Tworzymy listę pustych taktów do wypełnienia
        notes_split: List[List[Writeable]] = [[] for _ in range(self.bar_count)]

        # Obliczamy jaką długość ma każdy takt (w ilości shortest_note_duration)
        bar_length = self.get_length_to_fill() // self.bar_count
        value_to_fill = bar_length

        # Numer aktualnie przetwarzanego taktu
        bar_nr = 0

        for note in notes:
            # Obliczamy długość naszego elementu wyrażonego w ilości shortest_note_duration
            note_duration = note.get_duration(self.shortest_note_duration)

            # Jeśli w takcie skończyło się miejsce, to przeskakujemy do następnego
            if value_to_fill == 0:
                bar_nr += 1
                value_to_fill = bar_length

            # Przypadek 1 - element mieści się w takcie
            # Dodajemy go do naszego taktu, a następnie od pozostałej wartości odejmujemy jego długość
            if note_duration <= value_to_fill:
                notes_split[bar_nr].append(note)
                value_to_fill -= note_duration

            # Przypadek 2 - element nie mieści się w takcie
            # Przekazujemy go do metody split_note, wraz z pozostałym miejscem w pierwszym takcie, aby został
            # odpowiednio podzielony. Następnie pierwszą część dodajemy do pierwszego taktu, drugą do drugiego
            else:
                data: Tuple[List[Writeable], List[Writeable]] = self.split_note(note, value_to_fill)
                notes_split[bar_nr].extend(data[0])

                bar_nr += 1
                value_filled = sum([elem.get_duration(self.shortest_note_duration) for elem in data[1]])
                value_to_fill = bar_length - value_filled

                notes_split[bar_nr].extend(data[1])

        return notes_split

    def get_bar_parts(self) -> List[int]:
        """Wyznacz grupy główne w takcie"""
        parts: List[int] = []
        n = self.metre[0]

        if n % 3 == 0:
            parts = [3] * (n // 3)
        elif math.log2(n).is_integer():
            parts = [2] * int(math.log2(n))
        else:
            while n > 0:
                if n - 3 >= 2:
                    parts.append(3)
                    n -= 3
                else:
                    parts.append(2)
                    n -= 2

        return parts

    def group_bars(self, bars: List[List[Writeable]]) -> List[List[Writeable]]:
        """
        Pogrupuj nuty w taktach zgodnie z zasadami grupowania

        Args:
            bars:   Lista taktów do grupowania
        """
        bars_grouped: List[List[Writeable]] = []

        parts = self.get_bar_parts()
        part_durations = [part * (self.shortest_note_duration // self.metre[1]) for part in parts]

        for bar in bars:
            current_part = 0
            part_duration = part_durations[current_part]

            grouped_bar: List[List[Writeable]] = [[] for _ in range(len(parts))]
            
            for elem in bar:
                # Obliczamy długość naszego elementu wyrażonego w ilości shortest_note_duration
                note_duration = elem.get_duration(self.shortest_note_duration)

                # Jeśli w grupie skończyło się miejsce, to przeskakujemy do następnej
                if part_duration == 0:
                    current_part += 1
                    part_duration = part_durations[current_part]

                # Przypadek 1 - element mieści się w grupie
                # Dodajemy go do naszej grupy, a następnie od pozostałej wartości odejmujemy jego długość
                if note_duration <= part_duration:
                    grouped_bar[current_part].append(elem)
                    part_duration -= note_duration

                # Przypadek 2 - element nie mieści się w grupie
                # Przekazujemy go do metody split_note, wraz z pozostałym miejscem w pierwszej grupie, aby został
                # odpowiednio podzielony. Następnie pierwszą część dodajemy do pierwszej grupy, drugą do drugiej
                else:
                    data: Tuple[List[Writeable], List[Writeable]] = self.split_note(elem, part_duration)
                    grouped_bar[current_part].extend(data[0])

                    current_part += 1
                    value_filled = sum([i.get_duration(self.shortest_note_duration) for i in data[1]])
                    part_duration = part_durations[current_part] - value_filled

                    grouped_bar[current_part].extend(data[1])

            bars_grouped.append([y for x in grouped_bar for y in x])

        return bars_grouped    

    # endregion

    def generate(self, group: bool = False) -> Union[List[Writeable], List[List[Writeable]]]:
        """
        Wygeneruj listę nut bazując na ustalonych parametrach.

        Args:
            group:  Jeżeli True to zwrócona melodia będzie już pogrupowana zgodnie z zasadami muzyki i rozbita na takty
        """
        # Resetujemy wygenerowane dane
        self.generated_data = []

        # Długość którą mamy wygenerować podaną w ilości najkrótszej wartości rytmicznej, która może wystąpić
        length_to_fill = self.get_length_to_fill()

        # Generujemy pierwszą nutę a następnie podmieniamy jej wysokość na tą, którą wybrał użytkownik wybierając
        # nutę początkową
        start_note = self.get_random_note(self.shortest_note_duration)
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
