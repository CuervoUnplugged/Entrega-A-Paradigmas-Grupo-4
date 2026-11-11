package tac.dominio;

/** Excepcion base (verificada) del sistema. */
public class TacException extends Exception {
    private static final long serialVersionUID = 1L;

    public TacException(String mensaje) {
        super(mensaje);
    }

    public TacException(String mensaje, Throwable causa) {
        super(mensaje, causa);
    }
}
