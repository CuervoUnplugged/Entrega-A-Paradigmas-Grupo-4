package tac.analisis;

import tac.dominio.EstudioMedico;
import tac.dominio.ParametrosSegmentacion;
import tac.dominio.ResultadoAnalisis;
import tac.dominio.ResultadoSegmentacion;
import tac.integracion.IntegracionException;
import tac.integracion.NucleoConvolucion;
import tac.integracion.PipelineFuncional;

/**
 * Clase abstracta con el flujo comun (Template Method): normalizar (funcional) -> bordes (C++) ->
 * segmentar (funcional). Las subclases solo definen los parametros (polimorfismo + OCP).
 */
public abstract class AnalizadorBase implements AnalizadorMedico {
    private final NucleoConvolucion nucleo;
    private final PipelineFuncional pipeline;

    protected AnalizadorBase(NucleoConvolucion nucleo, PipelineFuncional pipeline) {
        this.nucleo = nucleo;
        this.pipeline = pipeline;
    }

    /** Punto de variacion: cada tipo de analisis decide su banda de intensidad, umbrales, etc. */
    protected abstract ParametrosSegmentacion parametros();

    /** Gancho opcional: validaciones extra antes de procesar. */
    protected void validar(EstudioMedico estudio) {
        if (estudio.getAncho() < 16 || estudio.getAlto() < 16) {
            throw new IllegalArgumentException("Imagen demasiado pequena para analizar");
        }
    }

    @Override
    public final ResultadoAnalisis analizar(EstudioMedico estudio) throws IntegracionException {
        validar(estudio);
        ParametrosSegmentacion p = parametros();
        int ancho = estudio.getAncho();
        int alto = estudio.getAlto();
        int[] normalizada = pipeline.normalizar(ancho, alto, estudio.getMaxval(), estudio.getPixeles(),
                p.nivel(), p.anchoVentana());
        int[] bordes = nucleo.detectarBordes(ancho, alto, normalizada);
        ResultadoSegmentacion seg = pipeline.segmentar(ancho, alto, normalizada, bordes, p);
        return new ResultadoAnalisis(estudio.getIdPaciente(), ancho, alto, bordes, seg.mascara(), seg.regiones());
    }
}
