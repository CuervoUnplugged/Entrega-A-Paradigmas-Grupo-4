package tac.repositorio;

import tac.dominio.TacException;

public class RepositorioException extends TacException {
    private static final long serialVersionUID = 1L;

    public RepositorioException(String mensaje) {
        super(mensaje);
    }

    public RepositorioException(String mensaje, Throwable causa) {
        super(mensaje, causa);
    }
}
