"""Capa IMPERATIVA ("Imperative Shell"): es la unica parte con entrada/salida.
Toda la logica y validacion se encadena con el contenedor monadico Option (Maybe).

  python3 cli.py normalizar --nivel N --ancho A            (PGM por stdin -> PGM por stdout)
  python3 cli.py segmentar --imagen f --bordes f --banda LO HI
                           --umbral-borde E --area-min N --salida-mascara f
"""
import argparse
import sys

import pgm
import pixeles
import segmentacion
from option import NOTHING, Option, Some


def _leer_archivo(ruta: str) -> Option:
    with open(ruta) as f:
        return pgm.parsear_pgm(f.read())


def _error(mensaje: str) -> int:
    sys.stderr.write(mensaje + "\n")
    return 1


def _escribir_stdout(texto: str) -> int:
    sys.stdout.write(texto)
    return 0


def _normalizar(args) -> int:
    return (
        pgm.parsear_pgm(sys.stdin.read())
        .map(lambda img: img._replace(
            maxval=255,
            pixeles=pixeles.normalizar(img.pixeles, args.nivel, args.ancho)
        ))
        .map(pgm.formatear_pgm)
        .fold(
            si_vacio=lambda: _error("PGM invalido"),
            si_valor=_escribir_stdout
        )
    )


def _emitir_reporte(img_base, resultado: segmentacion.ResultadoSegmentacion, ruta_mascara: str) -> int:
    with open(ruta_mascara, "w") as f:
        f.write(pgm.formatear_pgm(img_base._replace(maxval=255, pixeles=resultado.mascara)))
    return segmentacion.region_mayor(resultado.regiones).fold(
        si_vacio=lambda: (print("SIN_REGION") or 0),
        si_valor=lambda _: (
            print(f"REGIONES {len(resultado.regiones)}") or
            all(print(f"REGION {r.etiqueta} {r.area} {r.x_min} {r.y_min} {r.x_max} {r.y_max} {r.cx} {r.cy}") is None
                for r in resultado.regiones) and 0
        )
    )


def _segmentar(args) -> int:
    return (
        _leer_archivo(args.imagen)
        .flat_map(lambda norm: _leer_archivo(args.bordes).map(lambda bordes: (norm, bordes)))
        .filter(lambda par: len(par[0].pixeles) == len(par[1].pixeles))
        .flat_map(lambda par: segmentacion.segmentar_opt(
            par[0].pixeles, par[1].pixeles, par[0].ancho, par[0].alto,
            args.banda[0], args.banda[1], args.umbral_borde, args.area_min
        ).map(lambda res: (par[0], res)))
        .fold(
            si_vacio=lambda: _error("Imagenes invalidas o de distinto tamano"),
            si_valor=lambda datos: _emitir_reporte(datos[0], datos[1], args.salida_mascara)
        )
    )


def main(argv) -> int:
    p = argparse.ArgumentParser(prog="cli.py")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("normalizar")
    a.add_argument("--nivel", type=int, required=True)
    a.add_argument("--ancho", type=int, required=True)
    b = sub.add_parser("segmentar")
    b.add_argument("--imagen", required=True)
    b.add_argument("--bordes", required=True)
    b.add_argument("--banda", type=int, nargs=2, required=True)
    b.add_argument("--umbral-borde", type=int, required=True)
    b.add_argument("--area-min", type=int, required=True)
    b.add_argument("--salida-mascara", required=True)
    args = p.parse_args(argv)
    return _normalizar(args) if args.cmd == "normalizar" else _segmentar(args)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))