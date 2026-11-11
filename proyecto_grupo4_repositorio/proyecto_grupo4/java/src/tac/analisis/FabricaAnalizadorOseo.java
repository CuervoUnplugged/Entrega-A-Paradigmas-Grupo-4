package tac.analisis;

import tac.integracion.NucleoConvolucion;
import tac.integracion.PipelineFuncional;

public class FabricaAnalizadorOseo extends FabricaAnalizador {
    public FabricaAnalizadorOseo(NucleoConvolucion nucleo, PipelineFuncional pipeline) {
        super(nucleo, pipeline);
    }

    @Override
    protected AnalizadorMedico crearAnalizador() {
        return new AnalizadorOseo(nucleo, pipeline);
    }
}
