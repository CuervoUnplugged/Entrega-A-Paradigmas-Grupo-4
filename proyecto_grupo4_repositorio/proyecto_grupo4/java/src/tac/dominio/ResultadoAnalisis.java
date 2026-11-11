package tac.dominio;

import java.util.List;
import java.util.Optional;

/** Resultado final de analizar un estudio. Inmutable: copias defensivas de listas y arreglos. */
public record ResultadoAnalisis(String idPaciente, int ancho, int alto, int[] bordes, int[] mascara,
                                List<RegionTumoral> regiones) {
    public ResultadoAnalisis {
        regiones = List.copyOf(regiones);
        bordes = bordes.clone();
        mascara = mascara.clone();
    }

    @Override
    public int[] bordes() {
        return bordes.clone();
    }

    @Override
    public int[] mascara() {
        return mascara.clone();
    }

    public boolean hayRegiones() {
        return !regiones.isEmpty();
    }

    public Optional<RegionTumoral> regionMayor() {
        return regiones.stream().max((a, b) -> Integer.compare(a.area(), b.area()));
    }
}
