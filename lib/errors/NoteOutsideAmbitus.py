from lib.theory import Note


class NoteOutsideAmbitus(Exception):
    """Zgłaszany gdy nuta nie mieści się w ambitusie"""

    def __init__(self, note: Note, lowest: Note, highest: Note):
        super().__init__()
        self.message = f'Note {note} is outside ambitus [{lowest}; {highest}]'
