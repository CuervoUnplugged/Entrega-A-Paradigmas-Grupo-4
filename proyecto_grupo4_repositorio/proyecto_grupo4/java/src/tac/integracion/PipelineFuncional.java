package tac.integracion;

import tac.dominio.ParametrosSegmentacion;
import tac.dominio.ResultadoSegmentacion;

/** Contrato del Modulo 3 (pipeline funcional en Python). */
public interface PipelineFuncional {
    /** Ventana nivel/ancho: lleva la imagen original (maxval) a 8 bits (0..255). */
    int[] normalizar(int ancho, int alto, int maxval, int[] pixeles, int nivel, int anchoVentana)
            throws IntegracionException;

    /** Segmenta regiones usando la imagen normalizada y el mapa de bordes. */
    ResultadoSegmentacion segmentar(int ancho, int alto, int[] normalizada, int[] bordes,
                                    ParametrosSegmentacion parametros) throws IntegracionException;
}
