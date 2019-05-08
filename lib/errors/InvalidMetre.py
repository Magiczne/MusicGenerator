from typing import Tuple


class InvalidMetre(Exception):
    """Zgłaszany, gdy metrum jest nieprawidłowe"""

    def __init__(self, metre: Tuple[int, int]):
        super().__init__()
        self.message = f'Metre {metre[0]}/{metre[1]} is invalid!'
