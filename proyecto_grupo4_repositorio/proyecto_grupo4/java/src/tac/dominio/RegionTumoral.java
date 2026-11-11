package tac.dominio;

/** Region segmentada (caja contenedora y centroide). Record: inmutable por construccion. */
public record RegionTumoral(int etiqueta, int area, int xMin, int yMin, int xMax, int yMax, double cx, double cy) {
    public RegionTumoral {
        if (area <= 0) {
            throw new IllegalArgumentException("El area debe ser positiva");
        }
        if (xMax < xMin || yMax < yMin) {
            throw new IllegalArgumentException("Caja contenedora invalida");
        }
    }
}
