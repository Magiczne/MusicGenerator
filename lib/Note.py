from typing import List

from .NoteModifier import NoteModifier
from .OctaveType import OctaveType
from .Writeable import Writeable


class Note(Writeable):
    base_notes = ['c', 'd', 'e', 'f', 'g', 'a', 'b']
    def __init__(self, note: str, octave: OctaveType = OctaveType.SMALL, base_duration: int = 4):
        super().__init__(base_duration)

        if note[0] not in self.base_notes:
            raise ValueError

        self.note = note
        self.octave: OctaveType = octave
        self.modifiers: List[NoteModifier] = []

    def __eq__(self, other):
        return str(self) == str(other)

    def __str__(self):
        mods = ''.join([mod.value for mod in self.modifiers])
        return f'{self.note}{self.octave.value}{self.base_duration}{mods}'

    def __repr__(self):
        return f'Note <{self.__str__()}>'

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
