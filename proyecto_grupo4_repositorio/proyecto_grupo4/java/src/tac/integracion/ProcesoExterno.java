package tac.integracion;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.concurrent.TimeUnit;

/**
 * Ejecuta un programa externo (C++ o Python) redirigiendo stdin/stdout a ARCHIVOS.
 * Con archivos no hay riesgo de bloqueo por buffers llenos. No tiene estado: es seguro entre hilos.
 */
final class ProcesoExterno {
    private ProcesoExterno() {
    }

    static void ejecutar(List<String> comando, Path stdin, Path stdout, long timeoutSegundos)
            throws IntegracionException {
        Path stderr = null;
        try {
            stderr = Files.createTempFile("tac-err-", ".txt");
            ProcessBuilder pb = new ProcessBuilder(comando);
            if (stdin != null) {
                pb.redirectInput(stdin.toFile());
            }
            pb.redirectOutput(stdout.toFile());
            pb.redirectError(stderr.toFile());
            Process p = pb.start();
            if (!p.waitFor(timeoutSegundos, TimeUnit.SECONDS)) {
                p.destroyForcibly();
                throw new IntegracionException("Tiempo agotado ejecutando: " + comando.get(0));
            }
            if (p.exitValue() != 0) {
                throw new IntegracionException("Fallo " + comando.get(0) + " (codigo " + p.exitValue() + "): "
                        + Files.readString(stderr).trim());
            }
        } catch (IOException e) {
            throw new IntegracionException("No se pudo ejecutar " + comando.get(0) + ": " + e.getMessage(), e);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt(); // se conserva la senal de interrupcion
            throw new IntegracionException("Ejecucion interrumpida", e);
        } finally {
            borrar(stderr);
        }
    }

    static Path temporal(String prefijo, String sufijo) throws IOException {
        return Files.createTempFile(prefijo, sufijo);
    }

    static void borrar(Path... archivos) {
        for (Path a : archivos) {
            if (a != null) {
                try {
                    Files.deleteIfExists(a);
                } catch (IOException ignorado) {
                    // no es critico: es un archivo temporal
                }
            }
        }
    }
}
