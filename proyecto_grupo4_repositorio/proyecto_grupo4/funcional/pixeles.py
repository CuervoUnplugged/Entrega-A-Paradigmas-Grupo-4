"""Mapeo puro de intensidad de pixeles. Todas las funciones son puras:
no modifican sus argumentos, no leen ni escriben archivos y dan siempre el
mismo resultado para los mismos datos (transparencia referencial)."""
from functools import reduce


def curry(f):
    """Convierte f(a, b, c) en f(a)(b)(c) (tambien acepta f(a, b)(c), etc.)."""
    n = f.__code__.co_argcount

    def acumular(previos):
        def paso(*nuevos):
            todos = previos + nuevos
            return f(*todos) if len(todos) >= n else acumular(todos)

        return paso

    return acumular(())


def compose(*funciones):
    """compose(f, g)(x) == f(g(x))"""
    return lambda x: reduce(lambda acc, fn: fn(acc), reversed(funciones), x)


@curry
def ventana(nivel, ancho, p):
    """Ventana de nivel/ancho (window/level) de TAC: lleva un pixel de 12 bits a 0..255."""
    bajo = nivel - ancho / 2
    return max(0, min(255, int((p - bajo) * 255 / ancho)))


def normalizar(pixeles, nivel, ancho):
    """tuple(map(...)): devuelve una tupla NUEVA; la entrada no se toca."""
    return tuple(map(ventana(nivel, ancho), pixeles))


@curry
def en_banda(bajo, alto, p):
    return bajo <= p <= alto


@curry
def menor_que(limite, p):
    return p < limite


def mascara(norm, bordes, bajo, alto, umbral_borde):
    """1 si el pixel esta en la banda de intensidad Y no esta sobre un borde fuerte."""
    en_rango = en_banda(bajo, alto)
    sin_borde = menor_que(umbral_borde)
    return tuple(map(lambda p, e: 1 if en_rango(p) and sin_borde(e) else 0, norm, bordes))
