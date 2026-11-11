"""Contenedor Option (Maybe): representa 'hay un valor' o 'no hay valor' sin usar None."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class Option(Generic[T]):
    """Clase base. Las dos variantes son Some(valor) y Nothing."""

    def es_vacio(self) -> bool:
        raise NotImplementedError

    def map(self, f: Callable[[T], U]) -> "Option[U]":
        raise NotImplementedError

    def flat_map(self, f: Callable[[T], "Option[U]"]) -> "Option[U]":
        raise NotImplementedError

    def get_or_else(self, defecto: Any) -> Any:
        raise NotImplementedError


@dataclass(frozen=True)
class Some(Option[T]):
    valor: T

    def es_vacio(self) -> bool:
        return False

    def map(self, f):
        return Some(f(self.valor))

    def flat_map(self, f):
        return f(self.valor)

    def get_or_else(self, defecto):
        return self.valor


@dataclass(frozen=True)
class Nothing(Option[Any]):
    def es_vacio(self) -> bool:
        return True

    def map(self, f):
        return self

    def flat_map(self, f):
        return self

    def get_or_else(self, defecto):
        return defecto


NOTHING = Nothing()
