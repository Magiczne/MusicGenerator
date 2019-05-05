class InvalidNoteDuration(Exception):
    """Raised when note base duration is not an invalid duration"""

    def __init__(self, duration):
        super().__init__()
        self.message = f'{duration} is not a valid note base duration!'
