from __future__ import annotations
from typing import List, Optional
import random

import lib
from lib.theory.RestModifier import RestModifier
from lib.theory.Writeable import Writeable
from lib.errors import InvalidBaseNoteDuration
from lib.errors import BaseDurationTooLarge


class Rest(Writeable):
    def __init__(self, base_duration: int = 4, modifiers: Optional[List[RestModifier]] = None):
        super().__init__(base_duration)

        self.modifiers: List[RestModifier] = []

        if modifiers is not None:
            for mod in modifiers:
                self.add_modifier(mod)

    def __eq__(self, other):
        return self.__class__ == other.__class__ and str(self) == str(other)

    def __str__(self):
        mods = ''.join([mod.value for mod in self.modifiers])
        return f'r{self.base_duration}{mods}'

    def __repr__(self):
        return f'Rest <{self.__str__()}>'

    def get_duration(self, base_duration: int = 16) -> int:
        """
        Pobierz długośc pauzy wyrażonej w ilości base_duration

        Args:
            base_duration:     Bazowa wartość rytmiczna, na podstawie której będą wykonywane obliczenia

        Raises:
            InvalidBaseNoteDuration:        Jeśli base_duration nie jest poprawną bazową wartością rytmiczną
            BaseDurationTooLarge:           Jeśli base_duration jest dłuższą wartością rytmiczną niż self.base_duration
        """
        if base_duration not in lib.Generator.correct_note_lengths:
            raise InvalidBaseNoteDuration(base_duration)

        if self.base_duration > base_duration:
            raise BaseDurationTooLarge(self.base_duration, base_duration)

        rest_duration = base_duration / self.base_duration

        if RestModifier.DOT in self.modifiers:
            rest_duration = rest_duration * 1.5
        elif RestModifier.DOUBLE_DOT in self.modifiers:
            rest_duration = rest_duration * 1.75

        return int(rest_duration)

    def add_modifier(self, modifier: RestModifier):
        """
        Dodaj modyfikator do listy modyfikatorów, jeśli już takiego nie ma.
        Jeśli dodawana jest kropka lub podwójna kropka, to odpowiednio nadpisana zostaje podwójna kropka lub kropka

        Args:
            modifier:   Modyfikator do dodania
        """
        if modifier not in self.modifiers:
            self.modifiers.append(modifier)

        if modifier == RestModifier.DOUBLE_DOT:
            if RestModifier.DOT in self.modifiers:
                self.modifiers.remove(RestModifier.DOT)

        if modifier == RestModifier.DOT:
            if RestModifier.DOUBLE_DOT in self.modifiers:
                self.modifiers.remove(RestModifier.DOUBLE_DOT)

        return self

    def remove_modifier(self, modifier: RestModifier):
        """
        Usuń modyfikator, jeśli znajduje się w liście modyfikatorów

        Args:
            modifier:   Modyfikator do usunięcia
        """
        self.modifiers.remove(modifier)
        return self

    @staticmethod
    def random(longest_duration: Optional[int] = None) -> Rest:
        """
        Wygeneruj pauzę z losowymi parametrami o maksymalnej długości podanej w parametrze

        Args:
            longest_duration:   Najdłuższa możliwa wartośc rytmiczna, która może wystąpić podana w ilości
                                lib.Generator.shortest_note_duration.
                                Jeśli nie podano, skrypt zakłada że nuta o każdej długości jest dozwolona.

        Returns:
            Pauza z losowymi parametrami o maksymalnej długości wynoszącej longest_duration
        """
        # Jeśli nie był podany parametr najdłuższej możliwej wartości rytmicznej, to zakładamy że nuta o każdej długości
        # jest dozwolona do wygenerowania
        if longest_duration is None:
            longest_duration = lib.Generator.shortest_note_duration

        # Pobieramy listę dostępnych wartości rytmicznych i tworzymy listę dostępnych modyfikatorów
        available_notes = lib.Generator.get_available_note_lengths(longest_duration=longest_duration)
        available_mods = []

        base_duration = random.choice(available_notes)
        has_mod = random.choice([True, False])

        rest = Rest(base_duration=base_duration)

        # Jeśli długość nuty jest najkrótsza jaką możemy uzyskać, to nie możemy dodać modyfikatora wydłużającego,
        # gdyż kropka lub podwójna kropka doda mniejszą wartość rytmiczną
        if base_duration >= lib.Generator.shortest_note_duration:
            has_mod = False

        # Jeśli dostępne miejsce jest większej lub równej długości niż potencjalna pauza z kropką, to do dostępnych
        # modyfikatorów możemy dodać przedłużenie w postaci kropki
        if longest_duration >= rest.get_duration(lib.Generator.shortest_note_duration) * 1.5:
            available_mods.append(RestModifier.DOT)

        # Jeśli dostępne miejsce jest większej lub równej długości niż potencjalna pauza z podwójną kropką, to do
        # dostępnych modyfikatorów możemy dodać przedłużenie w postaci podwójnej kropki.
        # Sprawdzamy również, czy nie jest to przedostatnia dostępna wartośc rytmiczna. Jeśli tak jest, to nie możemy
        # dodać podwójnej kropki, gdyż skutkowałoby to dodaniem pauzy o połowę mniejszej wartości rytmicznej niż
        # dozwolona
        if longest_duration >= rest.get_duration(lib.Generator.shortest_note_duration) * 1.75 \
                and rest.base_duration > 2 * lib.Generator.shortest_note_duration:
            available_mods.append(RestModifier.DOUBLE_DOT)

        if has_mod and len(available_mods) > 0:
            rest.add_modifier(random.choice(available_mods))

        return rest
