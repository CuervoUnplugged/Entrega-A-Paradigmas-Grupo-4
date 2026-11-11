package tac.util;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;

/** Lectura/escritura de PGM P2 (texto). Clase utilitaria sin estado. */
public final class FormatoPGM {
    private FormatoPGM() {
    }

    /** Imagen leida de un PGM. */
    public record Imagen(int ancho, int alto, int maxval, int[] pixeles) {
    }

    public static Imagen leer(Path archivo) throws IOException {
        String[] tokens = Files.readAllLines(archivo).stream()
                .filter(l -> !l.stripLeading().startsWith("#"))
                .flatMap(l -> Arrays.stream(l.trim().split("\\s+")))
                .filter(t -> !t.isEmpty())
                .toArray(String[]::new);
        if (tokens.length < 4 || !tokens[0].equals("P2")) {
            throw new IOException("PGM invalido (se espera P2): " + archivo);
        }
        int ancho = Integer.parseInt(tokens[1]);
        int alto = Integer.parseInt(tokens[2]);
        int maxval = Integer.parseInt(tokens[3]);
        if (tokens.length - 4 != ancho * alto) {
            throw new IOException("Cantidad de pixeles incorrecta en " + archivo);
        }
        int[] px = new int[ancho * alto];
        for (int i = 0; i < px.length; i++) {
            px[i] = Integer.parseInt(tokens[4 + i]);
        }
        return new Imagen(ancho, alto, maxval, px);
    }

    public static void escribir(Path archivo, int ancho, int alto, int maxval, int[] px) throws IOException {
        StringBuilder sb = new StringBuilder();
        sb.append("P2\n").append(ancho).append(' ').append(alto).append('\n').append(maxval).append('\n');
        for (int y = 0; y < alto; y++) {
            for (int x = 0; x < ancho; x++) {
                sb.append(px[y * ancho + x]).append(x + 1 < ancho ? ' ' : '\n');
            }
        }
        Files.writeString(archivo, sb.toString());
    }
}
