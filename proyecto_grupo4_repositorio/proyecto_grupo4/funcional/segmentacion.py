"""Segmentacion funcional pura de regiones conexas mediante reduccion por capas
de frontera inmutables (sin recursion de cola para evitar desbordamiento de pila)
y composicion monadica con Option/Maybe.
"""
from functools import reduce
from typing import NamedTuple, Tuple, FrozenSet

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


class ResultadoSegmentacion(NamedTuple):
    """Tipo estructurado inmutable (compatible con desestructuracion de 2 elementos)."""
    regiones: Tuple[Region, ...]
    mascara: Tuple[int, ...]


def vecinos4(i: int, ancho: int, alto: int):
    """Generador perezoso de los 4 vecinos ortogonales (arriba/abajo/izquierda/derecha)."""
    x, y = i % ancho, i // ancho
    if y > 0:
        yield i - ancho
    if y < alto - 1:
        yield i + ancho
    if x > 0:
        yield i - 1
    if x < ancho - 1:
        yield i + 1


def _capa_siguiente(frontera: FrozenSet[int], visitados: FrozenSet[int],
                    activos: FrozenSet[int], ancho: int, alto: int) -> FrozenSet[int]:
    """Calcula de forma pura la siguiente capa de vecinos activos no visitados."""
    return frozenset(
        vecino
        for actual in frontera
        for vecino in vecinos4(actual, ancho, alto)
        if vecino in activos and vecino not in visitados
    )


def crecer_region(mascara, ancho: int, alto: int, semilla: int) -> FrozenSet[int]:
    """Expande una componente conexa desde 'semilla' mediante iteracion funcional
    por capas de frontera en espacio de pila constante O(1), sin recursion de cola."""
    if semilla < 0 or semilla >= len(mascara) or mascara[semilla] != 1:
        return frozenset()
    activos = frozenset(i for i, v in enumerate(mascara) if v == 1)
    frontera = frozenset((semilla,))
    region = frozenset((semilla,))
    while frontera:
        frontera = _capa_siguiente(frontera, region, activos, ancho, alto)
        region = region | frontera
    return region


def componentes(mascara, ancho: int, alto: int) -> Tuple[FrozenSet[int], ...]:
    """Obtiene todas las componentes conexas (4-vecinos) de los pixeles activos
    sin usar recursion de cola."""
    activos = frozenset(filter(lambda i: mascara[i] == 1, range(len(mascara))))
    pendientes = activos
    resultado = []
    while pendientes:
        semilla = min(pendientes)
        frontera = frozenset((semilla,))
        region = frozenset((semilla,))
        while frontera:
            frontera = _capa_siguiente(frontera, region, pendientes, ancho, alto)
            region = region | frontera
        resultado.append(region)
        pendientes = pendientes - region
    return tuple(resultado)


class _Acum(NamedTuple):
    area: int
    x_min: int
    y_min: int
    x_max: int
    y_max: int
    suma_x: int
    suma_y: int


def _acumular(ancho: int):
    def paso(acc: _Acum, i: int) -> _Acum:
        x, y = i % ancho, i // ancho
        return _Acum(acc.area + 1, min(acc.x_min, x), min(acc.y_min, y),
                     max(acc.x_max, x), max(acc.y_max, y), acc.suma_x + x, acc.suma_y + y)

    return paso


def estadisticas_opt(etiqueta: int, pixeles, ancho: int, area_min: int = 1) -> Option[Region]:
    """Calcula las estadisticas de una region devolviendo Option[Region]:
    Some(Region) si cumple el area minima, o NOTHING si es vacia o menor al umbral."""
    return (
        Some(tuple(sorted(pixeles)))
        .filter(lambda px: len(px) >= max(1, area_min))
        .map(lambda px: reduce(_acumular(ancho), px, _Acum(0, 10 ** 9, 10 ** 9, -1, -1, 0, 0)))
        .map(lambda a: Region(
            etiqueta, a.area, a.x_min, a.y_min, a.x_max, a.y_max,
            round(a.suma_x / a.area, 2), round(a.suma_y / a.area, 2)
        ))
    )


def estadisticas(etiqueta: int, pixeles, ancho: int) -> Region:
    """Area, caja y centroide de una region calculados via Option + reduce."""
    return estadisticas_opt(etiqueta, pixeles, ancho, 1).get_or_else(
        Region(etiqueta, 0, 0, 0, 0, 0, 0.0, 0.0)
    )


def region_mayor(regiones) -> Option[Region]:
    """Some(region de mayor area) o Nothing si no hay ninguna, usando fold monadico."""
    return reduce(
        lambda opt, r: opt.fold(
            si_vacio=lambda: Some(r),
            si_valor=lambda actual: Some(r) if r.area > actual.area else opt
        ),
        regiones,
        NOTHING
    )


def segmentar_opt(norm, bordes, ancho: int, alto: int, bajo: int,
                  alto_banda: int, umbral_borde: int, area_min: int) -> Option[ResultadoSegmentacion]:
    """Pipeline monadico completo de segmentacion que valida dimensiones con Option."""
    return (
        Some((norm, bordes))
        .filter(lambda par: ancho > 0 and alto > 0 and len(par[0]) == ancho * alto and len(par[1]) == ancho * alto)
        .map(lambda par: construir_mascara(par[0], par[1], bajo, alto_banda, umbral_borde))
        .map(lambda binaria: tuple(
             sorted(
                 filter(lambda r: len(r) >= area_min, componentes(binaria, ancho, alto)),
                 key=lambda r: (-len(r), min(r))
             )
        ))
        .map(lambda ordenadas: ResultadoSegmentacion(
            regiones=tuple(
                opt.valor
                for n, r in enumerate(ordenadas)
                for opt in (estadisticas_opt(n + 1, r, ancho, area_min),)
                if not opt.es_vacio()
            ),
            mascara=tuple(
                {i: n + 1 for n, r in enumerate(ordenadas) for i in r}.get(idx, 0)
                for idx in range(ancho * alto)
            )
        ))
    )


def segmentar(norm, bordes, ancho: int, alto: int, bajo: int,
              alto_banda: int, umbral_borde: int, area_min: int) -> ResultadoSegmentacion:
    """Funcion pura compatible: delega en el pipeline monadico segmentar_opt."""
    return segmentar_opt(
        norm, bordes, ancho, alto, bajo, alto_banda, umbral_borde, area_min
    ).get_or_else(ResultadoSegmentacion((), (0,) * len(norm)))