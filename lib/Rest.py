from typing import List

from .RestModifier import RestModifier
from .Writeable import Writeable


class Rest(Writeable):
    def __init__(self, base_duration: int = 4):
        self.base_duration: int = base_duration
        self.modifiers: List[RestModifier] = []

    def __eq__(self, other):
        return (
            self.__class__ == other.__class__ and
            self.base_duration == other.base_duration and
            self.modifiers == other.modifiers
        )

    def __str__(self):
        # TODO: Zwrócić reprezentację tekstową pauzy uwzględniając modyfikatory
        pass

    def get_duration(self, minimum_note_length: int = 16) -> int:
        """
        Get rest value in the minimum_note_length count

        Args:
            minimum_note_length:    Minimum note length in which we duration will be calculated

        Returns:
            Rest duration in the minimum_note_length count
        """

    def add_modifier(self, modifier: RestModifier):
        """
        Add modifier to the rest if it is not present

        Args:
            modifier:   Modifier to be added
        """
        # TODO: Dodaj modyfikator
        # TODO: Jeśli jest kropka i dodawana jest podwójna to usuń pojedynczą
        return self

    def remove_modifier(self, modifier: RestModifier):
        """
        Remove modifier if it is present

        Args:
            modifier:   Modifier to be removed
        """
        # TODO: Usuń modyfikator
        return self
