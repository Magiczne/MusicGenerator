class NoNotesError(Exception):
    """Zgłaszany gdy w liście brakuje nut"""

    def __init__(self):
        super().__init__()
        self.message = "There are no notes in the generated data!"
