package tac.dominio;

import java.util.List;

/** Respuesta del modulo funcional: regiones encontradas y mascara etiquetada. Inmutable. */
public record ResultadoSegmentacion(List<RegionTumoral> regiones, int[] mascara) {
    public ResultadoSegmentacion {
        regiones = List.copyOf(regiones); // lista inmodificable (copia)
        mascara = mascara.clone();
    }

    @Override
    public int[] mascara() {
        return mascara.clone();
    }
}
