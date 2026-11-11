package tac.dominio;

import java.util.Objects;

/**
 * Estudio de imagen medica (una TAC). Es INMUTABLE: ningun metodo publico permite cambiar su estado
 * y el arreglo de pixeles se copia al entrar (constructor) y al salir (getPixeles) para evitar aliasing.
 */
public final class EstudioMedico {
    private final String idPaciente;
    private final String modalidad;
    private final int ancho;
    private final int alto;
    private final int maxval;
    private final int[] pixeles;

    public EstudioMedico(String idPaciente, String modalidad, int ancho, int alto, int maxval, int[] pixeles) {
        this.idPaciente = Objects.requireNonNull(idPaciente, "idPaciente");
        this.modalidad = Objects.requireNonNull(modalidad, "modalidad");
        Objects.requireNonNull(pixeles, "pixeles");
        if (ancho <= 0 || alto <= 0) {
            throw new IllegalArgumentException("Dimensiones invalidas");
        }
        if (maxval <= 0) {
            throw new IllegalArgumentException("maxval invalido");
        }
        if (pixeles.length != ancho * alto) {
            throw new IllegalArgumentException("La cantidad de pixeles no coincide con ancho*alto");
        }
        this.ancho = ancho;
        this.alto = alto;
        this.maxval = maxval;
        this.pixeles = pixeles.clone(); // copia defensiva de entrada
    }

    public String getIdPaciente() {
        return idPaciente;
    }

    public String getModalidad() {
        return modalidad;
    }

    public int getAncho() {
        return ancho;
    }

    public int getAlto() {
        return alto;
    }

    public int getMaxval() {
        return maxval;
    }

    public int[] getPixeles() {
        return pixeles.clone(); // copia defensiva de salida
    }

    public int getPixel(int x, int y) {
        if (x < 0 || x >= ancho || y < 0 || y >= alto) {
            throw new IndexOutOfBoundsException("Pixel fuera de rango");
        }
        return pixeles[y * ancho + x];
    }
}
