package tac.analisis;

import tac.dominio.EstudioMedico;
import tac.dominio.ResultadoAnalisis;
import tac.integracion.IntegracionException;

/** Producto del Factory Method. */
public interface AnalizadorMedico {
    ResultadoAnalisis analizar(EstudioMedico estudio) throws IntegracionException;

    String nombre();
}
