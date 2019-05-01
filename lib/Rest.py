from typing import List

from .RestModifier import RestModifier
from .Writeable import Writeable


class Rest(Writeable):
    def __init__(self, base_duration: int = 4):
        super().__init__(base_duration)

        self.modifiers: List[RestModifier] = []

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.base_duration == other.base_duration and
            self.modifiers == other.modifiers
        )

    def __str__(self):
        mods = ''.join([mod.value for mod in self.modifiers])
        return f'r{self.base_duration}{mods}'

    def get_duration(self, minimum_note_length: int = 16) -> float:
        """
        Get note value in the minimum_note_length count

        Args:
            minimum_note_length:    Minimum note length in which we duration will be calculated

        Returns:
            Note duration in the minimum_note_length count
        """
        rest_duration = minimum_note_length / self.base_duration
        if RestModifier.DOT in self.modifiers:
            rest_duration = rest_duration * 1.5
        elif RestModifier.DOUBLE_DOT in self.modifiers:
            rest_duration = rest_duration * 1.75
        return rest_duration

    def add_modifier(self, modifier: RestModifier):
        """
        Add modifier to the rest if it is not present

        Args:
            modifier:   Modifier to be added
        """
        if modifier == RestModifier.DOUBLE_DOT:
            if RestModifier.DOT in self.modifiers:
                self.modifiers.remove(RestModifier.DOT)
            elif RestModifier.DOUBLE_DOT in self.modifiers:
                self.modifiers.remove(RestModifier.DOUBLE_DOT)

        if modifier == RestModifier.DOT:
            if RestModifier.DOUBLE_DOT in self.modifiers:
                self.modifiers.remove(RestModifier.DOUBLE_DOT)
            elif RestModifier.DOT in self.modifiers:
                self.modifiers.remove(RestModifier.DOT)

        self.modifiers.append(modifier)
        return self

    def remove_modifier(self, modifier: RestModifier):
        """
        Remove modifier if it is present

        Args:
            modifier:   Modifier to be removed
        """
        self.modifiers.remove(modifier)
        return self
