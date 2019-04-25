from .NoteModifier import NoteModifier
from .OctaveType import OctaveType


class Note:
    def __init__(self, note, octave=OctaveType.SMALL, base_duration=4):
        # TODO: Walidacja czy octave jest instancją Octave

        self.note = note
        self.octave = octave
        self.base_duration = base_duration
        self.modifiers = []

    def __eq__(self, other):
        return(
            self.__class__ == other.__class__ and
            self.note == other.note and
            self.octave == other.octave and
            self.base_duration == other.base_duration and
            self.modifiers == other.modifiers
        )

    def __str__(self):
        # TODO: Zwrócić reprezentację tekstową nuty uwzględniając modyfikatory
        pass

    def get_duration(self, minimum_note_length: int = 16):
        """
        Get note value in the minumum_note_length count

        Args:
            minimum_note_length:    Minimum note length in which we want the duration
        """
        # TODO: Zwrócić aktualną długość nuty, zwracając uwagi na kropkę i podwójną kropkę,
        # Licząc na podstawie wartości podanej w parametrze minimum_note_length
        pass

    def add_modifier(self, modifier: NoteModifier):
        """
        Add modifier to the note if it is not present

        Args:
            modifier:   Modifier to be added
        """
        # TODO: Dodaj modyfikator
        # TODO: Ustaw modyfikator w odpowiedniej kolejnośći - najpierw kropki później tylda, itd...
        return self

    def remove_modifier(self, modifier: NoteModifier):
        """
        Remove modifier if it is present

        Args:
            modifier:   Modifier to be removed
        """
        # TODO: Usuń modyfikator
        return self
