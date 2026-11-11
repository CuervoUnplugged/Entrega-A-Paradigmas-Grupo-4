package tac.analisis;

import tac.dominio.EstudioMedico;
import tac.dominio.ResultadoAnalisis;
import tac.integracion.IntegracionException;
import tac.integracion.NucleoConvolucion;
import tac.integracion.PipelineFuncional;

/**
 * Creator del patron Factory Method. El metodo de fabrica es crearAnalizador(); las subclases deciden
 * QUE analizador instanciar. Agregar un tipo nuevo = agregar una subclase (OCP), sin tocar este codigo.
 */
public abstract class FabricaAnalizador {
    protected final NucleoConvolucion nucleo;
    protected final PipelineFuncional pipeline;

    protected FabricaAnalizador(NucleoConvolucion nucleo, PipelineFuncional pipeline) {
        this.nucleo = nucleo;
        this.pipeline = pipeline;
    }

    /** Factory Method. */
    protected abstract AnalizadorMedico crearAnalizador();

    public final ResultadoAnalisis analizar(EstudioMedico estudio) throws IntegracionException {
        return crearAnalizador().analizar(estudio);
    }

    public final String nombreAnalizador() {
        return crearAnalizador().nombre();
    }
}
