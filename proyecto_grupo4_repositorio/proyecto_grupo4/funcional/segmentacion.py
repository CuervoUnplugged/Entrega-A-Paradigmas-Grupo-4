"""Segmentacion de regiones con recursion de cola + trampolin.

Python NO optimiza llamadas de cola (no hay TCO). Para obtener el mismo efecto
cada paso recursivo devuelve un objeto Rebote (la siguiente llamada, sin
ejecutar) y el trampolin las va ejecutando en un bucle: la pila no crece.
"""
from functools import reduce
from typing import NamedTuple

from option import NOTHING, Option, Some
from pixeles import mascara as construir_mascara


class Rebote(NamedTuple):
    funcion: object
    args: tuple


def rebotar(funcion, *args):
    return Rebote(funcion, args)


def trampolin(resultado):
    while isinstance(resultado, Rebote):
        resultado = resultado.funcion(*resultado.args)
    return resultado


class Region(NamedTuple):
    etiqueta: int
    area: int
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    cx: float
    cy: float


def vecinos4(i, ancho, alto):
    """Generador perezoso de los vecinos arriba/abajo/izquierda/derecha."""
    x, y = i % ancho, i // ancho
    if y > 0:
        yield i - ancho
    if y < alto - 1:
        yield i + ancho
    if x > 0:
        yield i - 1
    if x < ancho - 1:
        yield i + 1


def _crecer(mascara, ancho, alto, frontera, region):
    """Recursiva de cola: la ultima accion es la llamada recursiva (via rebotar)."""
    if not frontera:
        return region
    actual, resto = frontera[0], frontera[1:]
    if actual in region:
        return rebotar(_crecer, mascara, ancho, alto, resto, region)
    nuevos = tuple(v for v in vecinos4(actual, ancho, alto) if mascara[v] == 1 and v not in region)
    return rebotar(_crecer, mascara, ancho, alto, nuevos + resto, region | {actual})


def crecer_region(mascara, ancho, alto, semilla):
    return trampolin(_crecer(mascara, ancho, alto, (semilla,), frozenset()))


def _etiquetar(mascara, ancho, alto, pendientes, regiones):
    if not pendientes:
        return regiones
    region = crecer_region(mascara, ancho, alto, min(pendientes))
    return rebotar(_etiquetar, mascara, ancho, alto, pendientes - region, regiones + (region,))


def componentes(mascara, ancho, alto):
    """Componentes conexas (4-vecinos) de los pixeles con valor 1."""
    pendientes = frozenset(filter(lambda i: mascara[i] == 1, range(len(mascara))))
    return trampolin(_etiquetar(mascara, ancho, alto, pendientes, ()))


class _Acum(NamedTuple):
    area: int
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    suma_x: int
    suma_y: int


def _acumular(ancho):
    def paso(acc, i):
        x, y = i % ancho, i // ancho
        return _Acum(acc.area + 1, min(acc.x_min, x), min(acc.y_min, y),
                     max(acc.x_max, x), max(acc.y_max, y), acc.suma_x + x, acc.suma_y + y)

    return paso


def estadisticas(etiqueta, pixeles, ancho) -> Region:
    """Area, caja y centroide de una region, calculados con reduce."""
    vacio = _Acum(0, 10 ** 9, 10 ** 9, -1, -1, 0, 0)
    a = reduce(_acumular(ancho), sorted(pixeles), vacio)
    return Region(etiqueta, a.area, a.x_min, a.y_min, a.x_max, a.y_max,
                  round(a.suma_x / a.area, 2), round(a.suma_y / a.area, 2))


def region_mayor(regiones) -> Option:
    """Some(region de mayor area) o Nothing si no hay ninguna."""
    return reduce(lambda opt, r: Some(r) if opt.es_vacio() or r.area > opt.valor.area else opt,
                  regiones, NOTHING)


def segmentar(norm, bordes, ancho, alto, bajo, alto_banda, umbral_borde, area_min):
    """Funcion pura: devuelve (regiones, mascara_etiquetada) como tuplas inmutables."""
    binaria = construir_mascara(norm, bordes, bajo, alto_banda, umbral_borde)
    grandes = filter(lambda r: len(r) >= area_min, componentes(binaria, ancho, alto))  # perezoso
    ordenadas = sorted(grandes, key=lambda r: (-len(r), min(r)))
    regiones = tuple(estadisticas(n + 1, r, ancho) for n, r in enumerate(ordenadas))
    etiqueta_de = {i: n + 1 for n, r in enumerate(ordenadas) for i in r}
    etiquetada = tuple(map(lambda i: etiqueta_de.get(i, 0), range(len(norm))))
    return regiones, etiquetada
