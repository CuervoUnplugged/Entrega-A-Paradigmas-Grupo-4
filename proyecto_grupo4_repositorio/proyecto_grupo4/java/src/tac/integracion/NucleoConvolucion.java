package tac.integracion;

/** Contrato del Modulo 1 (kernel C++). Las clases de analisis dependen de esta interfaz (DIP). */
public interface NucleoConvolucion {
    /** Devuelve la magnitud del gradiente (0..255) de una imagen de 8 bits. */
    int[] detectarBordes(int ancho, int alto, int[] pixeles) throws IntegracionException;
}
