from .OctaveType import OctaveType


class Note:
    def __init__(self, note, octave=OctaveType.SMALL, duration=4, modifiers=None):
        # TODO: Walidacja czy octave jest instancją Octave

        self.note = note
        self.octave = octave
        self.duration = duration
        self.modifiers = modifiers

    def __str__(self):
        # TODO: Zwrócić reprezentację tekstową nuty
        pass
