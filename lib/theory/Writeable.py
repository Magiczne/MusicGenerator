import abc
import lib


class Writeable(abc.ABC):
    def __init__(self, base_duration: int = 4):
        if base_duration not in lib.Generator.available_note_lengths:
            raise ValueError

        self.base_duration: int = base_duration
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
        pass    # pragma: no cover