# Guía de sustentación (10 min en equipo + 10 min individual)

## Guion de 10 minutos (7 diapositivas)
1. **Portada y problema (1 min):** TAC → bordes → regiones sospechosas. Datos sintéticos.
2. **Arquitectura (1.5 min):** tres módulos; Java orquesta; archivos PGM como formato de intercambio.
3. **C++ (1.5 min):** Θ(W·H·K²), memoria contigua, padding, `omp parallel for` por filas.
4. **Java (1.5 min):** Factory Method, Template Method, DIP, copias defensivas, thread safety.
5. **Python (1.5 min):** pureza, map/filter/reduce, currificación, recursión de cola con trampolín, Option.
6. **Demo en vivo (2 min):** `make demo`; mostrar `salida/` y la figura de resultados.
7. **Resultados y cierre (0.5 min):** 30 pruebas en verde; honestidad sobre el speedup y los datos sintéticos.

## Preguntas probables y respuestas cortas
- **¿Por qué la convolución es Θ(W·H·K²)?** Cuatro sumatorias anidadas (y, x, i, j) con costo constante: c·H·W·K·K.
- **¿Por qué no hay condiciones de carrera?** Cada iteración `y` escribe solo la fila `y` de la salida; `pad` y el kernel solo se leen.
- **¿Hay deadlocks?** No usamos locks; solo la barrera implícita del `parallel for`.
- **¿Qué es el padding y por qué?** Copia con bordes replicados; evita `if` en el bucle interno y mantiene lecturas contiguas.
- **¿Gestión de memoria en C++?** `std::vector` en el Heap (RAII, sin `delete` manual); el kernel gaussiano de 5 valores en el Stack.
- **¿Qué es aliasing y cómo lo evitan?** Dos referencias al mismo arreglo mutable. `EstudioMedico` hace `clone()` al entrar y al salir; las listas usan `List.copyOf`.
- **¿VTable / JVM?** `analizar()` de `AnalizadorMedico` se despacha dinámicamente (invokeinterface/invokevirtual): la JVM busca el método en la tabla de métodos de la clase real (AnalizadorTumoral u AnalizadorOseo). `AnalizadorBase.analizar()` es `final`: no se sobrescribe.
- **¿Factory Method vs Abstract Factory?** Aquí una sola jerarquía de creadores con un método de fábrica; Abstract Factory crearía familias de objetos.
- **¿DIP en el proyecto?** `ServicioDiagnostico` depende de `RepositorioImagen` y `FabricaAnalizador`; las pruebas usan falsos sin C++ ni Python.
- **¿Es thread-safe el servicio?** Sí: sin estado mutable, archivos temporales únicos por llamada, `ConcurrentHashMap` y valores inmutables.
- **¿Qué es transparencia referencial?** Misma entrada, misma salida, sin efectos: se puede sustituir la llamada por su valor.
- **¿Python tiene TCO?** No. Usamos un trampolín: cada paso devuelve la siguiente llamada y un bucle la ejecuta (pila constante).
- **¿Por qué `Option`?** Hace explícito "puede no haber valor" (estudio sano) sin `None` ni excepciones.
- **¿Complejidad de la segmentación?** O(W·H + M²): copiar conjuntos inmutables cuesta; con estructuras mutables sería O(M).
- **¿Speedup real?** Lo medido aquí fue ≈1.0x en 1 hilo de hardware (resultado idéntico). Traigan la tabla de `make bench` de su máquina; la cota de Amdahl para K=5, p=4 es ≈3.6x (modelo).
- **¿Limitaciones?** Datos sintéticos, umbrales calibrados a mano, integración por procesos.
