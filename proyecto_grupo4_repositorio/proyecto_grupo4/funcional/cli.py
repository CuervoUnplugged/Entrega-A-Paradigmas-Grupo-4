"""Capa IMPERATIVA ("Imperative Shell"): es la unica parte con entrada/salida.
Toda la logica esta en modulos puros (Functional Core).

  python3 cli.py normalizar --nivel N --ancho A            (PGM por stdin -> PGM por stdout)
  python3 cli.py segmentar --imagen f --bordes f --banda LO HI
                           --umbral-borde E --area-min N --salida-mascara f
"""
import argparse
import sys

import pgm
import pixeles
import segmentacion
from option import NOTHING


def _leer_archivo(ruta):
    with open(ruta) as f:
        return pgm.parsear_pgm(f.read())


def _normalizar(args):
    opt = pgm.parsear_pgm(sys.stdin.read())
    if opt.es_vacio():
        sys.stderr.write("PGM invalido\n")
        return 1
    img = opt.valor
    salida = img._replace(maxval=255, pixeles=pixeles.normalizar(img.pixeles, args.nivel, args.ancho))
    sys.stdout.write(pgm.formatear_pgm(salida))
    return 0


def _segmentar(args):
    norm, bordes = _leer_archivo(args.imagen), _leer_archivo(args.bordes)
    if norm.es_vacio() or bordes.es_vacio() or len(norm.valor.pixeles) != len(bordes.valor.pixeles):
        sys.stderr.write("Imagenes invalidas o de distinto tamano\n")
        return 1
    n = norm.valor
    regiones, etiquetada = segmentacion.segmentar(
        n.pixeles, bordes.valor.pixeles, n.ancho, n.alto,
        args.banda[0], args.banda[1], args.umbral_borde, args.area_min)
    with open(args.salida_mascara, "w") as f:
        f.write(pgm.formatear_pgm(n._replace(maxval=255, pixeles=etiquetada)))
    mayor = segmentacion.region_mayor(regiones)
    if mayor.es_vacio():
        print("SIN_REGION")
    else:
        print(f"REGIONES {len(regiones)}")
        for r in regiones:
            print(f"REGION {r.etiqueta} {r.area} {r.x_min} {r.y_min} {r.x_max} {r.y_max} {r.cx} {r.cy}")
    return 0


def main(argv):
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
