
**UNIVERSIDAD SERGIO ARBOLEDA**  
Escuela de Ciencias Exactas e Ingeniería  
Ingeniería en Ciencias de la Computación e Inteligencia Artificial (ICCIA)  

# Informe de Avance Técnico y Demostración Formal Big O

Entrega Parcial (Sesión 3) - Entregable 3  

Paradigmas de Programación (SIST0176) - Semestre III  
**Grupo 4:** Segmentación y Procesamiento de Imágenes Médicas por Visión Artificial  

Integrantes: Juan Manuel Cuervo, Juan Nicolas Buitrago, David Santiago Sanchez, Santiago Vasquez Ochica  
Fecha: noviembre de 2026  


## 1. Estado de avance

| Módulo / actividad | Estado | Evidencia |
|---|---|---|
| Módulo 1 - Kernel imperativo C++17 | Terminado: convolución 2D (Gauss 5x5, Sobel 3x3), Loop Tiling 32x32, OpenMP collapse(2) | cpp/convolucion.cpp, build/convolve |
| Módulo 3 - Pipeline funcional Python | Terminado: normalización currificada, expansión por capas sin recursión de cola, mónada Option completa | funcional/, 12 pruebas unitarias OK |
| Módulo 2 - POO Java 17 | Terminado e integrado: dominio inmutable, Factory Method, Template Method, DIP, lote concurrente | java/src, 18 pruebas OK |
| Integración Java -> Python -> C++ -> Python | Funcionando de punta a punta con datos sintéticos | make demo |
| Pruebas de inmutabilidad y aliasing | Hechas (7 pruebas de copias defensivas e inmodificabilidad) | tac.pruebas.PruebasTac |
| Benchmarks Secuencial vs Paralelo | Programa listo y medido | cpp/bench.cpp, docs/benchmarks.md |


## 2. Notación y supuestos formales

**W** = ancho, **H** = alto (en píxeles), **N = W·H** (total de píxeles), **K** = lado del kernel impar, **r = piso(K/2)**, **B = 32** (lado del bloque de *Loop Tiling*), **p** = número de hilos OpenMP, **M** = cantidad de píxeles activos en la máscara binaria (M ≤ W·H), **nr** = píxeles de la r-ésima región conexa. Cada operación aritmética elemental, comparación o acceso a memoria tiene costo acotado por una constante positiva **c**.


## 3. Demostración formal - Módulo 1 (C++17 + OpenMP con Loop Tiling)


### 3.1 Complejidad temporal de la convolución con Loop Tiling

El dominio 2D de dimensiones H × W se particiona en bloques (*tiles*) de tamaño B × B (con B = 32). La cantidad de bloques horizontales es techo(W/B) y verticales es techo(H/B). Dentro de cada bloque (ty, tx), cada coordenada (y, x) válida se visita exactamente una vez y evalúa el producto interno con el kernel K × K:

`out(y, x) = Σky=0K-1 Σkx=0K-1 kw(ky, kx) · pad(y + ky, x + kx)`

Sumando el costo elemental c sobre todos los bloques (ty, tx) y sus píxeles internos:

`Tconv(W, H, K) = Σty Σtx Σy=tymin(ty+B,H)-1 Σx=txmin(tx+B,W)-1 Σky=0K-1 Σkx=0K-1 c = c · W · H · K²`

Por definición de orden asintótico ajustado, existen constantes positivas c₁ = c₂ = c y n₀ = 1 tales que c₁·W·H·K² ≤ Tconv(W, H, K) ≤ c₂·W·H·K² para todo W, H, K ≥ 1. Por tanto, **Tconv(W, H, K) ∈ Θ(W·H·K²)**.

**Costo del padding paralelo.** El arreglo con bordes replicados tiene dimensiones (W + K - 1)(H + K - 1) = W·H + (K-1)(W + H) + (K-1)². Dado que K ≤ min(W, H), se cumple (K-1)(W + H) ≤ 2·W·H·K y (K-1)² ≤ W·H. En consecuencia, Tpad ∈ Θ(W·H) ⊂ O(W·H·K²), por lo que el tiempo secuencial total es **Ttotal(W, H, K) ∈ Θ(W·H·K²)**.


### 3.2 Complejidad espacial y modelo de fallos de caché (Loop Tiling)

`S(W, H, K) = (W + K - 1)(H + K - 1) [pad] + W·H [salida] + K² [kernel] = Θ(W·H)`

**Optimización de caché por Loop Tiling (Cache Blocking).** En un recorrido ingenuo por filas completas, cuando W es grande (por ejemplo W = 1024 o 2048), las K filas necesarias para la ventana deslizante exceden la capacidad de la caché L1 de datos (32 KB), provocando desalojos antes de reutilizar las filas inferiores en y + 1 (complejidad de fallos de caché Q ≈ O(W·H·K / L), donde L es el tamaño de línea de caché). Al aplicar *Loop Tiling* con TILE_SIZE = B = 32, cada bloque de salida (32 × 32 × 4 B = 4 KB) junto con su vecindad en pad ((32 + K - 1)² × 4 B ≈ 5.1 KB para K = 5) y el kernel (100 B) ocupan en total ~9.2 KB, cabiendo holgadamente en la caché L1 (32 KB). Así, cada elemento cargado a L1 se reutiliza las K² veces sin desalojo, reduciendo los fallos de caché al óptimo asintótico **Q(W, H) ∈ Θ(W·H / L)**.


### 3.3 Detección de bordes y versión paralela con OpenMP collapse(2)

`Tbordes(W, H) = c · W·H · (5² + 3² + 3²) + c' · W·H = 43c · W·H + c' · W·H ∈ Θ(W·H)`

Con directiva #pragma omp parallel for collapse(2) schedule(static), los techo(H/B)·techo(W/B) bloques independientes se reparten equitativamente entre los p hilos sin condiciones de carrera (conjuntos de escritura disjuntos por bloque y ausencia de bloqueos mutuos):

`Tp(W, H, K) = Θ(W·H·K² / p)   para p ≤ techo(H/B)·techo(W/B)`

| Kernel | f (secuencial) | p = 2 | p = 4 | p = 8 |
|---|---|---|---|---|
| K = 3 | 10.0% | 1.82x | 3.08x | 4.71x |
| K = 5 | 3.8% | 1.93x | 3.59x | 6.30x |
| K = 9 | 1.2% | 1.98x | 3.86x | 7.37x |


## 4. Demostración formal - Módulo 3 (Python Funcional Puro)

| Función | Tiempo | Espacio (Heap) | Espacio (Pila) | Justificación matemática |
|---|---|---|---|---|
| normalizar (map + ventana currificada) | Θ(W·H) | Θ(W·H) | Θ(1) | ventana() ejecuta operaciones aritméticas O(1) aplicadas W·H veces. |
| mascara (map sobre 2 tuplas) | Θ(W·H) | Θ(W·H) | Θ(1) | Evalúa predicados currificados en_banda y menor_que en O(1) por píxel. |
| componentes (expansión funcional por capas) | O(W·H + M²) | O(M) | Θ(1) | Sin recursión de cola: expande capas con frozenset en espacio de pila constante. |
| estadisticas_opt (Option + sorted + reduce) | Θ(nr log nr) | Θ(nr) | Θ(1) | Encadena Some.filter.map con ordenamiento y reducción lineal. |
| region_mayor (reduce + Option.fold) | Θ(R) | Θ(1) | Θ(1) | Reducción sobre R regiones conexas usando fold monádico. |
| segmentar_opt / segmentar (pipeline total) | O(W·H + M²) | Θ(W·H) | Θ(1) | Composición monádica total libre de RecursionError. |


### 4.1 Demostración de componentes() y eliminación del desbordamiento de pila

**Complejidad de Pila Θ(1).** Python no implementa optimización de llamadas de cola (TCO), por lo que la recursión de cola nativa consume Θ(nr) marcos de pila y lanza RecursionError cuando nr supera sys.getrecursionlimit() (1000). Nuestra implementación reemplaza la recursión por expansión funcional iterativa de capas de frontera (_capa_siguiente) sobre conjuntos inmutables frozenset. Como no hay llamadas recursivas anidadas, el espacio en la pila de ejecución es estrictamente constante: **Sstack(W, H) ∈ Θ(1)**.

**Complejidad Temporal.** Sea M el número de píxeles con valor 1 en la máscara (M ≤ W·H). Para la r-ésima región con nr píxeles y dr capas de expansión en anchura (dr ≤ nr), la función pura _capa_siguiente inspecciona exactamente 4 vecinos por cada píxel de la frontera actual. Como cada píxel pertenece a una única capa de frontera, el número total de consultas de adyacencia en la región es 4·nr = Θ(nr). La unión inmutable region = region | frontera copia el conjunto acumulado de tamaño a lo sumo nr en cada una de las dr capas:

`Tregión(nr) = Σk=1dr O(|regionk| + 4·|fronterak|) ≤ c · dr · nr ≤ c · nr² ∈ O(nr²)`

Sumando sobre todas las R regiones disjuntas (donde Σr=1R nr = M), por convexidad de la función cuadrática se cumple Σr=1R nr² ≤ (Σ nr)² = M². Añadiendo el filtrado inicial Θ(W·H), se demuestra formalmente que **Tseg(W, H, M) ∈ O(W·H + M²)** y el espacio en el Heap es **Sheap(W, H) ∈ Θ(W·H)**.


## 5. Demostración formal - Módulo 2 (Java 17 POO e Integración)

| Operación | Tiempo | Espacio | Demostración |
|---|---|---|---|
| EstudioMedico (constructor) y getPixeles() | Θ(W·H) | Θ(W·H) | pixeles.clone() duplica exactamente N = W·H enteros contiguos para impedir aliasing. |
| FormatoPGM.leer / escribir | Θ(W·H) | Θ(W·H) | Procesa secuencialmente N tokens enteros. |
| ResultadoAnalisis (record compacto) | Θ(W·H + R) | Θ(W·H + R) | Clona bordes[N], mascara[N] y ejecuta List.copyOf sobre R regiones (R << N). |
| AnalizadorBase.analizar (Template Method) | Θ(W·H·K²) + O(M²) | Θ(W·H) | Suma secuencial de normalización Θ(N), convolución Θ(N·K²) y segmentación O(N + M²). |
| ServicioDiagnostico.analizarLote (p hilos) | Θ((L/p)·Testudio) | Θ(p·W·H) | Pool fijo de p hilos procesando L estudios independientes con estado inmutable. |

