from typing import List

from .NoteModifier import NoteModifier
from .OctaveType import OctaveType
from .Writeable import Writeable


class Note(Writeable):
    def __init__(self, note: str, octave: OctaveType = OctaveType.SMALL, base_duration: int = 4):
        super().__init__(base_duration)
        self.available_notes: List[str] = ['c', 'd', 'e', 'f', 'g', 'a', 'h']
        # TODO: przeniesc liste mozliwych nut
        if note in self.available_notes:
            self.note: str = note
        else:
            raise ValueError
        self.octave: OctaveType = octave
        self.modifiers: List[NoteModifier] = []

    def __eq__(self, other):
        return(
            self.__class__ == other.__class__ and
            self.note == other.note and
            self.octave == other.octave and
            self.base_duration == other.base_duration and
            self.modifiers == other.modifiers
        )

    def __str__(self):
        mods = ''.join([mod.value for mod in self.modifiers])
        octv = self.octave.value
        return f'{self.note}{octv}{self.base_duration}{mods}'

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
