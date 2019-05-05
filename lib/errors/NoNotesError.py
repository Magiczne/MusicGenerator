from typing import Optional


class NoNotesError(Exception):
    """Raised when there is no notes in the generated data list"""

    def __init__(self, message: Optional[str] = None):
        super().__init__(message)

        if message is not None:
            self.message = "There are no notes in the generated data!"
        else:
            self.message = message
