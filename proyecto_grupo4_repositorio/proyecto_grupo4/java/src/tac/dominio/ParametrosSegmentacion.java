package tac.dominio;

/**
 * Parametros de un analizador: ventana nivel/ancho (12 bits -> 8 bits), banda de intensidad a segmentar,
 * umbral de borde (pixeles con borde >= umbral se excluyen) y area minima de una region.
 */
public record ParametrosSegmentacion(int nivel, int anchoVentana, int bandaMin, int bandaMax,
                                     int umbralBorde, int areaMinima) {
    public ParametrosSegmentacion {
        if (anchoVentana <= 0) {
            throw new IllegalArgumentException("anchoVentana debe ser positivo");
        }
        if (bandaMin < 0 || bandaMax > 255 || bandaMin > bandaMax) {
            throw new IllegalArgumentException("Banda de intensidad invalida");
        }
        if (areaMinima < 1) {
            throw new IllegalArgumentException("areaMinima debe ser >= 1");
        }
    }
}
