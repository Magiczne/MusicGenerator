from __future__ import annotations
from typing import List, Optional

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
        Pobierz długość pauzy wyrażonej w ilości base_duration

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
