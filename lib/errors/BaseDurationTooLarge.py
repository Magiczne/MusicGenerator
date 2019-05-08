class BaseDurationTooLarge(Exception):
    """Zgłaszany gdy długość nuty jest zbyt mała aby wykonać pewne obliczenia"""

    def __init__(self, note_base, calculation_base):
        super().__init__()
        self.message = f'Note is too short to calculate duration. ' \
            f'Cannot get length of {note_base} using {calculation_base}'
