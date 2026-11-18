
**UNIVERSIDAD SERGIO ARBOLEDA**  
Escuela de Ciencias Exactas e Ingeniería  
Ingeniería en Ciencias de la Computación e Inteligencia Artificial (ICCIA)  

# Informe Técnico Final de Ingeniería

Entrega Final y Sustentación (Sesión 5)  

Paradigmas de Programación (SIST0176) - Semestre III  
**Grupo 4:** Segmentación y Procesamiento de Imágenes Médicas por Visión Artificial  

Integrantes: Juan Manuel Cuervo, Juan Nicolas Buitrago, David Santiago Sanchez, Santiago Vasquez Ochica  
Fecha: noviembre de 2026  


## 1. Resumen

Se desarrolló un sistema multiparadigma para procesar tomografías: un kernel imperativo en **C++17 con OpenMP y Loop Tiling (32×32)** calcula bordes por convolución 2D maximizando la localidad espacial y temporal de la caché L1; un dominio **orientado a objetos en Java 17** (Factory Method, Template Method, DIP, inmutabilidad) orquesta el análisis; y un pipeline **funcional en Python** normaliza intensidades y segmenta regiones mediante expansión funcional por capas (en espacio de pila O(1), sin recursión de cola) y composición monádica con **Option/Maybe**. El sistema detecta correctamente los tumores sintéticos de los tres estudios de prueba y pasa 30 pruebas automáticas (12 Python, 18 Java). La versión paralela produce resultados idénticos a la secuencial.


## 2. Caso de estudio y requerimientos

| Requerimiento de la especificación (Grupo 4) | Implementación | Dónde |
|---|---|---|
| Kernel de convolución Θ(W·H·K²), Loop Tiling y OpenMP | convolucionar(): padding contiguo, bloques TILE_SIZE=32, #pragma omp parallel for collapse(2) | cpp/convolucion.cpp |
| Factory Method y Template Method para analizadores médicos | FabricaAnalizador (Creator), AnalizadorBase (Template Method) y fábricas Tumoral / Óseo | java/src/tac/analisis |
| Copias defensivas en EstudioMedico y ResultadoAnalisis | clone() al entrar y al salir; List.copyOf() para regiones inmodificables | dominio/EstudioMedico.java |
| Inversión de dependencias con RepositorioImagen | Interfaz RepositorioImagen; ServicioDiagnostico depende solo de abstracciones | repositorio/, analisis/ServicioDiagnostico.java |
| Mapeo puro de intensidad de píxeles | ventana() currificada + map | funcional/pixeles.py |
| Segmentación sin desbordamiento de pila (O(1) stack) | crecer_region / componentes por capas de frontera con frozenset | funcional/segmentacion.py |
| Mónada Option / Maybe (Some / Nothing) | map, flat_map, filter, fold, get_or_else en parsear_pgm, estadisticas_opt, segmentar_opt y cli.py | funcional/option.py, segmentacion.py, cli.py |
| Functional Core, Imperative Shell; benchmarks; thread safety | cli.py como única capa con E/S; make bench; pruebas concurrentes | funcional/cli.py, cpp/bench.cpp, PruebasTac |


## 3. Implementación por paradigma


### 3.1 Imperativo - C++17, Loop Tiling y OpenMP

- **Memoria contigua:** imagen y buffers en std::vector<float> en el Heap sin fugas por RAII; punteros nativos en el núcleo de cómputo.
- **Loop Tiling (Cache Blocking 32×32):** particiona la iteración en bloques de 32×32 píxeles (~9.2 KB con vecindad y kernel), garantizando que los datos residan en la caché L1 de 32 KB durante todas las pasadas del filtro K×K.
- **Paralelismo:** #pragma omp parallel for collapse(2) schedule(static) reparte los bloques 2D entre hilos sin condiciones de carrera.


### 3.2 Orientado a objetos - Java 17

- **Inmutabilidad y aliasing:** 7 pruebas verifican copias defensivas de entrada y salida e inmodificabilidad de colecciones.
- **Thread safety:** servicio sin estado mutable, archivos temporales únicos por proceso e implementación concurrente con ConcurrentHashMap.


### 3.3 Funcional - Python 3.10+

- **Pureza y transparencia referencial:** funciones puras sobre tuplas y frozensets inmutables.
- **Eliminación de recursión de cola:** dado que Python no soporta TCO nativo, la exploración de componentes conexas se realiza por capas de frontera inmutables en espacio de pila constante Θ(1).
- **Mónada Option completa:** encadenamiento declarativo con map, flat_map, filter y fold sin usar excepciones ni None.


## 4. Resultados de segmentación

| Estudio | Verdad (fantoma) | Área real | Área detectada | Detectado/real | Centroide detectado |
|---|---|---|---|---|---|
| tac_01 | 2 tumores (r=13 en (100,108); r=8 en (165,150)) | 529 px y 197 px | 421 px y 140 px | 80% y 71% | (99.6, 107.9) y (165.0, 150.0) |
| tac_02 | 1 tumor irregular (dos círculos unidos) | 646 px | 536 px | 83% | (124.1, 163.5) |
| tac_03 | Sano (sin tumor) | 0 | Sin regiones (Option = Nothing) | - | - |

![Figura 2. Resultados: original, bordes (C++), máscara etiquetada (Python) y superposición.](figuras/resultados.png)

*Figura 2. Resultados: original, bordes (C++), máscara etiquetada (Python) y superposición.*


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


## 6. Benchmarks de paralelismo (Secuencial vs Paralelo)

Método: kernel de caja K×K sobre imagen aleatoria con Loop Tiling 32×32; mejor de 3 ejecuciones; igualdad bit a bit comprobada. **Hilos máximos de OpenMP en el entorno = 1**.

| Tamaño | K | Hilos | T seq (ms) | T par (ms) | Speedup | Eficiencia | Resultado igual |
|---|---|---|---|---|---|---|---|
| 512x512 | 3 | 2 | 1.5 | 1.4 | 1.04x | 52% | si |
| 512x512 | 3 | 4 | 1.5 | 1.6 | 0.92x | 23% | si |
| 512x512 | 5 | 2 | 4.1 | 3.8 | 1.10x | 55% | si |
| 512x512 | 5 | 4 | 4.1 | 3.7 | 1.11x | 28% | si |
| 512x512 | 9 | 2 | 10.0 | 10.4 | 0.96x | 48% | si |
| 512x512 | 9 | 4 | 10.0 | 10.0 | 1.00x | 25% | si |
| 1024x1024 | 3 | 2 | 6.1 | 5.6 | 1.09x | 54% | si |
| 1024x1024 | 3 | 4 | 6.1 | 5.5 | 1.11x | 28% | si |
| 1024x1024 | 5 | 2 | 14.7 | 15.3 | 0.96x | 48% | si |
| 1024x1024 | 5 | 4 | 14.7 | 15.0 | 0.98x | 25% | si |
| 1024x1024 | 9 | 2 | 41.7 | 43.5 | 0.96x | 48% | si |
| 1024x1024 | 9 | 4 | 41.7 | 44.4 | 0.94x | 23% | si |
| 2048x2048 | 3 | 2 | 30.2 | 23.6 | 1.28x | 64% | si |
| 2048x2048 | 3 | 4 | 30.2 | 23.8 | 1.27x | 32% | si |
| 2048x2048 | 5 | 2 | 61.9 | 62.6 | 0.99x | 49% | si |
| 2048x2048 | 5 | 4 | 61.9 | 61.5 | 1.01x | 25% | si |
| 2048x2048 | 9 | 2 | 160.9 | 161.2 | 1.00x | 50% | si |
| 2048x2048 | 9 | 4 | 160.9 | 163.7 | 0.98x | 25% | si |


## 7. Pruebas y validación

| Suite | Pruebas | Qué cubre |
|---|---|---|
| Python (unittest) | 12 | Mónada Option (map, flat_map, filter, fold), pureza, currificación, compose, máscara, componentes sin recursión de cola (20 000 píxeles en pila O(1)), PGM |
| Java (PruebasTac) | 18 | Aliasing, inmodificabilidad, Factory Method, integración real de 3 módulos, DIP con falsos, lote concurrente, estrés, propagación de errores |
| C++ (bench) | - | Igualdad bit a bit secuencial vs paralelo con Loop Tiling en cada configuración |

