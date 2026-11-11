package tac.repositorio;

import java.util.List;

import tac.dominio.EstudioMedico;

/** Abstraccion de donde viven los estudios (DIP: los servicios dependen de esta interfaz). */
public interface RepositorioImagen {
    EstudioMedico cargar(String id) throws RepositorioException;

    List<String> listarIds() throws RepositorioException;
}
