"""Genera los PDF/Markdown de las entregas. Ejecutar desde la raiz del proyecto:
    python3 docs/herramientas/generar_documentos.py
Requiere: reportlab, matplotlib, pillow. Lee docs/benchmarks.md (resultado de `make bench`)."""
import math
import os
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
        ("sub", "Integrantes: [Nombre 1], [Nombre 2], [Nombre 3], [Nombre 4]  (completar)"),
        ("sub", "Docente: [completar]   |   Fecha: noviembre de 2026"),
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
    f = 1.0 / (1 + k * k)  # fraccion secuencial: 1 unidad (copia con borde) frente a K^2 unidades (MAC)
    return 1.0 / (f + (1 - f) / p)


HILOS_BENCH, FILAS_BENCH = leer_benchmarks()
TABLA_BENCH = FILAS_BENCH
GT1a, GT1b = area_real([(100, 108, 13)]), area_real([(165, 150, 8)])
GT2 = area_real([(120, 160, 12), (132, 170, 9)])
TABLA_AMDAHL = [[f"K = {k}", f"{1/(1+k*k)*100:.1f}%"] + [f"{amdahl(k, p):.2f}x" for p in (2, 4, 8)] for k in (3, 5, 9)]

# =====================================================================================
# 1. ENTREGA PARCIAL - DOCUMENTO DE ARQUITECTURA Y ESPECIFICACIÓN UML (PDF)
# =====================================================================================
b = portada("Documento de Arquitectura y Especificación UML", "Entrega Parcial (Sesión 3) - Entregable 1")
b += [
    ("h1", "1. Alcance y caso de estudio"),
    ("p", "<b>Problema (Grupo 4).</b> Un centro de diagnóstico necesita procesar tomografías (TAC) de alta resolución, aplicar "
          "filtros de convolución bidimensional para detectar bordes de tejidos y segmentar automáticamente regiones tumorales."),
    ("p", "<b>Solución multiparadigma.</b> Tres módulos conectados, cada uno en el paradigma y lenguaje exigidos por la especificación: "
          "Módulo 1 imperativo en C++17 con OpenMP (convolución sobre memoria contigua), Módulo 2 orientado a objetos en Java 17 "
          "(modelo de dominio, Factory Method, DIP, copias defensivas) y Módulo 3 funcional en Python 3.10+ (mapeo puro de intensidades, "
          "recursión de cola y contenedor Option)."),
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
# 3. ENTREGA PARCIAL - INFORME DE AVANCE TÉCNICO Y ANÁLISIS BIG O PRELIMINAR
# =====================================================================================
b = portada("Informe de Avance Técnico y Análisis Big O Preliminar", "Entrega Parcial (Sesión 3) - Entregable 3")
b += [
    ("h1", "1. Estado de avance"),
    ("table", ["Módulo / actividad", "Estado a la Sesión 3", "Evidencia"], [
        ["Módulo 1 - Kernel imperativo C++17", "Terminado: convolución 2D (Gauss 5x5, Sobel 3x3), padding contiguo, OpenMP por filas", "cpp/, build/convolve, build/bench"],
        ["Módulo 3 - Pipeline funcional Python", "Terminado: normalización, máscara, recursión de cola con trampolín, Option, currificación", "funcional/, 12 pruebas unitarias OK"],
        ["Módulo 2 - POO Java 17", "Terminado e integrado: dominio inmutable, Factory Method, DIP, servicio con lote concurrente", "java/src, 18 pruebas OK"],
        ["Integración Java -> Python -> C++ -> Python", "Funcionando de punta a punta con datos sintéticos", "make demo"],
        ["Pruebas de inmutabilidad y aliasing", "Hechas (7 pruebas de copias defensivas e inmodificabilidad)", "tac.pruebas.PruebasTac"],
        ["Benchmarks Secuencial vs Paralelo", "Programa listo; resultados de esta máquina en el informe final", "cpp/bench.cpp, docs/benchmarks.md"],
        ["Pendiente (Sesión 4-5)", "Refactor final, benchmarks en el equipo del grupo, informe final, diapositivas y sustentación", "-"],
    ], [0.30, 0.45, 0.25]),
    ("nota", "<b>Datos:</b> las TAC son <b>sintéticas</b> (fantoma generado con datos/generar_tac.py: cráneo, cerebro, ventrículos, "
             "tumores, ruido y desenfoque). No son imágenes de pacientes ni validan un uso clínico."),
    ("h1", "2. Notación y supuestos"),
    ("p", "<b>W</b> = ancho, <b>H</b> = alto (en píxeles), <b>K</b> = lado del kernel (impar), <b>r = piso(K/2)</b>, <b>p</b> = número de hilos, "
          "<b>M</b> = cantidad de píxeles marcados en la máscara de segmentación (M ≤ W·H), <b>n<sub>r</sub></b> = píxeles de una región. "
          "Se cuenta como operación elemental cada multiplicación, suma, comparación o acceso a memoria; su costo se acota por una constante <b>c</b>."),
    ("h1", "3. Módulo 1 (C++): convolución 2D"),
    ("h2", "3.1 Complejidad temporal"),
    ("p", "Para cada píxel de salida (y, x) se calcula:"),
    ("formula", "out(y, x) = Σ<sub>i=0</sub><super>K-1</super> Σ<sub>j=0</sub><super>K-1</super> w(i, j) · pad(y + i, x + j)"),
    ("p", "Cada término cuesta una multiplicación, una suma y dos lecturas: a lo sumo <b>c</b> operaciones. Entonces:"),
    ("formula", "T(W, H, K) = Σ<sub>y=0</sub><super>H-1</super> Σ<sub>x=0</sub><super>W-1</super> Σ<sub>i=0</sub><super>K-1</super> Σ<sub>j=0</sub><super>K-1</super> c = c · H · W · K · K = c · W · H · K²"),
    ("p", "Como el costo por término es constante, existen c₁ = c₂ = c tales que c₁·W·H·K² ≤ T ≤ c₂·W·H·K²; por definición <b>T(W, H, K) = Θ(W·H·K²)</b>."),
    ("p", "<b>Costo del padding.</b> Se copia una imagen de tamaño (W + K - 1)(H + K - 1) = W·H + (K-1)(W + H) + (K-1)². Como W + H ≤ 2·W·H, "
          "se cumple (K-1)(W+H) ≤ 2·W·H·K², y además (K-1)² ≤ W·H·K². Luego el padding es O(W·H·K²) y no cambia el orden total: "
          "<b>T<sub>total</sub> = Θ(W·H·K²)</b>."),
    ("h2", "3.2 Complejidad espacial"),
    ("formula", "S(W, H, K) = (W + K - 1)(H + K - 1) [pad] + W·H [salida] + K² [kernel] = Θ(W·H + K(W + H) + K²)"),
    ("p", "Si K ≤ min(W, H) (siempre cierto en imágenes reales) entonces K·W ≤ W·H y K·H ≤ W·H, por lo que K(W + H) ≤ 2·W·H y K² ≤ W·H. "
          "Resulta <b>S = Θ(W·H)</b> (espacio auxiliar, además de la entrada)."),
    ("h2", "3.3 Detección de bordes (Gauss 5x5 + Sobel X + Sobel Y + magnitud)"),
    ("formula", "T<sub>bordes</sub> = c · W·H · (5² + 3² + 3²) + c' · W·H = c · W·H · 43 + c' · W·H = Θ(W·H)"),
    ("p", "Con K fijos (5 y 3) los factores K² son constantes: el pipeline de bordes es <b>lineal en el número de píxeles</b>. "
          "En espacio se usan 5 arreglos auxiliares de W·H floats (liso, gx, gy, magnitud, pad) y la copia de entrada: <b>Θ(W·H)</b>. "
          "Para 256×256 son unos 1.6 MB."),
    ("h2", "3.4 Versión paralela (OpenMP)"),
    ("p", "<b>Corrección (sin condiciones de carrera).</b> La iteración y escribe únicamente en la fila y de la salida: los conjuntos de escritura "
          "{out[y·W .. y·W + W - 1]} son disjuntos para y distintos, y los arreglos pad y kernel solo se leen. Se cumplen las condiciones de "
          "Bernstein (ningún par de iteraciones tiene conflicto escritura/escritura ni lectura/escritura), así que no hay <i>data races</i>. "
          "No se usan locks, de modo que tampoco hay <i>deadlocks</i>; la única sincronización es la barrera implícita al final del "
          "<font face='DV-M'>parallel for</font>. El benchmark comprueba además que el resultado paralelo es <b>idéntico bit a bit</b> al secuencial."),
    ("p", "<b>Tiempo.</b> Con planificación estática, cada hilo procesa a lo sumo techo(H/p) filas de costo Θ(W·K²); el padding se mantiene secuencial:"),
    ("formula", "T<sub>p</sub> = Θ(techo(H/p) · W · K²) + Θ(W·H) = Θ(W·H·K² / p + W·H)   (p ≤ H)"),
    ("p", "Aplicando la ley de Amdahl con fracción secuencial f ≈ 1/(1 + K²) (una unidad de copia por píxel frente a K² de cálculo):"),
    ("formula", "S<sub>máx</sub>(p) = 1 / ( f + (1 - f)/p )"),
    ("table", ["Kernel", "f (secuencial)", "p = 2", "p = 4", "p = 8"], TABLA_AMDAHL, [0.2, 0.2, 0.2, 0.2, 0.2]),
    ("p", "<i>Estos valores son un modelo teórico (cota superior), no mediciones: ignoran el ancho de banda de memoria y el costo de crear hilos.</i>"),
    ("h2", "3.5 Localidad de caché"),
    ("p", "La imagen se guarda por filas (row-major) en un bloque contiguo de memoria. El bucle interno recorre K floats consecutivos de cada fila "
          "(<font face='DV-M'>fp[kx]</font>), que caben en una o dos líneas de caché de 64 bytes (16 floats); al avanzar x se reutilizan K-1 de ellos. "
          "El padding con bordes replicados elimina los <font face='DV-M'>if</font> de borde del bucle interno, y paralelizar por filas evita que dos hilos escriban en la misma línea de caché (salvo en el borde entre bloques)."),
    ("h1", "4. Módulo 3 (Python funcional)"),
    ("table", ["Función", "Tiempo", "Espacio", "Justificación"], [
        ["normalizar (map + ventana)", "Θ(W·H)", "Θ(W·H)", "Una aplicación O(1) por píxel; se crea una tupla nueva."],
        ["mascara (map sobre 2 tuplas)", "Θ(W·H)", "Θ(W·H)", "Una comparación de banda y una de borde por píxel."],
        ["componentes (recursión de cola)", "O(M²) peor caso", "O(M)", "Ver análisis abajo."],
        ["estadisticas (sorted + reduce)", "Θ(n<sub>r</sub> log n<sub>r</sub>)", "O(n<sub>r</sub>)", "sorted es n log n; reduce recorre n elementos una vez."],
        ["region_mayor (reduce)", "Θ(R)", "O(1)", "Un paso por región; R = cantidad de regiones."],
        ["segmentar (total)", "O(W·H + M²)", "O(W·H)", "Suma de las anteriores; domina M² solo si M es grande."],
    ], [0.30, 0.18, 0.12, 0.40]),
    ("h2", "Análisis de componentes()"),
    ("p", "En <font face='DV-M'>_crecer</font> cada paso extrae un elemento de la frontera. Un píxel entra a la frontera como máximo 4 veces (una por vecino), "
          "así que los pasos de una región con n<sub>r</sub> píxeles son ≤ 4·n<sub>r</sub> + 1. Cada paso hace <font face='DV-M'>region | {actual}</font>, que "
          "copia un frozenset de hasta n<sub>r</sub> elementos (inmutabilidad), y <font face='DV-M'>frontera[1:]</font>, que copia la frontera "
          "(≤ 4·n<sub>r</sub>). La parte dominante es:"),
    ("formula", "Σ<sub>k=1</sub><super>n<sub>r</sub></super> k = n<sub>r</sub>(n<sub>r</sub> + 1)/2 = Θ(n<sub>r</sub>²)  por región"),
    ("p", "Sumando sobre todas las regiones, Σ n<sub>r</sub>² ≤ M²; además <font face='DV-M'>min(pendientes)</font> y <font face='DV-M'>pendientes - region</font> cuestan "
          "O(M) por región, o sea O(R·M) ≤ O(M²). Total: <b>O(M²)</b> en el peor caso. En las imágenes de prueba M ≈ 600 píxeles, muy por debajo de W·H = 65 536."),
    ("p", "<b>Costo de la pureza.</b> Una versión con conjunto mutable (BFS) sería O(M); aquí se acepta O(M²) porque el requisito es inmutabilidad y "
          "transparencia referencial. Se podría recuperar O(M log M) con estructuras de datos persistentes (por ejemplo, HAMT)."),
    ("p", "<b>Pila.</b> Python no optimiza llamadas de cola. El trampolín ejecuta cada paso en un bucle, por lo que la profundidad de pila es <b>O(1)</b> "
          "frente a O(n<sub>r</sub>) de la recursión directa (la prueba <font face='DV-M'>test_recursion_de_cola_no_desborda_la_pila</font> recorre 20 000 pasos, más que el límite de recursión)."),
    ("h1", "5. Módulo 2 (Java) e integración"),
    ("table", ["Operación", "Tiempo", "Espacio", "Comentario"], [
        ["EstudioMedico (constructor) y getPixeles()", "Θ(W·H)", "Θ(W·H)", "Copia defensiva con clone(): el precio de evitar aliasing."],
        ["Leer / escribir PGM (FormatoPGM)", "Θ(W·H)", "Θ(W·H)", "Un token por píxel."],
        ["ResultadoAnalisis (constructor)", "Θ(W·H + R)", "Θ(W·H + R)", "Clona 2 arreglos y copia la lista de R regiones."],
        ["ServicioDiagnostico.analizar", "Θ(W·H·(K<sub>g</sub>² + K<sub>s</sub>²)) + O(M²)", "Θ(W·H)", "Suma de C++ (Θ(W·H) con K fijo) y segmentación Python."],
        ["analizarLote con p hilos y N estudios", "≈ (N / p) · T<sub>estudio</sub>", "Θ(p · W·H)", "Cada tarea usa archivos temporales propios; resultados inmutables."],
    ], [0.30, 0.25, 0.15, 0.30]),
    ("h1", "6. Plan para las sesiones 4 y 5"),
    ("bullets", [
        "Medir speedup real en el computador del grupo con <font face='DV-M'>make bench</font> y completar las tablas del informe final.",
        "Refinar la separación Functional Core / Imperative Shell y documentar los efectos secundarios.",
        "Preparar diapositivas (máx. 10) y repasar el código para el interrogatorio individual.",
    ]),
]
generar(b, f"{DOCS}/Entrega_Parcial/3_Informe_Avance_BigO.pdf", encabezado=ENC, ruta_base=DOCS)
print("3_Informe_Avance_BigO.pdf ok")

# =====================================================================================
# ENTREGA FINAL - INFORME TÉCNICO FINAL DE INGENIERÍA (PDF + Markdown)
# =====================================================================================
FILAS_SEG = [
    ["tac_01", "2 tumores (r=13 en (100,108); r=8 en (165,150))", f"{GT1a} px y {GT1b} px", "421 px y 140 px", f"{421/GT1a*100:.0f}% y {140/GT1b*100:.0f}%", "(99.6, 107.9) y (165.0, 150.0)"],
    ["tac_02", "1 tumor irregular (dos círculos unidos)", f"{GT2} px", "536 px", f"{536/GT2*100:.0f}%", "(124.1, 163.5)"],
    ["tac_03", "Sano (sin tumor)", "0", "Sin regiones (Option = Nothing)", "-", "-"],
]
b = portada("Informe Técnico Final de Ingeniería", "Entrega Final y Sustentación (Sesión 5)")
b += [
    ("h1", "1. Resumen"),
    ("p", "Se desarrolló un sistema multiparadigma para procesar tomografías: un kernel imperativo en <b>C++17 con OpenMP</b> calcula bordes por convolución "
          "2D; un dominio <b>orientado a objetos en Java 17</b> (Factory Method, DIP, inmutabilidad) orquesta el análisis; y un pipeline <b>funcional en Python</b> "
          "normaliza intensidades y segmenta regiones con recursión de cola y contenedores Option. El sistema detecta correctamente los tumores sintéticos de los "
          "tres estudios de prueba y pasa 30 pruebas automáticas (12 Python, 18 Java). La versión paralela produce resultados idénticos a la secuencial."),
    ("nota", "<b>Limitaciones importantes:</b> (1) los datos son TAC sintéticas, no clínicas; (2) los benchmarks incluidos se midieron en un entorno con "
             "<b>1 solo hilo de hardware</b>, por lo que no pueden mostrar aceleración: la sección 7 explica cómo obtener la tabla de speedup real en el equipo del grupo."),
    ("h1", "2. Caso de estudio y requerimientos"),
    ("table", ["Requerimiento de la especificación (Grupo 4)", "Implementación", "Dónde"], [
        ["Kernel de convolución O(W·H·K²), localidad de caché por filas contiguas, OpenMP", "convolucionar(): padding contiguo, bucle por filas, #pragma omp parallel for", "cpp/convolucion.cpp"],
        ["Factory Method para instanciar analizadores médicos", "FabricaAnalizador (Creator) y fábricas Tumoral / Óseo", "java/src/tac/analisis"],
        ["Copias defensivas en EstudioMedico", "clone() al entrar y al salir; getPixeles() devuelve copia", "dominio/EstudioMedico.java"],
        ["Inversión de dependencias con RepositorioImagen", "Interfaz RepositorioImagen; ServicioDiagnostico depende solo de ella", "repositorio/, analisis/ServicioDiagnostico.java"],
        ["Mapeo puro de intensidad de píxeles", "ventana() currificada + map", "funcional/pixeles.py"],
        ["Recursión de cola (TCO) para segmentación", "_crecer / _etiquetar con trampolín", "funcional/segmentacion.py"],
        ["Contenedores Option / Maybe", "Some / Nothing; parsear_pgm y region_mayor", "funcional/option.py"],
        ["Functional Core, Imperative Shell; benchmarks; thread safety", "cli.py como única capa con E/S; make bench; pruebas concurrentes", "funcional/cli.py, cpp/bench.cpp, PruebasTac"],
    ], [0.36, 0.38, 0.26]),
    ("h1", "3. Arquitectura de dominio"),
    ("p", "El diseño completo (diagramas UML con visibilidades, firmas y relaciones) está en el documento de la entrega parcial. Resumen de decisiones:"),
    ("bullets", [
        "<b>Dominio inmutable:</b> EstudioMedico es una clase final con copias defensivas; ResultadoAnalisis, RegionTumoral y ParametrosSegmentacion son <i>records</i> con listas copiadas (List.copyOf) y arreglos clonados.",
        "<b>Template Method:</b> AnalizadorBase.analizar() es final y fija normalizar -> bordes -> segmentar; las subclases solo entregan parámetros (OCP, LSP).",
        "<b>Factory Method:</b> el servicio crea analizadores a través de FabricaAnalizador sin conocer clases concretas.",
        "<b>DIP:</b> ServicioDiagnostico, AnalizadorBase y las fábricas dependen de interfaces; las pruebas sustituyen C++ y Python por falsos.",
    ]),
    ("img", "figuras/flujo_datos.png", 1.0, "Figura 1. Flujo de datos entre los tres módulos."),
    ("h1", "4. Implementación por paradigma"),
    ("h2", "4.1 Imperativo - C++17 y OpenMP"),
    ("bullets", [
        "<b>Memoria:</b> imagen y buffers en std::vector&lt;float&gt; (bloque contiguo en el Heap, sin fugas por RAII); el filtro gaussiano es un arreglo pequeño en el Stack.",
        "<b>Optimización:</b> el padding con bordes replicados quita las ramas del bucle interno; el recorrido es por filas (row-major).",
        "<b>Paralelismo:</b> <font face='DV-M'>#pragma omp parallel for schedule(static)</font> sobre las filas; cada hilo escribe filas distintas, sin locks y sin carreras.",
        "<b>Interfaz:</b> programa convolve (PGM por stdin/stdout) y programa bench.",
    ]),
    ("h2", "4.2 Orientado a objetos - Java 17"),
    ("bullets", [
        "<b>Inmutabilidad y aliasing:</b> 7 pruebas comprueban que modificar el arreglo original, el devuelto por getPixeles() o la lista de resultados no altera el estado interno.",
        "<b>Thread safety:</b> el servicio no tiene estado mutable; cada llamada externa usa archivos temporales propios; RepositorioImagenEnMemoria usa ConcurrentHashMap. Prueba de estrés: 8 hilos × 500 escrituras sin pérdidas; lote con 4 hilos = lote con 1 hilo.",
        "<b>Errores:</b> jerarquía de excepciones verificadas (TacException); un fallo en un hilo del lote se propaga al llamador.",
    ]),
    ("h2", "4.3 Funcional - Python 3.10+"),
    ("bullets", [
        "<b>Pureza y transparencia referencial:</b> normalizar, mascara y segmentar no modifican sus argumentos ni hacen E/S; mismas entradas, mismas salidas (probado).",
        "<b>map / filter / reduce:</b> map para ventana y máscara, filter para filtrar regiones pequeñas y píxeles pendientes, reduce para estadísticas de región y región mayor.",
        "<b>Currificación:</b> <font face='DV-M'>ventana(nivel)(ancho)(pixel)</font> y <font face='DV-M'>en_banda(bajo)(alto)</font>; compose para composición de funciones.",
        "<b>Evaluación perezosa:</b> generador vecinos4 y filter sobre componentes se evalúan bajo demanda.",
        "<b>Recursión de cola:</b> Python no hace TCO; se emula con un <i>trampolín</i> (cada paso devuelve la siguiente llamada y un bucle la ejecuta), con pila constante.",
        "<b>Option:</b> parsear_pgm devuelve Some/Nothing en lugar de excepciones o None; region_mayor devuelve Nothing si no hay regiones (estudio sano).",
    ]),
    ("h1", "5. Algoritmo de segmentación"),
    ("p", "1) Ventana nivel/ancho lleva 12 bits a 8 bits. 2) C++ calcula la magnitud del gradiente (suavizado 5×5 + Sobel). 3) Máscara = píxeles dentro de "
          "la banda de intensidad del tejido buscado <b>y</b> con borde débil (excluye las transiciones cerebro/cráneo, que caerían en la banda). "
          "4) Componentes conexas (4 vecinos) por recursión de cola; 5) se descartan regiones menores que el área mínima; 6) se calculan área, caja y centroide."),
    ("table", ["Estudio", "Verdad (fantoma)", "Área real", "Área detectada", "Detectado/real", "Centroide detectado"], FILAS_SEG, [0.09, 0.26, 0.13, 0.17, 0.13, 0.22]),
    ("p", "Las áreas detectadas son menores (70-80 %) porque se excluyen los píxeles del borde del tumor para separar regiones; los centroides coinciden con los reales (error menor que 0.5 px en tac_01). "
          "Los umbrales (banda 100-170, borde < 30, área mínima 30) se calibraron manualmente sobre estos fantomas y <b>no se validaron con imágenes reales</b>."),
    ("img", "figuras/resultados.png", 0.95, "Figura 2. Resultados: original, bordes (C++), máscara etiquetada (Python) y superposición."),
    ("h1", "6. Análisis Big O"),
    ("p", "Demostraciones formales en el informe de avance (entrega parcial). Resumen:"),
    ("table", ["Componente", "Tiempo", "Espacio"], [
        ["Convolución K×K (C++)", "Θ(W·H·K²)", "Θ(W·H)"],
        ["Detección de bordes (K fijos 5 y 3)", "Θ(W·H)", "Θ(W·H)"],
        ["Versión paralela con p hilos", "Θ(W·H·K²/p + W·H)", "Θ(W·H)"],
        ["Normalizar y máscara (Python)", "Θ(W·H)", "Θ(W·H)"],
        ["Componentes conexas con estructuras inmutables", "O(M²) peor caso", "O(M)"],
        ["Copias defensivas y E/S (Java)", "Θ(W·H)", "Θ(W·H)"],
    ], [0.5, 0.3, 0.2]),
    ("h1", "7. Benchmarks de paralelismo (Secuencial vs Paralelo)"),
    ("p", f"Método: kernel de caja K×K sobre imagen aleatoria; se toma el mejor de 3 ejecuciones; se verifica que el resultado paralelo sea idéntico al secuencial. "
          f"<b>Entorno de esta medición: hilos máximos de OpenMP = {HILOS_BENCH}</b>."),
    ("table", ["Tamaño", "K", "Hilos", "T seq (ms)", "T par (ms)", "Speedup", "Eficiencia", "Resultado igual"], TABLA_BENCH,
     [0.14, 0.07, 0.08, 0.14, 0.14, 0.13, 0.15, 0.15]),
    ("nota", "<b>Interpretación honesta:</b> con 1 hilo de hardware, pedir 2 o 4 hilos no puede acelerar (speedup ≈ 1.0x; las pequeñas diferencias son ruido de medición). "
             "Estas cifras <b>no demuestran</b> aceleración; demuestran que la versión paralela es correcta e idéntica a la secuencial. "
             "Para el speedup real, ejecutar <font face='DV-M'>make bench</font> en el computador del grupo (con 4 o más núcleos), y volver a correr "
             "<font face='DV-M'>python3 docs/herramientas/generar_documentos.py</font>, que incorpora la nueva tabla a este informe."),
    ("p", "<b>Cota teórica esperada</b> (ley de Amdahl, sección 3.4 del informe de avance; modelo, no medición):"),
    ("table", ["Kernel", "f (secuencial)", "p = 2", "p = 4", "p = 8"], TABLA_AMDAHL, [0.2, 0.2, 0.2, 0.2, 0.2]),
    ("h1", "8. Control de efectos secundarios"),
    ("table", ["Efecto secundario", "Dónde ocurre", "Cómo se aísla"], [
        ["Lectura/escritura de archivos y procesos", "Java: RepositorioImagenArchivo, FormatoPGM, ProcesoExterno", "Detrás de interfaces; el dominio no hace E/S."],
        ["stdin/stdout, argumentos, códigos de salida", "Python: solo cli.py (Imperative Shell)", "Los módulos pgm, pixeles, segmentacion y option son puros (Functional Core)."],
        ["Escritura de arreglos en paralelo", "C++: convolucionar()", "Cada hilo escribe filas disjuntas; la entrada solo se lee."],
        ["Estado compartido entre hilos", "Java: RepositorioImagenEnMemoria", "ConcurrentHashMap con valores inmutables."],
        ["Archivos temporales", "ProcesoExterno", "Nombres únicos por llamada; se borran en finally."],
    ], [0.30, 0.35, 0.35]),
    ("h1", "9. Pruebas y validación"),
    ("table", ["Suite", "Pruebas", "Qué cubre"], [
        ["Python (unittest)", "12", "Option, pureza, currificación, compose, máscara, componentes, pila con 20 000 pasos, PGM"],
        ["Java (PruebasTac)", "18", "Aliasing, inmodificabilidad, Factory Method, integración real de 3 módulos, DIP con falsos, lote concurrente, estrés, propagación de errores"],
        ["C++ (bench)", "-", "Igualdad bit a bit secuencial vs paralelo en cada configuración"],
    ], [0.22, 0.10, 0.68]),
    ("h1", "10. Limitaciones y trabajo futuro"),
    ("bullets", [
        "Datos sintéticos: faltaría validar con imágenes reales (DICOM) y umbrales adaptativos.",
        "Integración por procesos y archivos: simple y portable, pero con sobrecosto; JNI/JNA o sockets lo reducirían.",
        "Segmentación inmutable O(M²): estructuras persistentes la bajarían a O(M log M).",
        "Gauss 5×5 es separable: dos pasadas 1D bajarían de 25 a 10 multiplicaciones por píxel; también se puede paralelizar el padding (hoy secuencial).",
        "Medir speedup en un equipo multinúcleo (pendiente, ver sección 7).",
    ]),
    ("h1", "11. Conclusiones"),
    ("p", "Cada paradigma resolvió la parte donde más aporta: el imperativo, el control de memoria y el paralelismo; el orientado a objetos, el modelado del dominio con "
          "invariantes protegidos y bajo acoplamiento; el funcional, la transformación de datos sin efectos secundarios. La integración por contratos permitió "
          "probar cada módulo por separado y luego juntos."),
    ("h1", "Apéndice. Cómo ejecutar"),
    ("code", "make all      # compila C++ y Java\nmake test     # 12 pruebas Python + 18 pruebas Java\nmake demo     # analiza tac_01 y un lote concurrente\nmake bench    # benchmark secuencial vs paralelo (docs/benchmarks.md)\n"
             "python3 datos/generar_tac.py   # regenera las TAC sinteticas"),
]
generar(b, f"{DOCS}/Entrega_Final/Informe_Tecnico_Final.pdf", md=f"{DOCS}/Entrega_Final/Informe_Tecnico_Final.md", encabezado=ENC, ruta_base=DOCS)
print("Informe_Tecnico_Final ok")
