import abc
import lib


class Writeable(abc.ABC):
    def __init__(self, base_duration: int = 4):
        if base_duration not in lib.Generator.correct_note_lengths:
            raise ValueError

        self.base_duration: int = base_duration
        super().__init__()

    @abc.abstractmethod
    def get_duration(self, base_duration: int = 16) -> float:
        """
        Pobierz długość nuty wyrażonej w ilości base_duration

        Args:
            base_duration:    Bazowa wartość rytmiczna, na podstawie której będą wykonywane obliczenia
        """
        pass    # pragma: no cover
