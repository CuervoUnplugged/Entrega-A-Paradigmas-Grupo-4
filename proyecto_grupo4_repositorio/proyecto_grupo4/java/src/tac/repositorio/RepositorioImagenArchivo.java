package tac.repositorio;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import java.util.regex.Pattern;
import java.util.stream.Stream;

import tac.dominio.EstudioMedico;
import tac.util.FormatoPGM;

/** Lee estudios desde archivos PGM de una carpeta. No guarda estado mutable. */
public class RepositorioImagenArchivo implements RepositorioImagen {
    private static final Pattern ID_VALIDO = Pattern.compile("[A-Za-z0-9_-]+");
    private final Path carpeta;

    public RepositorioImagenArchivo(Path carpeta) {
        this.carpeta = carpeta;
    }

    @Override
    public EstudioMedico cargar(String id) throws RepositorioException {
        if (!ID_VALIDO.matcher(id).matches()) { // evita rutas como ../../x
            throw new RepositorioException("Identificador invalido: " + id);
        }
        Path archivo = carpeta.resolve(id + ".pgm");
        try {
            FormatoPGM.Imagen img = FormatoPGM.leer(archivo);
            return new EstudioMedico(id, "TAC", img.ancho(), img.alto(), img.maxval(), img.pixeles());
        } catch (IOException | RuntimeException e) {
            throw new RepositorioException("No se pudo cargar " + id + ": " + e.getMessage(), e);
        }
    }

    @Override
    public List<String> listarIds() throws RepositorioException {
        try (Stream<Path> s = Files.list(carpeta)) {
            return s.map(p -> p.getFileName().toString())
                    .filter(n -> n.endsWith(".pgm"))
                    .map(n -> n.substring(0, n.length() - 4))
                    .sorted()
                    .toList(); // lista inmodificable
        } catch (IOException e) {
            throw new RepositorioException("No se pudo listar " + carpeta, e);
        }
    }
}
