from __future__ import annotations
from typing import List


class Interval:
    # Liczba półtonów odpowiadająca każdemu z interwałów
    interval_semitones = {
        '1cz': 0,
        '2m': 1,
        '2w': 2,
        '3m': 3,
        '3w': 4,
        '4cz': 5,
        '4zw': 6,
        '5zmn': 6,
        '5cz': 7,
        '6m': 8,
        '6w': 9,
        '7m': 10,
        '7w': 11,
        '8cz': 12
    }

    # Lista używana do tworzenia interwałów komplementarnych
    interval_inversion = {
        'cz': 'cz',
        'zmn': 'zw',
        'zw': 'zmn',
        'm': 'w',
        'w': 'm'
    }

    @staticmethod
    def names() -> List[str]:
        """Zwraca listę dostępnych interwałów w formie tekstowej"""
        return list(Interval.interval_semitones.keys())

    def __init__(self, name: str):
        if name not in self.interval_semitones.keys():
            raise KeyError

        self.name = name
        self.degrees = int(name[0])
        self.quality = name[1:]
        self.semitones = self.interval_semitones[name]
        
    def __str__(self):
        return f'{self.name}'

    def __repr__(self):
        return f'Interval <{self.__str__()}>'

    def get_complement_interval(self) -> Interval:
        """
        Zwraca interwał komplementarny. Przykładowo dla 1cz zwraca 8cz

        Returns:
            Interwał komplementarny.
        """
        complement_degree = 9 - self.degrees
        complement_quality = self.interval_inversion[self.quality]
        return Interval(f'{complement_degree}{complement_quality}')
