class InvalidBaseNoteDuration(Exception):
    """Zgłaszany, gdy długość nuty nie jest poprawną bazową wartością rytmiczną"""

    def __init__(self, duration):
        super().__init__()
        self.message = f'{duration} is not a valid note base duration!'
