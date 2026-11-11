package tac.repositorio;

import java.util.List;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

import tac.dominio.EstudioMedico;

/** Repositorio en memoria, thread-safe: ConcurrentHashMap + valores inmutables (EstudioMedico). */
public class RepositorioImagenEnMemoria implements RepositorioImagen {
    private final ConcurrentMap<String, EstudioMedico> estudios = new ConcurrentHashMap<>();

    public void guardar(EstudioMedico estudio) {
        estudios.put(estudio.getIdPaciente(), estudio);
    }

    @Override
    public EstudioMedico cargar(String id) throws RepositorioException {
        EstudioMedico e = estudios.get(id);
        if (e == null) {
            throw new RepositorioException("No existe el estudio " + id);
        }
        return e;
    }

    @Override
    public List<String> listarIds() {
        return estudios.keySet().stream().sorted().toList();
    }
}
