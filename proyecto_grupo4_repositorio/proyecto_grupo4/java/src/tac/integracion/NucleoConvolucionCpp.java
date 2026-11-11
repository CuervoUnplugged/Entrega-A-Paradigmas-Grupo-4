package tac.integracion;

import java.io.IOException;
import java.nio.file.Path;
import java.util.List;

import tac.util.FormatoPGM;

/** Adaptador: llama al ejecutable C++ 'convolve' (OpenMP). Sin estado mutable. */
public class NucleoConvolucionCpp implements NucleoConvolucion {
    private final Path ejecutable;
    private final int hilos; // 0 = los que decida OpenMP

    public NucleoConvolucionCpp(Path ejecutable, int hilos) {
        this.ejecutable = ejecutable;
        this.hilos = hilos;
    }

    @Override
    public int[] detectarBordes(int ancho, int alto, int[] pixeles) throws IntegracionException {
        Path entrada = null;
        Path salida = null;
        try {
            entrada = ProcesoExterno.temporal("tac-in-", ".pgm");
            salida = ProcesoExterno.temporal("tac-out-", ".pgm");
            FormatoPGM.escribir(entrada, ancho, alto, 255, pixeles);
            List<String> cmd = hilos > 0
                    ? List.of(ejecutable.toString(), "--modo", "bordes", "--hilos", String.valueOf(hilos))
                    : List.of(ejecutable.toString(), "--modo", "bordes");
            ProcesoExterno.ejecutar(cmd, entrada, salida, 60);
            return FormatoPGM.leer(salida).pixeles();
        } catch (IOException e) {
            throw new IntegracionException("Error de E/S con el nucleo C++: " + e.getMessage(), e);
        } finally {
            ProcesoExterno.borrar(entrada, salida);
        }
    }
}
