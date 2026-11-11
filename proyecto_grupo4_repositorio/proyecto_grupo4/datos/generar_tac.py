"""Genera tomografias sinteticas (256x256, 12 bits) en formato PGM P2.

No son imagenes de pacientes reales: es un 'fantoma' con craneo, cerebro,
ventriculos y (opcionalmente) tumores, mas ruido y un leve desenfoque.
Uso: python3 datos/generar_tac.py
"""
import math
import random

N = 256
MAXVAL = 4095
AIRE, CEREBRO, VENTRICULO, TUMOR, CRANEO = 0, 1100, 400, 1750, 3200


def dentro_elipse(x, y, cx, cy, a, b):
    return ((x - cx) / a) ** 2 + ((y - cy) / b) ** 2 <= 1.0


def fantoma(tumores):
    img = [[AIRE] * N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            if dentro_elipse(x, y, 128, 128, 100, 115):
                v = CRANEO
                if dentro_elipse(x, y, 128, 128, 92, 107):
                    v = CEREBRO
                    if dentro_elipse(x, y, 118, 120, 10, 22) or dentro_elipse(x, y, 140, 120, 10, 22):
                        v = VENTRICULO
                    for (tx, ty, r) in tumores:
                        if (x - tx) ** 2 + (y - ty) ** 2 <= r * r:
                            v = TUMOR
                img[y][x] = v
    return img


def desenfocar(img):
    k = [1, 2, 1]
    out = [[0] * N for _ in range(N)]
    for y in range(N):
        for x in range(N):
            s = 0
            for j in range(3):
                for i in range(3):
                    yy = min(max(y + j - 1, 0), N - 1)
                    xx = min(max(x + i - 1, 0), N - 1)
                    s += img[yy][xx] * k[i] * k[j]
            out[y][x] = s / 16.0
    return out


def con_ruido(img, semilla, sigma=35.0):
    rnd = random.Random(semilla)
    return [[min(MAXVAL, max(0, int(round(v + rnd.gauss(0, sigma))))) for v in fila] for fila in img]


def guardar(nombre, img):
    with open(nombre, "w") as f:
        f.write("# TAC sintetica (fantoma) generada por generar_tac.py\n")
        f.write(f"P2\n{N} {N}\n{MAXVAL}\n")
        for fila in img:
            f.write(" ".join(map(str, fila)) + "\n")


CASOS = {
    "tac_01": ([(100, 108, 13), (165, 150, 8)], 1),     # dos tumores
    "tac_02": ([(120, 160, 12), (132, 170, 9)], 2),     # un tumor irregular (dos circulos unidos)
    "tac_03": ([], 3),                                  # estudio sano
}

if __name__ == "__main__":
    for nombre, (tumores, semilla) in CASOS.items():
        guardar(f"datos/{nombre}.pgm", con_ruido(desenfocar(fantoma(tumores)), semilla))
        print("generado", nombre)
