package tac.analisis;

import tac.dominio.ParametrosSegmentacion;
import tac.integracion.NucleoConvolucion;
import tac.integracion.PipelineFuncional;

/** Busca regiones de tejido denso (intensidad media-alta) como posibles tumores. */
public class AnalizadorTumoral extends AnalizadorBase {
    public AnalizadorTumoral(NucleoConvolucion nucleo, PipelineFuncional pipeline) {
        super(nucleo, pipeline);
    }

    @Override
    protected ParametrosSegmentacion parametros() {
        return new ParametrosSegmentacion(1700, 2400, 100, 170, 30, 30);
    }

    @Override
    public String nombre() {
        return "Analizador tumoral";
    }
}
