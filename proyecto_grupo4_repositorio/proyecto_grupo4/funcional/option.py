"""Contenedor monadico Option (Maybe): representa 'hay un valor' (Some) o
'no hay valor' (Nothing) sin usar None ni excepciones, cumpliendo las leyes monadicas."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Generic, TypeVar

T = TypeVar("T")
U = TypeVar("U")


class Option(Generic[T]):
    """Tipo algebraico monadico con variantes Some(valor) y Nothing."""

    def es_vacio(self) -> bool:
        raise NotImplementedError

    def map(self, f: Callable[[T], U]) -> "Option[U]":
        raise NotImplementedError

    def flat_map(self, f: Callable[[T], "Option[U]"]) -> "Option[U]":
        raise NotImplementedError

    def filter(self, predicado: Callable[[T], bool]) -> "Option[T]":
        raise NotImplementedError

    def fold(self, si_vacio: Callable[[], U], si_valor: Callable[[T], U]) -> U:
        raise NotImplementedError

    def get_or_else(self, defecto: Any) -> Any:
        raise NotImplementedError


@dataclass(frozen=True)
class Some(Option[T]):
    valor: T

    def es_vacio(self) -> bool:
        return False

    def map(self, f: Callable[[T], U]) -> Option[U]:
        return Some(f(self.valor))

    def flat_map(self, f: Callable[[T], Option[U]]) -> Option[U]:
        return f(self.valor)

    def filter(self, predicado: Callable[[T], bool]) -> Option[T]:
        return self if predicado(self.valor) else NOTHING

    def fold(self, si_vacio: Callable[[], U], si_valor: Callable[[T], U]) -> U:
        return si_valor(self.valor)

    def get_or_else(self, defecto: Any) -> Any:
        return self.valor


@dataclass(frozen=True)
class Nothing(Option[Any]):
    def es_vacio(self) -> bool:
        return True

    def map(self, f: Callable[[Any], U]) -> Option[U]:
        return self

    def flat_map(self, f: Callable[[Any], Option[U]]) -> Option[U]:
        return self

    def filter(self, predicado: Callable[[Any], bool]) -> Option[Any]:
        return self

    def fold(self, si_vacio: Callable[[], U], si_valor: Callable[[Any], U]) -> U:
        return si_vacio()

    def get_or_else(self, defecto: Any) -> Any:
        return defecto


NOTHING = Nothing()