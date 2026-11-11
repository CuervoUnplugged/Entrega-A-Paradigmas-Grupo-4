"""Lectura/escritura de PGM P2 como funciones puras sobre texto."""
from typing import NamedTuple

from option import NOTHING, Option, Some


class Imagen(NamedTuple):
    ancho: int
    alto: int
    maxval: int
    pixeles: tuple


def parsear_pgm(texto: str) -> Option:
    """Some(Imagen) si el texto es un PGM P2 valido; Nothing en cualquier otro caso."""
    sin_comentarios = "\n".join(filter(lambda l: not l.lstrip().startswith("#"), texto.splitlines()))
    tokens = sin_comentarios.split()
    if len(tokens) < 4 or tokens[0] != "P2" or not all(map(str.isdigit, tokens[1:])):
        return NOTHING
    ancho, alto, maxval = int(tokens[1]), int(tokens[2]), int(tokens[3])
    datos = tuple(map(int, tokens[4:]))
    if ancho <= 0 or alto <= 0 or len(datos) != ancho * alto:
        return NOTHING
    return Some(Imagen(ancho, alto, maxval, datos))


def formatear_pgm(img: Imagen) -> str:
    filas = (" ".join(map(str, img.pixeles[y * img.ancho:(y + 1) * img.ancho])) for y in range(img.alto))
    return f"P2\n{img.ancho} {img.alto}\n{img.maxval}\n" + "\n".join(filas) + "\n"
