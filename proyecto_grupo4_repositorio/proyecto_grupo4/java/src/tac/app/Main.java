package tac.app;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.Map;

import tac.analisis.FabricaAnalizador;
import tac.analisis.FabricaAnalizadorOseo;
import tac.analisis.FabricaAnalizadorTumoral;
import tac.analisis.ServicioDiagnostico;
import tac.dominio.RegionTumoral;
import tac.dominio.ResultadoAnalisis;
import tac.dominio.TacException;
import tac.integracion.NucleoConvolucionCpp;
import tac.integracion.PipelineFuncionalPython;
import tac.repositorio.RepositorioImagen;
import tac.repositorio.RepositorioImagenArchivo;
import tac.util.FormatoPGM;

/**
 * Punto de entrada.
 *   analizar <id> [--tipo tumoral|oseo] [--hilos N]
 *   lote [--tipo tumoral|oseo] [--hilos N]
 * Rutas configurables con -Dtac.cpp, -Dtac.py, -Dtac.python, -Dtac.datos, -Dtac.salida.
 */
public final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        if (args.length == 0) {
            System.err.println("Uso: analizar <id> [--tipo tumoral|oseo] | lote [--hilos N]");
            System.exit(2);
        }
        String tipo = "tumoral";
        int hilos = 2;
        String id = null;
        for (int i = 1; i < args.length; i++) {
            switch (args[i]) {
                case "--tipo" -> tipo = args[++i];
                case "--hilos" -> hilos = Integer.parseInt(args[++i]);
                default -> id = args[i];
            }
        }
        try {
            Path datos = Path.of(System.getProperty("tac.datos", "datos"));
            Path salida = Path.of(System.getProperty("tac.salida", "salida"));
            Files.createDirectories(salida);
            RepositorioImagen repo = new RepositorioImagenArchivo(datos);
            FabricaAnalizador fabrica = crearFabrica(tipo);
            ServicioDiagnostico servicio = new ServicioDiagnostico(repo, fabrica);
            System.out.println("Analizador: " + fabrica.nombreAnalizador());

            if (args[0].equals("analizar")) {
                if (id == null) {
                    throw new TacException("Falta el id del estudio");
                }
                mostrar(servicio.analizar(id), salida);
            } else if (args[0].equals("lote")) {
                Map<String, ResultadoAnalisis> res = servicio.analizarLote(repo.listarIds(), hilos);
                res.values().forEach(r -> mostrarSeguro(r, salida));
            } else {
                throw new TacException("Comando desconocido: " + args[0]);
            }
        } catch (TacException | IOException e) {
            System.err.println("Error: " + e.getMessage());
            System.exit(1);
        }
    }

    static FabricaAnalizador crearFabrica(String tipo) throws TacException {
        Path cpp = Path.of(System.getProperty("tac.cpp", "build/convolve"));
        Path py = Path.of(System.getProperty("tac.py", "funcional/cli.py"));
        String python = System.getProperty("tac.python", "python3");
        var nucleo = new NucleoConvolucionCpp(cpp, 0);
        var pipeline = new PipelineFuncionalPython(python, py);
        return switch (tipo) {
            case "tumoral" -> new FabricaAnalizadorTumoral(nucleo, pipeline);
            case "oseo" -> new FabricaAnalizadorOseo(nucleo, pipeline);
            default -> throw new TacException("Tipo de analisis desconocido: " + tipo);
        };
    }

    private static void mostrarSeguro(ResultadoAnalisis r, Path salida) {
        try {
            mostrar(r, salida);
        } catch (IOException e) {
            System.err.println("No se pudo escribir la salida de " + r.idPaciente() + ": " + e.getMessage());
        }
    }

    private static void mostrar(ResultadoAnalisis r, Path salida) throws IOException {
        System.out.println("--- Estudio " + r.idPaciente() + " (" + r.ancho() + "x" + r.alto() + ")");
        if (!r.hayRegiones()) {
            System.out.println("Sin regiones sospechosas.");
        } else {
            System.out.println("Regiones encontradas: " + r.regiones().size());
            for (RegionTumoral g : r.regiones()) {
                System.out.printf(java.util.Locale.ROOT,
                        "  #%d area=%d px  caja=[%d,%d]-[%d,%d]  centro=(%.1f, %.1f)%n",
                        g.etiqueta(), g.area(), g.xMin(), g.yMin(), g.xMax(), g.yMax(), g.cx(), g.cy());
            }
        }
        FormatoPGM.escribir(salida.resolve(r.idPaciente() + "_bordes.pgm"), r.ancho(), r.alto(), 255, r.bordes());
        FormatoPGM.escribir(salida.resolve(r.idPaciente() + "_mascara.pgm"), r.ancho(), r.alto(), 255, r.mascara());
    }
}
