import abc
from typing import List


class Writeable(abc.ABC):
    def __init__(self, base_duration: int = 4):
        self.available_lengths: List[int] = [16, 8, 4, 2, 1]
        # TODO: przeniesc liste mozliwych wartosci
        if base_duration in self.available_lengths:
            self.base_duration: int = base_duration
        else:
            raise ValueError
        super().__init__()

    @abc.abstractmethod
    def get_duration(self, minimum_note_length: int = 16) -> float:
        """
        Get note value in the minimum_note_length count

        Args:
            minimum_note_length:    Minimum note length in which we duration will be calculated

        Returns:
            Note duration in the minimum_note_length count
        """
        pass
