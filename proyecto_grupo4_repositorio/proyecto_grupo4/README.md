# Proyecto Final Integrador - Grupo 4
**Segmentación y procesamiento de imágenes médicas (TAC) por visión artificial**
Paradigmas de Programación (SIST0176) · Universidad Sergio Arboleda · ICCIA

Sistema de tres módulos conectados, cada uno en su paradigma:

| Módulo | Paradigma / lenguaje | Carpeta | Qué hace |
|---|---|---|---|
| 1 | Imperativo · C++17 + OpenMP | `cpp/` | Convolución 2D (Gauss 5x5 + Sobel 3x3) sobre memoria contigua, paralela por filas |
| 2 | Orientado a objetos · Java 17 | `java/` | Dominio inmutable, Factory Method, DIP, orquestación y lotes concurrentes |
| 3 | Funcional · Python 3.10+ | `funcional/` | Normalización, máscara, segmentación con recursión de cola y `Option` |

Flujo: `Java carga el estudio → Python normaliza → C++ calcula bordes → Python segmenta → Java entrega ResultadoAnalisis`.

## Requisitos
`g++` con OpenMP (C++17), JDK 17+, Python 3.10+ y `make`. (Solo para regenerar PDFs: `reportlab`, `matplotlib`, `pillow`.)

## Uso
```bash
make all      # compila C++ (build/convolve, build/bench) y Java (build/java)
make test     # 12 pruebas Python + 18 pruebas Java
make demo     # analiza tac_01 y un lote concurrente; escribe salida/*.pgm
make bench    # benchmark secuencial vs paralelo -> docs/benchmarks.md
java -cp build/java tac.app.Main analizar tac_02 --tipo tumoral   # o --tipo oseo
```
Los datos son TAC **sintéticas** (`datos/generar_tac.py`), no imágenes de pacientes.

## Estructura
```
cpp/         kernel C++ (convolucion.*, main.cpp, bench.cpp)
java/src/tac dominio/ repositorio/ integracion/ analisis/ app/ pruebas/ util/
funcional/   option.py pixeles.py segmentacion.py pgm.py cli.py tests/
datos/       TAC sintéticas y generador
docs/        Entrega_Parcial/ Entrega_Final/ uml/ figuras/ herramientas/ benchmarks.md
```

## Entregas (Git)
- Etiqueta `checkpoint-30`: entrega parcial (Sesión 3).
- Etiqueta `entrega-final`: entrega final (Sesión 5).

## Pendiente del grupo
Ejecutar `make bench` en un computador multinúcleo para obtener el speedup real y regenerar los informes con
`python3 docs/herramientas/generar_documentos.py`. Completar nombres de integrantes en las portadas
(`docs/herramientas/generar_documentos.py`).
