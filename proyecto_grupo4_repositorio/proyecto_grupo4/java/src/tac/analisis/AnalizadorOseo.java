package tac.analisis;

import tac.dominio.ParametrosSegmentacion;
import tac.integracion.NucleoConvolucion;
import tac.integracion.PipelineFuncional;

/** Segmenta hueso (intensidad muy alta), por ejemplo el craneo. */
public class AnalizadorOseo extends AnalizadorBase {
    public AnalizadorOseo(NucleoConvolucion nucleo, PipelineFuncional pipeline) {
        super(nucleo, pipeline);
    }

    @Override
    protected ParametrosSegmentacion parametros() {
        return new ParametrosSegmentacion(1700, 2400, 240, 255, 60, 200);
    }

    @Override
    public String nombre() {
        return "Analizador oseo";
    }
}
