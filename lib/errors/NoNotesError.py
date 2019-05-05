class NoNotesError(Exception):
    """Raised when there is no notes in the generated data list"""

    def __init__(self):
        super().__init__()
        self.message = "There are no notes in the generated data!"
