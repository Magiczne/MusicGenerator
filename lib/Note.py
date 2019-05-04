from typing import List, Optional
import copy

from lib.Interval import Interval
from lib.NoteModifier import NoteModifier
from lib.OctaveType import OctaveType
from lib.Writeable import Writeable


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

    def get_duration(self, minimum_note_length: int = 16) -> float:
        """
        Get note value in the minimum_note_length count

        Args:
            minimum_note_length:    Minimum note length in which the duration will be calculated

        Returns:
            Note duration in the minimum_note_length count
        """
        note_duration = minimum_note_length / self.base_duration
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
