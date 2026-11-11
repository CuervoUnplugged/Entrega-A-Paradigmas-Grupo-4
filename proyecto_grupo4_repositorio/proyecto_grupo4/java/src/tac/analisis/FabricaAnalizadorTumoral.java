package tac.analisis;

import tac.integracion.NucleoConvolucion;
import tac.integracion.PipelineFuncional;

public class FabricaAnalizadorTumoral extends FabricaAnalizador {
    public FabricaAnalizadorTumoral(NucleoConvolucion nucleo, PipelineFuncional pipeline) {
        super(nucleo, pipeline);
    }

    @Override
    protected AnalizadorMedico crearAnalizador() {
        return new AnalizadorTumoral(nucleo, pipeline);
    }
}
