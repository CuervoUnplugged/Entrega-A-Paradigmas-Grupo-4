"""Genera los PDF/Markdown de las entregas. Ejecutar desde la raiz del proyecto:
    python3 docs/herramientas/generar_documentos.py
Requiere: reportlab, matplotlib, pillow. Lee docs/benchmarks.md (resultado de `make bench`)."""
import os
import shutil
import sys

sys.path.insert(0, os.path.dirname(__file__))
from reportgen import generar  # noqa: E402

RAIZ = os.getcwd()
DOCS = os.path.join(RAIZ, "docs")
os.makedirs(f"{DOCS}/Entrega_Parcial", exist_ok=True)
os.makedirs(f"{DOCS}/Entrega_Final", exist_ok=True)

ENC = "Universidad Sergio Arboleda | ICCIA | SIST0176 Paradigmas de Programación | Proyecto Final - Grupo 4"


def portada(titulo, subtitulo):
    return [
        ("space", 0.6),
        ("sub", "<b>UNIVERSIDAD SERGIO ARBOLEDA</b>"),
        ("sub", "Escuela de Ciencias Exactas e Ingeniería"),
        ("sub", "Ingeniería en Ciencias de la Computación e Inteligencia Artificial (ICCIA)"),
        ("space", 0.5),
        ("title", titulo),
        ("sub", subtitulo),
        ("space", 0.3),
        ("sub", "Paradigmas de Programación (SIST0176) - Semestre III"),
        ("sub", "<b>Grupo 4:</b> Segmentación y Procesamiento de Imágenes Médicas por Visión Artificial"),
        ("space", 0.2),
        ("sub", "Integrantes: Juan Manuel Cuervo, Juan Nicolas Buitrago, David Santiago Sanchez, Santiago Vasquez Ochica"),
        ("sub", "Fecha: noviembre de 2026"),
        ("space", 0.4),
    ]


# ---------- datos medidos ----------
def leer_benchmarks():
    filas, hilos = [], "?"
    with open(f"{DOCS}/benchmarks.md", encoding="utf-8") as f:
        for linea in f:
            if linea.startswith("Hilos maximos"):
                hilos = linea.split(":")[1].strip()
            elif linea.startswith("|") and not linea.startswith("|---") and "Tamano" not in linea:
                filas.append([c.strip() for c in linea.strip().strip("|").split("|")])
    return hilos, filas


def area_real(circulos):
    pts = set()
    for (cx, cy, r) in circulos:
        for y in range(256):
            for x in range(256):
                if (x - cx) ** 2 + (y - cy) ** 2 <= r * r:
                    pts.add((x, y))
    return len(pts)


def amdahl(k, p):
    f = 1.0 / (1 + k * k)  # fraccion secuencial frente a K^2 unidades (MAC)
    return 1.0 / (f + (1 - f) / p)


HILOS_BENCH, FILAS_BENCH = leer_benchmarks()
TABLA_BENCH = FILAS_BENCH
GT1a, GT1b = area_real([(100, 108, 13)]), area_real([(165, 150, 8)])
GT2 = area_real([(120, 160, 12), (132, 170, 9)])
TABLA_AMDAHL = [[f"K = {k}", f"{1/(1+k*k)*100:.1f}%"] + [f"{amdahl(k, p):.2f}x" for p in (2, 4, 8)] for k in (3, 5, 9)]

# =====================================================================================
# BLOQUES DE DEMOSTRACIÓN FORMAL BIG O (Compartidos en Avance, Final y Raíz)
# =====================================================================================
BLOQUES_BIG_O = [
    ("h1", "2. Notación y supuestos formales"),
    ("p", "<b>W</b> = ancho, <b>H</b> = alto (en píxeles), <b>N = W·H</b> (total de píxeles), <b>K</b> = lado del kernel impar, "
          "<b>r = piso(K/2)</b>, <b>B = 32</b> (lado del bloque de <i>Loop Tiling</i>), <b>p</b> = número de hilos OpenMP, "
          "<b>M</b> = cantidad de píxeles activos en la máscara binaria (M ≤ W·H), <b>n<sub>r</sub></b> = píxeles de la r-ésima región conexa. "
          "Cada operación aritmética elemental, comparación o acceso a memoria tiene costo acotado por una constante positiva <b>c</b>."),
    ("h1", "3. Demostración formal - Módulo 1 (C++17 + OpenMP con Loop Tiling)"),
    ("h2", "3.1 Complejidad temporal de la convolución con Loop Tiling"),
    ("p", "El dominio 2D de dimensiones H × W se particiona en bloques (<i>tiles</i>) de tamaño B × B (con B = 32). "
          "La cantidad de bloques horizontales es techo(W/B) y verticales es techo(H/B). Dentro de cada bloque (ty, tx), "
          "cada coordenada (y, x) válida se visita exactamente una vez y evalúa el producto interno con el kernel K × K:"),
    ("formula", "out(y, x) = Σ<sub>ky=0</sub><super>K-1</super> Σ<sub>kx=0</sub><super>K-1</super> kw(ky, kx) · pad(y + ky, x + kx)"),
    ("p", "Sumando el costo elemental c sobre todos los bloques (ty, tx) y sus píxeles internos:"),
    ("formula", "T<sub>conv</sub>(W, H, K) = Σ<sub>ty</sub> Σ<sub>tx</sub> Σ<sub>y=ty</sub><super>min(ty+B,H)-1</super> Σ<sub>x=tx</sub><super>min(tx+B,W)-1</super> Σ<sub>ky=0</sub><super>K-1</super> Σ<sub>kx=0</sub><super>K-1</super> c = c · W · H · K²"),
    ("p", "Por definición de orden asintótico ajustado, existen constantes positivas c₁ = c₂ = c y n₀ = 1 tales que "
          "c₁·W·H·K² ≤ T<sub>conv</sub>(W, H, K) ≤ c₂·W·H·K² para todo W, H, K ≥ 1. Por tanto, <b>T<sub>conv</sub>(W, H, K) ∈ Θ(W·H·K²)</b>."),
    ("p", "<b>Costo del padding paralelo.</b> El arreglo con bordes replicados tiene dimensiones (W + K - 1)(H + K - 1) = W·H + (K-1)(W + H) + (K-1)². "
          "Dado que K ≤ min(W, H), se cumple (K-1)(W + H) ≤ 2·W·H·K y (K-1)² ≤ W·H. En consecuencia, T<sub>pad</sub> ∈ Θ(W·H) ⊂ O(W·H·K²), "
          "por lo que el tiempo secuencial total es <b>T<sub>total</sub>(W, H, K) ∈ Θ(W·H·K²)</b>."),
    ("h2", "3.2 Complejidad espacial y modelo de fallos de caché (Loop Tiling)"),
    ("formula", "S(W, H, K) = (W + K - 1)(H + K - 1) [pad] + W·H [salida] + K² [kernel] = Θ(W·H)"),
    ("p", "<b>Optimización de caché por Loop Tiling (Cache Blocking).</b> En un recorrido ingenuo por filas completas, cuando W es grande "
          "(por ejemplo W = 1024 o 2048), las K filas necesarias para la ventana deslizante exceden la capacidad de la caché L1 de datos (32 KB), "
          "provocando desalojos antes de reutilizar las filas inferiores en y + 1 (complejidad de fallos de caché Q ≈ O(W·H·K / L), donde L es el tamaño de línea de caché). "
          "Al aplicar <i>Loop Tiling</i> con TILE_SIZE = B = 32, cada bloque de salida (32 × 32 × 4 B = 4 KB) junto con su vecindad en pad "
          "((32 + K - 1)² × 4 B ≈ 5.1 KB para K = 5) y el kernel (100 B) ocupan en total ~9.2 KB, cabiendo holgadamente en la caché L1 (32 KB). "
          "Así, cada elemento cargado a L1 se reutiliza las K² veces sin desalojo, reduciendo los fallos de caché al óptimo asintótico <b>Q(W, H) ∈ Θ(W·H / L)</b>."),
    ("h2", "3.3 Detección de bordes y versión paralela con OpenMP collapse(2)"),
    ("formula", "T<sub>bordes</sub>(W, H) = c · W·H · (5² + 3² + 3²) + c' · W·H = 43c · W·H + c' · W·H ∈ Θ(W·H)"),
    ("p", "Con directiva <font face='DV-M'>#pragma omp parallel for collapse(2) schedule(static)</font>, los techo(H/B)·techo(W/B) bloques independientes "
          "se reparten equitativamente entre los p hilos sin condiciones de carrera (conjuntos de escritura disjuntos por bloque y ausencia de bloqueos mutuos):"),
    ("formula", "T<sub>p</sub>(W, H, K) = Θ(W·H·K² / p)   para p ≤ techo(H/B)·techo(W/B)"),
    ("table", ["Kernel", "f (secuencial)", "p = 2", "p = 4", "p = 8"], TABLA_AMDAHL, [0.2, 0.2, 0.2, 0.2, 0.2]),
    ("h1", "4. Demostración formal - Módulo 3 (Python Funcional Puro)"),
    ("table", ["Función", "Tiempo", "Espacio (Heap)", "Espacio (Pila)", "Justificación matemática"], [
        ["normalizar (map + ventana currificada)", "Θ(W·H)", "Θ(W·H)", "Θ(1)", "ventana() ejecuta operaciones aritméticas O(1) aplicadas W·H veces."],
        ["mascara (map sobre 2 tuplas)", "Θ(W·H)", "Θ(W·H)", "Θ(1)", "Evalúa predicados currificados en_banda y menor_que en O(1) por píxel."],
        ["componentes (expansión funcional por capas)", "O(W·H + M²)", "O(M)", "Θ(1)", "Sin recursión de cola: expande capas con frozenset en espacio de pila constante."],
        ["estadisticas_opt (Option + sorted + reduce)", "Θ(n<sub>r</sub> log n<sub>r</sub>)", "Θ(n<sub>r</sub>)", "Θ(1)", "Encadena Some.filter.map con ordenamiento y reducción lineal."],
        ["region_mayor (reduce + Option.fold)", "Θ(R)", "Θ(1)", "Θ(1)", "Reducción sobre R regiones conexas usando fold monádico."],
        ["segmentar_opt / segmentar (pipeline total)", "O(W·H + M²)", "Θ(W·H)", "Θ(1)", "Composición monádica total libre de RecursionError."],
    ], [0.26, 0.14, 0.13, 0.11, 0.36]),
    ("h2", "4.1 Demostración de componentes() y eliminación del desbordamiento de pila"),
    ("p", "<b>Complejidad de Pila Θ(1).</b> Python no implementa optimización de llamadas de cola (TCO), por lo que la recursión de cola nativa consume "
          "Θ(n<sub>r</sub>) marcos de pila y lanza <font face='DV-M'>RecursionError</font> cuando n<sub>r</sub> supera <font face='DV-M'>sys.getrecursionlimit()</font> (1000). "
          "Nuestra implementación reemplaza la recursión por expansión funcional iterativa de capas de frontera (<font face='DV-M'>_capa_siguiente</font>) sobre "
          "conjuntos inmutables <font face='DV-M'>frozenset</font>. Como no hay llamadas recursivas anidadas, el espacio en la pila de ejecución es estrictamente constante: <b>S<sub>stack</sub>(W, H) ∈ Θ(1)</b>."),
    ("p", "<b>Complejidad Temporal.</b> Sea M el número de píxeles con valor 1 en la máscara (M ≤ W·H). Para la r-ésima región con n<sub>r</sub> píxeles y d<sub>r</sub> "
          "capas de expansión en anchura (d<sub>r</sub> ≤ n<sub>r</sub>), la función pura <font face='DV-M'>_capa_siguiente</font> inspecciona exactamente 4 vecinos por cada píxel "
          "de la frontera actual. Como cada píxel pertenece a una única capa de frontera, el número total de consultas de adyacencia en la región es 4·n<sub>r</sub> = Θ(n<sub>r</sub>). "
          "La unión inmutable <font face='DV-M'>region = region | frontera</font> copia el conjunto acumulado de tamaño a lo sumo n<sub>r</sub> en cada una de las d<sub>r</sub> capas:"),
    ("formula", "T<sub>región</sub>(n<sub>r</sub>) = Σ<sub>k=1</sub><super>d<sub>r</sub></super> O(|region<sub>k</sub>| + 4·|frontera<sub>k</sub>|) ≤ c · d<sub>r</sub> · n<sub>r</sub> ≤ c · n<sub>r</sub>² ∈ O(n<sub>r</sub>²)"),
    ("p", "Sumando sobre todas las R regiones disjuntas (donde Σ<sub>r=1</sub><super>R</super> n<sub>r</sub> = M), por convexidad de la función cuadrática se cumple "
          "Σ<sub>r=1</sub><super>R</super> n<sub>r</sub>² ≤ (Σ n<sub>r</sub>)² = M². Añadiendo el filtrado inicial Θ(W·H), se demuestra formalmente que "
          "<b>T<sub>seg</sub>(W, H, M) ∈ O(W·H + M²)</b> y el espacio en el Heap es <b>S<sub>heap</sub>(W, H) ∈ Θ(W·H)</b>."),
    ("h1", "5. Demostración formal - Módulo 2 (Java 17 POO e Integración)"),
    ("table", ["Operación", "Tiempo", "Espacio", "Demostración"], [
        ["EstudioMedico (constructor) y getPixeles()", "Θ(W·H)", "Θ(W·H)", "pixeles.clone() duplica exactamente N = W·H enteros contiguos para impedir aliasing."],
        ["FormatoPGM.leer / escribir", "Θ(W·H)", "Θ(W·H)", "Procesa secuencialmente N tokens enteros."],
        ["ResultadoAnalisis (record compacto)", "Θ(W·H + R)", "Θ(W·H + R)", "Clona bordes[N], mascara[N] y ejecuta List.copyOf sobre R regiones (R << N)."],
        ["AnalizadorBase.analizar (Template Method)", "Θ(W·H·K²) + O(M²)", "Θ(W·H)", "Suma secuencial de normalización Θ(N), convolución Θ(N·K²) y segmentación O(N + M²)."],
        ["ServicioDiagnostico.analizarLote (p hilos)", "Θ((L/p)·T<sub>estudio</sub>)", "Θ(p·W·H)", "Pool fijo de p hilos procesando L estudios independientes con estado inmutable."],
    ], [0.28, 0.18, 0.14, 0.40]),
]

# =====================================================================================
# 1. ENTREGA PARCIAL - DOCUMENTO DE ARQUITECTURA Y ESPECIFICACIÓN UML (PDF)
# =====================================================================================
b = portada("Documento de Arquitectura y Especificación UML", "Entrega Parcial (Sesión 3) - Entregable 1")
b += [
    ("h1", "1. Alcance y caso de estudio"),
    ("p", "<b>Problema (Grupo 4).</b> Un centro de diagnóstico necesita procesar tomografías (TAC) de alta resolución, aplicar "
          "filtros de convolución bidimensional para detectar bordes de tejidos y segmentar automáticamente regiones tumorales."),
    ("p", "<b>Solución multiparadigma.</b> Tres módulos conectados, cada uno en el paradigma y lenguaje exigidos por la especificación: "
          "Módulo 1 imperativo en C++17 con OpenMP y Loop Tiling (convolución por bloques de caché sobre memoria contigua), Módulo 2 orientado a objetos en Java 17 "
          "(modelo de dominio, Factory Method, Template Method, DIP, copias defensivas) y Módulo 3 funcional en Python 3.10+ (mapeo puro de intensidades, "
          "expansión funcional por capas sin recursión de cola y mónada Option/Maybe)."),
    ("pagebreak",),
    ("h1", "2. Notación usada"),
    ("table", ["Símbolo", "Significado"], [
        ["+  /  -  /  #  /  ~", "Visibilidad: público / privado / protegido / paquete"],
        ["Línea continua con triángulo hueco", "Generalización (herencia, <i>extends</i>)"],
        ["Línea discontinua con triángulo hueco", "Realización (<i>implements</i> de una interfaz)"],
        ["Línea con rombo hueco", "Agregación: el todo referencia a las partes, que viven por separado (inyección de dependencias)"],
        ["Línea con rombo relleno", "Composición: el todo es dueño de las partes y las destruye con él"],
        ["Flecha discontinua abierta", "Dependencia (usa, crea, lanza). Estereotipos &lt;&lt;use&gt;&gt;, &lt;&lt;create&gt;&gt;, &lt;&lt;throws&gt;&gt;"],
    ], [0.35, 0.65]),
    ("pagebreak",),
    ("h1", "3. Diagrama de clases UML - Módulo POO (Java 17)"),
    ("h2", "3.1 Dominio, repositorio y servicio"),
    ("img", "figuras/clases_dominio.png", 1.0, "Figura 1. Dominio, repositorio, servicio y excepciones (Generalización, Realización, Agregación, Composición, Dependencia)."),
    ("pagebreak",),
    ("h2", "3.2 Factory Method y Template Method (análisis)"),
    ("img", "figuras/clases_fabrica.png", 0.9, "Figura 2. Fábricas (Creator), analizadores (Product) y clase abstracta con método plantilla."),
    ("pagebreak",),
    ("h2", "3.3 Integración con los módulos C++ y Python"),
    ("img", "figuras/clases_integracion.png", 1.0, "Figura 3. Contratos (interfaces) y adaptadores hacia el kernel C++ y el pipeline funcional."),
    ("pagebreak",),
    ("h1", "4. Diagrama de flujo de datos e integración entre módulos"),
    ("img", "figuras/flujo_datos.png", 1.0, "Figura 4. Flujo de datos. Java orquesta; Python normaliza y segmenta; C++ calcula bordes."),
    ("p", "<b>Formato de intercambio.</b> Las imágenes viajan entre módulos como archivos PGM P2 (texto), que los tres lenguajes leen sin "
          "librerías externas. Java ejecuta los otros módulos como procesos y redirige su entrada/salida a archivos temporales únicos, "
          "lo que evita bloqueos por buffers y permite llamadas concurrentes seguras."),
    ("pagebreak",),
    ("h1", "5. Contratos de interfaz entre módulos"),
    ("table", ["Contrato", "Entrada", "Salida", "Quién lo implementa"], [
        ["NucleoConvolucion.detectarBordes", "ancho, alto, píxeles 8 bits", "Mapa de bordes 0..255", "NucleoConvolucionCpp (llama a build/convolve)"],
        ["PipelineFuncional.normalizar", "píxeles 12 bits, nivel, ancho de ventana", "Píxeles 8 bits", "PipelineFuncionalPython (cli.py normalizar)"],
        ["PipelineFuncional.segmentar", "imagen 8 bits, bordes, ParametrosSegmentacion", "ResultadoSegmentacion (regiones + máscara)", "PipelineFuncionalPython (cli.py segmentar)"],
        ["RepositorioImagen.cargar", "id de estudio", "EstudioMedico inmutable", "RepositorioImagenArchivo / RepositorioImagenEnMemoria"],
    ], [0.27, 0.25, 0.25, 0.23]),
    ("h1", "6. Justificación de diseño: SOLID y patrones GoF"),
    ("table", ["Principio / patrón", "Dónde se aplica", "Justificación"], [
        ["S - Responsabilidad única", "EstudioMedico, FormatoPGM, ProcesoExterno, ServicioDiagnostico", "Cada clase tiene un solo motivo de cambio: modelar un estudio, leer PGM, ejecutar procesos, orquestar el caso de uso."],
        ["O - Abierto/Cerrado", "FabricaAnalizador y AnalizadorBase", "Para un nuevo tipo de análisis (p. ej. vascular) se agrega una subclase de analizador y una de fábrica; no se modifica código existente."],
        ["L - Sustitución de Liskov", "AnalizadorTumoral / AnalizadorOseo", "Ambos pueden usarse donde se espera AnalizadorMedico: respetan el contrato y no endurecen precondiciones."],
        ["I - Segregación de interfaces", "NucleoConvolucion y PipelineFuncional", "Interfaces pequeñas y separadas, una por módulo externo."],
        ["D - Inversión de dependencias", "ServicioDiagnostico, AnalizadorBase", "Dependen de interfaces (RepositorioImagen, NucleoConvolucion, PipelineFuncional), no de C++/Python/archivos. Las pruebas usan falsos sin esos módulos."],
        ["GoF: Factory Method", "FabricaAnalizador.crearAnalizador()", "Las subclases deciden qué analizador instanciar; el servicio no conoce clases concretas."],
        ["GoF: Template Method", "AnalizadorBase.analizar() (final)", "Fija el flujo normalizar -> bordes -> segmentar; las subclases solo definen parametros()."],
        ["Inmutabilidad / copias defensivas", "EstudioMedico, records de resultados", "Se copia el arreglo al entrar y al salir; List.copyOf produce listas inmodificables: no hay aliasing."],
    ], [0.22, 0.30, 0.48]),
]
generar(b, f"{DOCS}/Entrega_Parcial/1_Arquitectura_UML.pdf", apaisado=True, encabezado=ENC, ruta_base=DOCS)
print("1_Arquitectura_UML.pdf ok")

# =====================================================================================
# 3. ENTREGA PARCIAL - INFORME DE AVANCE TÉCNICO Y ANÁLISIS BIG O FORMAL (PDF + MD)
# =====================================================================================
b = portada("Informe de Avance Técnico y Demostración Formal Big O", "Entrega Parcial (Sesión 3) - Entregable 3")
b += [
    ("h1", "1. Estado de avance"),
    ("table", ["Módulo / actividad", "Estado", "Evidencia"], [
        ["Módulo 1 - Kernel imperativo C++17", "Terminado: convolución 2D (Gauss 5x5, Sobel 3x3), Loop Tiling 32x32, OpenMP collapse(2)", "cpp/convolucion.cpp, build/convolve"],
        ["Módulo 3 - Pipeline funcional Python", "Terminado: normalización currificada, expansión por capas sin recursión de cola, mónada Option completa", "funcional/, 12 pruebas unitarias OK"],
        ["Módulo 2 - POO Java 17", "Terminado e integrado: dominio inmutable, Factory Method, Template Method, DIP, lote concurrente", "java/src, 18 pruebas OK"],
        ["Integración Java -> Python -> C++ -> Python", "Funcionando de punta a punta con datos sintéticos", "make demo"],
        ["Pruebas de inmutabilidad y aliasing", "Hechas (7 pruebas de copias defensivas e inmodificabilidad)", "tac.pruebas.PruebasTac"],
        ["Benchmarks Secuencial vs Paralelo", "Programa listo y medido", "cpp/bench.cpp, docs/benchmarks.md"],
    ], [0.30, 0.45, 0.25]),
] + BLOQUES_BIG_O

generar(
    b,
    f"{DOCS}/Entrega_Parcial/3_Informe_Avance_BigO.pdf",
    md=f"{DOCS}/Entrega_Parcial/3_Informe_Avance_BigO.md",
    encabezado=ENC,
    ruta_base=DOCS,
)
shutil.copyfile(f"{DOCS}/Entrega_Parcial/3_Informe_Avance_BigO.md", os.path.join(RAIZ, "ANALISIS_BIG_O.md"))
print("3_Informe_Avance_BigO.pdf + .md + ANALISIS_BIG_O.md ok")

# =====================================================================================
# ENTREGA FINAL - INFORME TÉCNICO FINAL DE INGENIERÍA (PDF + Markdown con Big O completo)
# =====================================================================================
FILAS_SEG = [
    ["tac_01", "2 tumores (r=13 en (100,108); r=8 en (165,150))", f"{GT1a} px y {GT1b} px", "421 px y 140 px", f"{421/GT1a*100:.0f}% y {140/GT1b*100:.0f}%", "(99.6, 107.9) y (165.0, 150.0)"],
    ["tac_02", "1 tumor irregular (dos círculos unidos)", f"{GT2} px", "536 px", f"{536/GT2*100:.0f}%", "(124.1, 163.5)"],
    ["tac_03", "Sano (sin tumor)", "0", "Sin regiones (Option = Nothing)", "-", "-"],
]
b = portada("Informe Técnico Final de Ingeniería", "Entrega Final y Sustentación (Sesión 5)")
b += [
    ("h1", "1. Resumen"),
    ("p", "Se desarrolló un sistema multiparadigma para procesar tomografías: un kernel imperativo en <b>C++17 con OpenMP y Loop Tiling (32×32)</b> calcula bordes por convolución "
          "2D maximizando la localidad espacial y temporal de la caché L1; un dominio <b>orientado a objetos en Java 17</b> (Factory Method, Template Method, DIP, inmutabilidad) orquesta el análisis; y un pipeline <b>funcional en Python</b> "
          "normaliza intensidades y segmenta regiones mediante expansión funcional por capas (en espacio de pila O(1), sin recursión de cola) y composición monádica con <b>Option/Maybe</b>. El sistema detecta correctamente los tumores sintéticos de los "
          "tres estudios de prueba y pasa 30 pruebas automáticas (12 Python, 18 Java). La versión paralela produce resultados idénticos a la secuencial."),
    ("h1", "2. Caso de estudio y requerimientos"),
    ("table", ["Requerimiento de la especificación (Grupo 4)", "Implementación", "Dónde"], [
        ["Kernel de convolución Θ(W·H·K²), Loop Tiling y OpenMP", "convolucionar(): padding contiguo, bloques TILE_SIZE=32, #pragma omp parallel for collapse(2)", "cpp/convolucion.cpp"],
        ["Factory Method y Template Method para analizadores médicos", "FabricaAnalizador (Creator), AnalizadorBase (Template Method) y fábricas Tumoral / Óseo", "java/src/tac/analisis"],
        ["Copias defensivas en EstudioMedico y ResultadoAnalisis", "clone() al entrar y al salir; List.copyOf() para regiones inmodificables", "dominio/EstudioMedico.java"],
        ["Inversión de dependencias con RepositorioImagen", "Interfaz RepositorioImagen; ServicioDiagnostico depende solo de abstracciones", "repositorio/, analisis/ServicioDiagnostico.java"],
        ["Mapeo puro de intensidad de píxeles", "ventana() currificada + map", "funcional/pixeles.py"],
        ["Segmentación sin desbordamiento de pila (O(1) stack)", "crecer_region / componentes por capas de frontera con frozenset", "funcional/segmentacion.py"],
        ["Mónada Option / Maybe (Some / Nothing)", "map, flat_map, filter, fold, get_or_else en parsear_pgm, estadisticas_opt, segmentar_opt y cli.py", "funcional/option.py, segmentacion.py, cli.py"],
        ["Functional Core, Imperative Shell; benchmarks; thread safety", "cli.py como única capa con E/S; make bench; pruebas concurrentes", "funcional/cli.py, cpp/bench.cpp, PruebasTac"],
    ], [0.36, 0.38, 0.26]),
    ("h1", "3. Implementación por paradigma"),
    ("h2", "3.1 Imperativo - C++17, Loop Tiling y OpenMP"),
    ("bullets", [
        "<b>Memoria contigua:</b> imagen y buffers en std::vector&lt;float&gt; en el Heap sin fugas por RAII; punteros nativos en el núcleo de cómputo.",
        "<b>Loop Tiling (Cache Blocking 32×32):</b> particiona la iteración en bloques de 32×32 píxeles (~9.2 KB con vecindad y kernel), garantizando que los datos residan en la caché L1 de 32 KB durante todas las pasadas del filtro K×K.",
        "<b>Paralelismo:</b> <font face='DV-M'>#pragma omp parallel for collapse(2) schedule(static)</font> reparte los bloques 2D entre hilos sin condiciones de carrera.",
    ]),
    ("h2", "3.2 Orientado a objetos - Java 17"),
    ("bullets", [
        "<b>Inmutabilidad y aliasing:</b> 7 pruebas verifican copias defensivas de entrada y salida e inmodificabilidad de colecciones.",
        "<b>Thread safety:</b> servicio sin estado mutable, archivos temporales únicos por proceso e implementación concurrente con ConcurrentHashMap.",
    ]),
    ("h2", "3.3 Funcional - Python 3.10+"),
    ("bullets", [
        "<b>Pureza y transparencia referencial:</b> funciones puras sobre tuplas y frozensets inmutables.",
        "<b>Eliminación de recursión de cola:</b> dado que Python no soporta TCO nativo, la exploración de componentes conexas se realiza por capas de frontera inmutables en espacio de pila constante Θ(1).",
        "<b>Mónada Option completa:</b> encadenamiento declarativo con <font face='DV-M'>map</font>, <font face='DV-M'>flat_map</font>, <font face='DV-M'>filter</font> y <font face='DV-M'>fold</font> sin usar excepciones ni None.",
    ]),
    ("h1", "4. Resultados de segmentación"),
    ("table", ["Estudio", "Verdad (fantoma)", "Área real", "Área detectada", "Detectado/real", "Centroide detectado"], FILAS_SEG, [0.09, 0.26, 0.13, 0.17, 0.13, 0.22]),
    ("img", "figuras/resultados.png", 0.95, "Figura 2. Resultados: original, bordes (C++), máscara etiquetada (Python) y superposición."),
] + BLOQUES_BIG_O + [
    ("h1", "6. Benchmarks de paralelismo (Secuencial vs Paralelo)"),
    ("p", f"Método: kernel de caja K×K sobre imagen aleatoria con Loop Tiling 32×32; mejor de 3 ejecuciones; igualdad bit a bit comprobada. "
          f"<b>Hilos máximos de OpenMP en el entorno = {HILOS_BENCH}</b>."),
    ("table", ["Tamaño", "K", "Hilos", "T seq (ms)", "T par (ms)", "Speedup", "Eficiencia", "Resultado igual"], TABLA_BENCH,
     [0.14, 0.07, 0.08, 0.14, 0.14, 0.13, 0.15, 0.15]),
    ("h1", "7. Pruebas y validación"),
    ("table", ["Suite", "Pruebas", "Qué cubre"], [
        ["Python (unittest)", "12", "Mónada Option (map, flat_map, filter, fold), pureza, currificación, compose, máscara, componentes sin recursión de cola (20 000 píxeles en pila O(1)), PGM"],
        ["Java (PruebasTac)", "18", "Aliasing, inmodificabilidad, Factory Method, integración real de 3 módulos, DIP con falsos, lote concurrente, estrés, propagación de errores"],
        ["C++ (bench)", "-", "Igualdad bit a bit secuencial vs paralelo con Loop Tiling en cada configuración"],
    ], [0.22, 0.10, 0.68]),
]
generar(b, f"{DOCS}/Entrega_Final/Informe_Tecnico_Final.pdf", md=f"{DOCS}/Entrega_Final/Informe_Tecnico_Final.md", encabezado=ENC, ruta_base=DOCS)
print("Informe_Tecnico_Final ok")
# =====================================================================================
# DOCUMENTO DE EVIDENCIA DE INTEGRACIÓN Y PRUEBAS DE ALIASING (ACTUALIZADO)
# =====================================================================================
b_ev = [
    ("title", "Integración Java–C++–Python y Pruebas de Aliasing"),
    ("sub", "<b>Grupo 4:</b> Segmentación y Procesamiento de Imágenes Médicas por Visión Artificial"),
    ("sub", "Integrantes: Juan Manuel Cuervo, Juan Nicolas Buitrago, David Santiago Sanchez, Santiago Vasquez Ochica"),
    ("space", 0.2),
    ("h1", "1. Integración del Módulo OO (Java) con el Kernel C++ y el Pipeline Funcional"),
    ("h2", "1.1 Cómo se integran"),
    ("p", "El Módulo 2 (Java 17, orientado a objetos) es el orquestador. No conoce los detalles de C++ ni de Python: depende de dos interfaces, "
          "NucleoConvolucion (kernel C++ con OpenMP y Loop Tiling) y PipelineFuncional (funciones puras en Python con mónada Option). "
          "Cada interfaz tiene un adaptador que ejecuta el programa externo como un proceso, con la entrada y la salida en archivos temporales (imágenes PGM). "
          "Para un estudio, el flujo es: Java carga el estudio -> Python normaliza (12 a 8 bits) -> C++ calcula bordes (Gauss 5x5 + Sobel 3x3 con Loop Tiling 32x32 y OpenMP collapse(2)) "
          "-> Python segmenta regiones (expansión funcional por capas sin recursión de cola + mónada Option) -> Java entrega un resultado inmutable."),
    ("img", "figuras/flujo_datos.png", 1.0, "Figura 1. Flujo de datos entre los tres módulos."),
    ("table", ["Contrato (Java)", "Módulo que lo cumple", "Adaptador"], [
        ["NucleoConvolucion.detectarBordes(ancho, alto, pixeles)", "Kernel imperativo C++17 + OpenMP + Loop Tiling (build/convolve)", "NucleoConvolucionCpp"],
        ["PipelineFuncional.normalizar(...)", "Pipeline funcional Python (funcional/cli.py normalizar)", "PipelineFuncionalPython"],
        ["PipelineFuncional.segmentar(...)", "Pipeline funcional Python (funcional/cli.py segmentar)", "PipelineFuncionalPython"],
    ], [0.38, 0.38, 0.24]),
    ("h2", "1.2 Código de la integración actualizado"),
    ("p", "<b>Kernel C++ paralelo con Loop Tiling 32x32 (cpp/convolucion.cpp):</b> maximiza la localidad espacial y temporal en caché L1:"),
    ("code", "constexpr int TILE_SIZE = 32;\n"
             "#pragma omp parallel for collapse(2) schedule(static) if (paralelo)\n"
             "for (int ty = 0; ty < h; ty += TILE_SIZE) {\n"
             "    for (int tx = 0; tx < w; tx += TILE_SIZE) {\n"
             "        const int y_lim = std::min(ty + TILE_SIZE, h);\n"
             "        const int x_lim = std::min(tx + TILE_SIZE, w);\n"
             "        for (int y = ty; y < y_lim; ++y) {\n"
             "            float* fila = out + static_cast<size_t>(y) * w;\n"
             "            for (int x = tx; x < x_lim; ++x) {\n"
             "                float acc = 0.0f;\n"
             "                for (int ky = 0; ky < k; ++ky) {\n"
             "                    const float* fp = p + static_cast<size_t>(y + ky) * pw + x;\n"
             "                    const float* fk = kw + static_cast<size_t>(ky) * k;\n"
             "                    for (int kx = 0; kx < k; ++kx) acc += fp[kx] * fk[kx];\n"
             "                }\n"
             "                fila[x] = acc;\n"
             "            }\n"
             "        }\n"
             "    }\n"
             "}"),
    ("p", "<b>Segmentación funcional pura con mónada Option y sin recursión de cola (funcional/segmentacion.py):</b>"),
    ("code", "def estadisticas_opt(etiqueta: int, pixeles, ancho: int, area_min: int = 1) -> Option[Region]:\n"
             "    return (\n"
             "        Some(tuple(sorted(pixeles)))\n"
             "        .filter(lambda px: len(px) >= max(1, area_min))\n"
             "        .map(lambda px: reduce(_acumular(ancho), px, _Acum(0, 10 ** 9, 10 ** 9, -1, -1, 0, 0)))\n"
             "        .map(lambda a: Region(etiqueta, a.area, a.x_min, a.y_min, a.x_max, a.y_max,\n"
             "                              round(a.suma_x / a.area, 2), round(a.suma_y / a.area, 2)))\n"
             "    )"),
    ("h1", "2. Pruebas de inmutabilidad, mónada Option y prevención de aliasing"),
    ("p", "Ejecución de las 12 pruebas unitarias de Python y las 18 pruebas de Java (30/30 pruebas exitosas):"),
    ("code", "test_some_map_flat_map_filter_y_fold ... ok\n"
             "test_nothing_ignora_las_funciones ... ok\n"
             "test_expansion_por_capas_no_desborda_la_pila ... ok\n"
             "test_region_mayor_y_estadisticas_con_option ... ok\n"
             "test_segmentar_es_pura_y_monadica ... ok\n"
             "Ran 12 tests ... OK\n\n"
             "[OK] Copia defensiva de entrada (constructor)\n"
             "[OK] Copia defensiva de salida (getPixeles)\n"
             "[OK] Lista del resultado es inmodificable\n"
             "[OK] Mascara del resultado protegida con copia\n"
             "18/18 pruebas correctas"),
    ("h1", "3. Diagramas de clases UML del Módulo POO (Java 17)"),
    ("img", "figuras/clases_dominio.png", 1.0, "Figura 2. Dominio, repositorio y servicio."),
    ("img", "figuras/clases_fabrica.png", 0.95, "Figura 3. Factory Method (fábricas), Template Method y analizadores."),
    ("img", "figuras/clases_integracion.png", 1.0, "Figura 4. Contratos y adaptadores hacia el kernel C++ y el pipeline funcional."),
]
generar(b_ev, f"{DOCS}/Entrega_Final/Evidencia_Integracion_y_Aliasing.pdf", apaisado=True, encabezado=ENC, ruta_base=DOCS)
shutil.copyfile(f"{DOCS}/Entrega_Final/Evidencia_Integracion_y_Aliasing.pdf", os.path.join(RAIZ, "Evidencia Integracion y Aliasing.pdf"))
print("Evidencia_Integracion_y_Aliasing.pdf ok")