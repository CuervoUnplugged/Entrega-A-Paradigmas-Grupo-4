import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pgm
import pixeles
import segmentacion
from option import NOTHING, Some


class PruebasOption(unittest.TestCase):
    def test_some_map_y_flat_map(self):
        self.assertEqual(Some(2).map(lambda x: x * 3), Some(6))
        self.assertEqual(Some(2).flat_map(lambda x: Some(x + 1)), Some(3))

    def test_nothing_ignora_las_funciones(self):
        self.assertTrue(NOTHING.map(lambda x: x / 0).es_vacio())
        self.assertEqual(NOTHING.get_or_else(7), 7)


class PruebasPureza(unittest.TestCase):
    def test_normalizar_no_modifica_la_entrada_y_es_determinista(self):
        entrada = (0, 500, 1700, 2900, 4095)
        copia = tuple(entrada)
        a = pixeles.normalizar(entrada, 1700, 2400)
        b = pixeles.normalizar(entrada, 1700, 2400)
        self.assertEqual(entrada, copia)
        self.assertEqual(a, b)
        self.assertEqual(a, (0, 0, 127, 255, 255))

    def test_currificacion(self):
        f = pixeles.ventana(1700)(2400)
        self.assertEqual(f(1700), pixeles.ventana(1700, 2400, 1700))
        self.assertEqual(pixeles.ventana(1700, 2400)(2900), 255)

    def test_compose(self):
        doble_mas_uno = pixeles.compose(lambda x: x + 1, lambda x: x * 2)
        self.assertEqual(doble_mas_uno(5), 11)

    def test_mascara_excluye_bordes_fuertes(self):
        norm = (120, 120, 120, 50)
        bordes = (5, 50, 5, 5)
        self.assertEqual(pixeles.mascara(norm, bordes, 100, 170, 30), (1, 0, 1, 0))


class PruebasSegmentacion(unittest.TestCase):
    def test_dos_componentes(self):
        # 5x3:  1 1 0 0 1
        #       1 0 0 0 1
        #       0 0 0 0 1
        m = (1, 1, 0, 0, 1,
             1, 0, 0, 0, 1,
             0, 0, 0, 0, 1)
        regiones = segmentacion.componentes(m, 5, 3)
        self.assertEqual(sorted(len(r) for r in regiones), [3, 3])

    def test_recursion_de_cola_no_desborda_la_pila(self):
        # Una "linea" de 20000 pixeles requeriria 20000 llamadas recursivas anidadas.
        n = 20000
        m = (1,) * n
        region = segmentacion.crecer_region(m, n, 1, 0)
        self.assertEqual(len(region), n)
        self.assertGreater(n, sys.getrecursionlimit())

    def test_region_mayor_con_option(self):
        self.assertTrue(segmentacion.region_mayor(()).es_vacio())
        r1 = segmentacion.Region(1, 10, 0, 0, 1, 1, 0.5, 0.5)
        r2 = segmentacion.Region(2, 30, 0, 0, 1, 1, 0.5, 0.5)
        self.assertEqual(segmentacion.region_mayor((r1, r2)), Some(r2))

    def test_segmentar_es_pura(self):
        norm = (120,) * 9 + (0,) * 7
        bordes = (0,) * 16
        a = segmentacion.segmentar(norm, bordes, 4, 4, 100, 170, 30, 2)
        b = segmentacion.segmentar(norm, bordes, 4, 4, 100, 170, 30, 2)
        self.assertEqual(a, b)
        self.assertEqual(a[0][0].area, 9)


class PruebasPGM(unittest.TestCase):
    def test_ida_y_vuelta(self):
        img = pgm.Imagen(2, 2, 255, (1, 2, 3, 4))
        self.assertEqual(pgm.parsear_pgm(pgm.formatear_pgm(img)), Some(img))

    def test_invalido_da_nothing(self):
        self.assertTrue(pgm.parsear_pgm("P5 1 1 255").es_vacio())
        self.assertTrue(pgm.parsear_pgm("P2\n2 2\n255\n1 2 3").es_vacio())


if __name__ == "__main__":
    unittest.main()
