package tac.integracion;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;

import tac.dominio.ParametrosSegmentacion;
import tac.dominio.RegionTumoral;
import tac.dominio.ResultadoSegmentacion;
import tac.util.FormatoPGM;

/** Adaptador: llama a funcional/cli.py (Python). Sin estado mutable. */
public class PipelineFuncionalPython implements PipelineFuncional {
    private final String python;
    private final Path script;

    public PipelineFuncionalPython(String python, Path script) {
        this.python = python;
        this.script = script;
    }

    @Override
    public int[] normalizar(int ancho, int alto, int maxval, int[] pixeles, int nivel, int anchoVentana)
            throws IntegracionException {
        Path entrada = null;
        Path salida = null;
        try {
            entrada = ProcesoExterno.temporal("tac-raw-", ".pgm");
            salida = ProcesoExterno.temporal("tac-norm-", ".pgm");
            FormatoPGM.escribir(entrada, ancho, alto, maxval, pixeles);
            ProcesoExterno.ejecutar(List.of(python, script.toString(), "normalizar",
                    "--nivel", String.valueOf(nivel), "--ancho", String.valueOf(anchoVentana)), entrada, salida, 60);
            return FormatoPGM.leer(salida).pixeles();
        } catch (IOException e) {
            throw new IntegracionException("Error de E/S con el pipeline funcional: " + e.getMessage(), e);
        } finally {
            ProcesoExterno.borrar(entrada, salida);
        }
    }

    @Override
    public ResultadoSegmentacion segmentar(int ancho, int alto, int[] normalizada, int[] bordes,
                                           ParametrosSegmentacion p) throws IntegracionException {
        Path imagen = null;
        Path mapaBordes = null;
        Path mascara = null;
        Path texto = null;
        try {
            imagen = ProcesoExterno.temporal("tac-seg-img-", ".pgm");
            mapaBordes = ProcesoExterno.temporal("tac-seg-bor-", ".pgm");
            mascara = ProcesoExterno.temporal("tac-seg-msk-", ".pgm");
            texto = ProcesoExterno.temporal("tac-seg-txt-", ".txt");
            FormatoPGM.escribir(imagen, ancho, alto, 255, normalizada);
            FormatoPGM.escribir(mapaBordes, ancho, alto, 255, bordes);
            ProcesoExterno.ejecutar(List.of(python, script.toString(), "segmentar",
                    "--imagen", imagen.toString(), "--bordes", mapaBordes.toString(),
                    "--banda", String.valueOf(p.bandaMin()), String.valueOf(p.bandaMax()),
                    "--umbral-borde", String.valueOf(p.umbralBorde()),
                    "--area-min", String.valueOf(p.areaMinima()),
                    "--salida-mascara", mascara.toString()), null, texto, 120);
            return new ResultadoSegmentacion(leerRegiones(Files.readAllLines(texto)),
                    FormatoPGM.leer(mascara).pixeles());
        } catch (IOException e) {
            throw new IntegracionException("Error de E/S con el pipeline funcional: " + e.getMessage(), e);
        } finally {
            ProcesoExterno.borrar(imagen, mapaBordes, mascara, texto);
        }
    }

    /** Formato: "SIN_REGION" o lineas "REGION etiqueta area xMin yMin xMax yMax cx cy". */
    private static List<RegionTumoral> leerRegiones(List<String> lineas) throws IntegracionException {
        List<RegionTumoral> regiones = new ArrayList<>();
        for (String linea : lineas) {
            if (!linea.startsWith("REGION ")) {
                continue;
            }
            String[] t = linea.trim().split("\\s+");
            if (t.length != 9) {
                throw new IntegracionException("Linea de region invalida: " + linea);
            }
            regiones.add(new RegionTumoral(Integer.parseInt(t[1]), Integer.parseInt(t[2]),
                    Integer.parseInt(t[3]), Integer.parseInt(t[4]), Integer.parseInt(t[5]),
                    Integer.parseInt(t[6]), Double.parseDouble(t[7]), Double.parseDouble(t[8])));
        }
        return regiones;
    }
}
