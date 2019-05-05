from __future__ import annotations
from typing import List, Optional
import copy
import random

import lib
from lib.theory.Interval import Interval
from lib.theory.NoteModifier import NoteModifier
from lib.theory.OctaveType import OctaveType
from lib.theory.Writeable import Writeable
from lib.errors import InvalidNoteDuration


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

    def __eq__(self, other):
        return self.__class__ == other.__class__ and str(self) == str(other)

    def __str__(self):
        mods = ''.join([mod.value for mod in self.modifiers])
        return f'{self.note}{self.octave.value}{self.base_duration}{mods}'

    def __repr__(self):
        return f'Note <{self.__str__()}>'

    # region Base note & Accidentals

    def get_base_note(self) -> str:
        return self.note[0]

    def get_base_note_id(self):
        return self.base_notes_ids[self.get_base_note()]

    def get_id(self):
        # This is actually a number that is compliant to MIDI number and is used in some calculations or the intervals
        return self.get_base_note_id() + OctaveType.get_id(self.octave) * 12 + self.get_accidentals_value()

    def get_accidentals(self) -> str:
        return self.note[1:]

    def get_accidentals_value(self) -> int:
        accidentals = self.get_accidentals()
        return accidentals.count('is') - accidentals.count('es')

    # endregion

    # region Utility

    @staticmethod
    def create_accidentals_string(value: int) -> str:
        if value < 0:
            return 'es' * (-value)
        else:
            return 'is' * value

    @staticmethod
    def random(shortest_duration: Optional[int] = None) -> Note:
        """
        Wygeneruj nutę z losowymi parametrami

        Args:
            shortest_duration:  Najkrótsza możliwa wartość rytmiczna która może wystąpić

        Returns:
            Nuta z losowymi parametrami
        """

        # Jeśli nie był podany parametr najkrótszej nuty, to zakładamy że najkrótszą możliwą wartością rytmiczną
        # jest ta, która jest najmniejsza możliwa do wystąpienia w generatorze
        if shortest_duration is None:
            shortest_duration = lib.Generator.correct_note_lengths[-1]

        if shortest_duration not in lib.Generator.correct_note_lengths:
            raise InvalidNoteDuration(shortest_duration)

        # Pobieramy listę dostępnych wartości rytmicznych i tworzymy listę dostępnych modyfikatorów
        available_notes = lib.Generator.get_available_note_lengths(shortest_duration=shortest_duration)
        available_mods = []

        base_note = random.choice(Note.base_notes)
        octave = OctaveType.random()
        base_duration = random.choice(available_notes)
        has_mod = random.choice([True, False])

        note = Note(note=base_note, octave=octave, base_duration=base_duration)

        # Jeśli długość nuty jest najkrótsza jaką możemy uzyskać, to nie możemy dodać modyfikatora wydłużającego,
        # gdyż kropka lub podwójna kropka doda mniejszą wartość rytmiczną
        if base_duration == shortest_duration:
            has_mod = False

        # Jeśli stosunek maksymalnej długości do wylosowanej jest większy lub równy 2 to przedłużenie kropką będzie
        # miało długośc mniejszej lub równej shortest_duration, więć dostępny staje się modyfikator kropki
        if shortest_duration / base_duration >= 2:
            available_mods.append(NoteModifier.DOT)

        # Jeśli stosunek maksymalnej długości do wylosowanej jest większy lub równy 4 to przedłużenie podwójna kropką
        # w najgorszym wypadku sprawi, że będzie konieczność pojawienia się nuty o długości shortest_duration
        if shortest_duration / base_duration >= 4:
            available_mods.append(NoteModifier.DOUBLE_DOT)

        if has_mod:
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

            id_difference = new_id % 12 - new_base_note_id

            if id_difference < -3:
                id_difference += 12
            if id_difference > 3:
                id_difference -= 12

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

    # endregion

    def get_duration(self, base_note_duration: int = 16) -> float:
        """
        Get note value in the minimum_note_length count

        Args:
            base_note_duration:    Minimum note length in which the duration will be calculated

        Returns:
            Note duration in the minimum_note_length count
        """
        if base_note_duration not in lib.Generator.correct_note_lengths:
            raise InvalidNoteDuration(base_note_duration)

        note_duration = base_note_duration / self.base_duration
        if NoteModifier.DOT in self.modifiers:
            note_duration = note_duration * 1.5
        elif NoteModifier.DOUBLE_DOT in self.modifiers:
            note_duration = note_duration * 1.75
        return note_duration

    def add_modifier(self, modifier: NoteModifier):
        """
        Add modifier to the note if it is not present

        Args:
            modifier:   Modifier to be added
        """
        if modifier not in self.modifiers:
            self.modifiers.append(modifier)

        if modifier == NoteModifier.DOUBLE_DOT:
            if NoteModifier.DOT in self.modifiers:
                self.modifiers.remove(NoteModifier.DOT)

        if modifier == NoteModifier.DOT:
            if NoteModifier.DOUBLE_DOT in self.modifiers:
                self.modifiers.remove(NoteModifier.DOUBLE_DOT)

        # We need to be sure that TIE is last, so in order to do it we first remove it
        # and then add it again at the end (probably could improve that, but not now).
        if NoteModifier.TIE in self.modifiers:
            self.modifiers.remove(NoteModifier.TIE)
            self.modifiers.append(NoteModifier.TIE)

        return self

    def remove_modifier(self, modifier: NoteModifier):
        """
        Remove modifier if it is present

        Args:
            modifier:   Modifier to be removed
        """
        self.modifiers.remove(modifier)
        return self
