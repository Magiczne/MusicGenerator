from __future__ import annotations
from typing import List, Optional
import random

import lib
from lib.theory.RestModifier import RestModifier
from lib.theory.Writeable import Writeable
from lib.errors import InvalidNoteDuration


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

    def get_duration(self, minimum_note_length: int = 16) -> float:
        """
        Get note value in the minimum_note_length count

        Args:
            minimum_note_length:    Minimum note length in which we duration will be calculated

        Returns:
            Note duration in the minimum_note_length count
        """
        rest_duration = minimum_note_length / self.base_duration
        if RestModifier.DOT in self.modifiers:
            rest_duration = rest_duration * 1.5
        elif RestModifier.DOUBLE_DOT in self.modifiers:
            rest_duration = rest_duration * 1.75
        return rest_duration

    def add_modifier(self, modifier: RestModifier):
        """
        Add modifier to the rest if it is not present

        Args:
            modifier:   Modifier to be added
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
        Remove modifier if it is present

        Args:
            modifier:   Modifier to be removed
        """
        self.modifiers.remove(modifier)
        return self

    @staticmethod
    def random(shortest_duration: Optional[int] = None) -> Rest:
        """
        Wygeneruj pauzę z losowymi parametrami

        Args:
            shortest_duration:  Najkrótsza możliwa wartość rytmiczna, która może wystąpić

        Returns:
            Pauza z losowymi parametrami

        Raises:
            InvalidNoteDuration:    Gdy shortest_duration nie jest poprawną długością bazową nuty
        """

        # Jeśli nie był podany parametr najkrótszej nuty, to zakładamy że najkrótszą możliwą wartością rytmiczną
        # jest ta, która jest najmniejsza możliwa do wystąpienia w generatorze
        if shortest_duration is None:
            shortest_duration = lib.Generator.shortest_note_duration

        # Pobieramy listę dostępnych wartości rytmicznych i tworzymy listę dostępnych modyfikatorów
        available_notes = lib.Generator.get_available_note_lengths(shortest_duration=shortest_duration)
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
        if shortest_duration >= rest.get_duration(lib.Generator.shortest_note_duration) * 1.5:
            available_mods.append(RestModifier.DOT)

        # Jeśli dostępne miejsce jest większej lub równej długości niż potencjalna pauza z podwójną kropką, to do
        # dostępnych modyfikatorów możemy dodać przedłużenie w postaci podwójnej kropki.
        # Sprawdzamy również, czy nie jest to przedostatnia dostępna wartośc rytmiczna. Jeśli tak jest, to nie możemy
        # dodać podwójnej kropki, gdyż skutkowałoby to dodaniem pauzy o połowę mniejszej wartości rytmicznej niż
        # dozwolona
        if shortest_duration >= rest.get_duration(lib.Generator.shortest_note_duration) * 1.75 \
                and rest.base_duration > 2 * lib.Generator.shortest_note_duration:
            available_mods.append(RestModifier.DOUBLE_DOT)

        if has_mod and len(available_mods) > 0:
            rest.add_modifier(random.choice(available_mods))

        return rest
