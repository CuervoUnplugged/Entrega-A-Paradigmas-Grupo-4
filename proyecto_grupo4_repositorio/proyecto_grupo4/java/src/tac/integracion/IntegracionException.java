package tac.integracion;

import tac.dominio.TacException;

public class IntegracionException extends TacException {
    private static final long serialVersionUID = 1L;

    public IntegracionException(String mensaje) {
        super(mensaje);
    }

    public IntegracionException(String mensaje, Throwable causa) {
        super(mensaje, causa);
    }
}
