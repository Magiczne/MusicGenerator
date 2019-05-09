from __future__ import annotations
from typing import List, Optional
import copy
import random

import lib
from lib.theory.Interval import Interval
from lib.theory.NoteModifier import NoteModifier
from lib.theory.OctaveType import OctaveType
from lib.theory.Writeable import Writeable
from lib.errors import InvalidBaseNoteDuration
from lib.errors import BaseDurationTooLarge


class Note(Writeable):
    base_notes = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
    base_notes_indexes = {x: i for i, x in enumerate(base_notes)}
    base_notes_ids = {'c': 0, 'd': 2, 'e': 4, 'f': 5, 'g': 7, 'a': 9, 'b': 11}

    def __init__(self, note: str, octave: OctaveType = OctaveType.SMALL, base_duration: int = 4,
                 modifiers: Optional[List[NoteModifier]] = None):
        super().__init__(base_duration)

        if note[0] not in self.base_notes:
            raise ValueError

        self.note = note
        self.octave: OctaveType = octave
        self.modifiers: List[NoteModifier] = []

        if modifiers is not None:
            for mod in modifiers:
                self.add_modifier(mod)

    def __str__(self):
        mods = ''.join([mod.value for mod in self.modifiers])
        return f'{self.note}{self.octave.value}{self.base_duration}{mods}'

    def __repr__(self):
        return f'Note <{self.__str__()}>'

    # region Base note & Accidentals

    def get_base_note(self) -> str:
        """Pobierz bazową nutę bez znaków diakrytycznych"""
        return self.note[0]

    def get_base_note_id(self) -> int:
        """Pobierz identyfikator dla nuty bazowej"""
        return self.base_notes_ids[self.get_base_note()]

    def get_id(self) -> int:
        """
        Pobierz identyfikator dla nuty.
        Numer ten jest zgodny z numeracją MIDI. Używany jest przy generowaniu interwałów
        """
        return self.get_base_note_id() + OctaveType.get_id(self.octave) * 12 + self.get_accidentals_value()

    def get_accidentals(self) -> str:
        """Pobierz znaki diaktrytyczne"""
        return self.note[1:]

    def get_accidentals_value(self) -> int:
        """Pobierz wartość znaków diakrytycznych. Używane przy generowaniu interwałów"""
        accidentals = self.get_accidentals()
        return accidentals.count('is') - accidentals.count('es')

    # endregion

    # region Utility

    @staticmethod
    def create_accidentals_string(value: int) -> str:
        """
        Stwórz ciąg znaków diakrytycznych na podstawie ilości półtonów podanej w parametrze.

        Args:
            value:  Ilość półtonów. Jeśli liczba jest ujemna generowany jest ciąg bemoli. Jeśli liczba jest dodatnia
                    generowany jest ciąg krzyżyków.
        """
        if value < 0:
            return 'es' * (-value)
        else:
            return 'is' * value

    @staticmethod
    def random(longest_duration: Optional[int] = None) -> Note:
        """
        Wygeneruj nutę z losowymi parametrami o pewnej maksymalnej długości podanej w parametrze.

        Args:
            longest_duration:   Najdłuższa możliwa wartośc rytmiczna, która może wystąpić podana w ilości
                                lib.Generator.shortest_note_duration.
                                Jeśli nie podano, skrypt zakłada że nuta o każdej długości jest dozwolona.

        Returns:
            Nuta z losowymi parametrami o maksymalnej długości wynoszącej longest_duration
        """
        # Jeśli nie był podany parametr najdłuższej możliwej wartości rytmicznej, to zakładamy że nuta o każdej długości
        # jest dozwolona do wygenerowania
        if longest_duration is None:
            longest_duration = lib.Generator.shortest_note_duration

        # Pobieramy listę dostępnych wartości rytmicznych i tworzymy listę dostępnych modyfikatorów
        available_notes = lib.Generator.get_available_note_lengths(longest_duration=longest_duration)
        available_mods = []

        base_note = random.choice(Note.base_notes)
        octave = OctaveType.random()
        base_duration = random.choice(available_notes)
        has_mod = random.choice([True, False])

        note = Note(note=base_note, octave=octave, base_duration=base_duration)

        # Jeśli długość nuty jest najkrótsza jaką możemy uzyskać, to nie możemy dodać modyfikatora wydłużającego,
        # gdyż kropka lub podwójna kropka doda mniejszą wartość rytmiczną
        if base_duration >= lib.Generator.shortest_note_duration:
            has_mod = False

        # Jeśli dostępne miejsce jest większej lub równej długości niż potencjalna nuta z kropką, to do dostępnych
        # modyfikatorów możemy dodać przedłużenie w postaci kropki
        if longest_duration >= note.get_duration(lib.Generator.shortest_note_duration) * 1.5:
            available_mods.append(NoteModifier.DOT)

        # Jeśli dostępne miejsce jest większej lub równej długości niż potencjalna nuta z podwójną kropką, to do
        # dostępnych modyfikatorów możemy dodać przedłużenie w postaci podwójnej kropki.
        # Sprawdzamy również, czy nie jest to przedostatnia dostępna wartośc rytmiczna. Jeśli tak jest, to nie możemy
        # dodać podwójnej kropki, gdyż skutkowałoby to dodaniem nuty o połowę mniejszej wartości rytmicznej niż
        # dozwolona
        if longest_duration >= note.get_duration(lib.Generator.shortest_note_duration) * 1.75 \
                and note.base_duration > 2 * lib.Generator.shortest_note_duration:
            available_mods.append(NoteModifier.DOUBLE_DOT)

        if has_mod and len(available_mods) > 0:
            note.add_modifier(random.choice(available_mods))

        return note

    # endregion

    # region Operators

    def __add__(self, other):
        if isinstance(other, Interval):
            # Find new base note according to the current note
            new_base_note_idx = (self.base_notes_indexes[self.get_base_note()] + other.degrees - 1) % len(self.base_notes)
            new_base_note = self.base_notes[new_base_note_idx]
            new_base_note_id = self.base_notes_ids[new_base_note]

            new_id = self.get_id() + other.semitones

            new_octave_id = OctaveType.get_id(self.octave) + int(self.get_base_note() in self.base_notes[8 - other.degrees:])
            new_octave = OctaveType.from_id(new_octave_id)

            # Na podstawie naszego nowego ID wyliczamy pozycję naszej nuty w oktawie
            # new_id % 12 zwraca indeks od 0 do 11 co obrazuje która to nuta w oktawie
            # Następnie odejmujemy od tego nowe ID nuty bazowej
            id_difference = new_id % 12 - new_base_note_id

            # Wstępna redukcja ilości znaków chromatycznych do maksymalnie trzech
            if id_difference > 3:
                id_difference -= 12

            if id_difference < -3:
                id_difference += 12

            # Jeśli otrzymaliśmy nutę o więcej niż 3 bemolach, to musimy zredukować tą ilość do maksymalnie dwóch
            while id_difference <= -3:
                # Znajdujemy poprzednią nutę bazową
                previous_base_note_idx = new_base_note_idx - 1
                previous_base_note = self.base_notes[previous_base_note_idx]
                previous_base_note_id = self.base_notes_ids[previous_base_note]

                # Liczmy różnicę w półtonach między tymi nutami (jeśli indeks jest równy -1 to znaczy że przeszliśmy z
                # nuty c na nutę b i sposób obliczania różnicy w półtonach będzie inny
                if previous_base_note_idx == -1:
                    semitones_diff = 12 - previous_base_note_id
                else:
                    semitones_diff = new_base_note_id - previous_base_note_id

                # Ustawiamy na nowo parametry nuty.
                # Jeśli miałaby wystąpić kolejna iteracja pętli to zostaną użyte do zredukowania znaków chromatycznych
                # W przeciwnym wypadku zostaną użyte do stworzenia nowej nuty
                new_base_note_idx = previous_base_note_idx
                new_base_note = previous_base_note
                new_base_note_id = previous_base_note_id

                id_difference += semitones_diff

            # Jeśli otrzymaliśmy nutę o więcej niż 3 krzyżykach, to musimy zredukować tą ilość do maksymalnie dwóch
            while id_difference >= 3:
                # Znajdujemy następną nutę bazową
                next_base_note_idx = new_base_note_idx + 1
                if next_base_note_idx == len(self.base_notes):
                    next_base_note_idx = 0
                next_base_note = self.base_notes[next_base_note_idx]
                next_base_note_id = self.base_notes_ids[next_base_note]

                # Liczymy różnicę w półtonach między tymi nutami (jeśli indeks jest równy 0 to znaczy że przeszliśmy z
                # nuty b na nutę c i sposób obliczania różnicy w półtonach będzie inny
                if next_base_note_idx == 0:
                    semitones_diff = 12 - new_base_note_id
                else:
                    semitones_diff = next_base_note_id - new_base_note_id

                # Ustawiamy na nowo parametry nuty
                # Jeśli miałaby wystąpić kolejna iteracja pętli to zostaną użyte do zredukowania znaków chromatycznych
                # W przeciwnym wypadku zostaną użyte do stworzenia nowej nuty
                new_base_note_idx = next_base_note_idx
                new_base_note = next_base_note
                new_base_note_id = next_base_note_id

                id_difference -= semitones_diff

            return Note(f'{new_base_note}{self.create_accidentals_string(id_difference)}', new_octave)
        else:
            raise NotImplementedError('This operation is not implemented')

    def __sub__(self, other):
        if isinstance(other, Interval):
            octave_lower = copy.deepcopy(self)
            octave_lower.octave = OctaveType.get_octave_down(self.octave)

            return octave_lower + other.get_complement_interval()
        else:
            raise NotImplementedError('This operation is not implemented')

    def __eq__(self, other):
        return self.__class__ == other.__class__ and str(self) == str(other)

    def __lt__(self, other):
        if isinstance(other, Note):
            return self.get_id() < other.get_id()
        else:
            raise NotImplementedError('This operation is not implemented')

    def __le__(self, other):
        if isinstance(other, Note):
            return self.get_id() <= other.get_id()
        else:
            raise NotImplementedError('This operation is not implemented')

    def __gt__(self, other):
        if isinstance(other, Note):
            return self.get_id() > other.get_id()
        else:
            raise NotImplementedError('This operation is not implemented')

    def __ge__(self, other):
        if isinstance(other, Note):
            return self.get_id() >= other.get_id()
        else:
            raise NotImplementedError('This operation is not implemented')

    # endregion

    def get_duration(self, base_duration: int = 16) -> int:
        """
        Pobierz długośc nuty wyrażoną w ilości base_duration

        Args:
            base_duration:    Bazowa wartość rytmiczna, na podstawie której będą wykonywane obliczenia

        Raises:
            InvalidBaseNoteDuration:        Jeśli base_duration nie jest poprawną bazową wartością rytmiczną
            BaseDurationTooLarge:           Jeśli base_duration jest dłuższą wartością rytmiczną niż self.base_duration
        """
        if base_duration not in lib.Generator.correct_note_lengths:
            raise InvalidBaseNoteDuration(base_duration)

        if self.base_duration > base_duration:
            raise BaseDurationTooLarge(self.base_duration, base_duration)

        note_duration = base_duration / self.base_duration

        if NoteModifier.DOT in self.modifiers:
            note_duration = note_duration * 1.5
        elif NoteModifier.DOUBLE_DOT in self.modifiers:
            note_duration = note_duration * 1.75

        return int(note_duration)

    def add_modifier(self, modifier: NoteModifier):
        """
        Dodaj modyfikator do listy modyfikatorów, jeśli już takiego nie ma.
        Jeśli dodawana jest kropka lub podwójna kropka, to odpowiednio nadpisana zostaje podwójna kropka lub kropka

        Args:
            modifier:   Modyfikator do dodania
        """
        if modifier not in self.modifiers:
            self.modifiers.append(modifier)

        if modifier == NoteModifier.DOUBLE_DOT:
            if NoteModifier.DOT in self.modifiers:
                self.modifiers.remove(NoteModifier.DOT)

        if modifier == NoteModifier.DOT:
            if NoteModifier.DOUBLE_DOT in self.modifiers:
                self.modifiers.remove(NoteModifier.DOUBLE_DOT)

        # Musimy mieć pewnośc że modyfikator przedłużenia nuty jest ostatni, więc aby to zrobić najpierw go usuwamy
        # a następnie dodajemy ponownie
        if NoteModifier.TIE in self.modifiers:
            self.modifiers.remove(NoteModifier.TIE)
            self.modifiers.append(NoteModifier.TIE)

        return self

    def remove_modifier(self, modifier: NoteModifier):
        """
        Usuń modyfikator, jeśli znajduje się w liście modyfikatorów

        Args:
            modifier:   Modyfikator do usunięcia
        """
        self.modifiers.remove(modifier)
        return self

    def between(self, lower: Note, higher: Note) -> bool:
        """
        Sprawdź czy nuta mieści się pomiędzy dwoma innymi

        Args:
            lower:  Nuta początkowa zakresu
            higher: Nuta końcowa zakresu
        """
        # Jeśli nuta początkowa jest większa niż końcowa, to zmieniamy ich kolejność
        if lower > higher:
            lower, higher = higher, lower

        return lower <= self <= higher

