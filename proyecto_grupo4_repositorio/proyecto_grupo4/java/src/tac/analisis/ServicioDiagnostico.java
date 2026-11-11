package tac.analisis;

import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.Callable;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Future;

import tac.dominio.ResultadoAnalisis;
import tac.dominio.TacException;
import tac.repositorio.RepositorioImagen;

/**
 * Orquesta el caso de uso. Depende de ABSTRACCIONES (RepositorioImagen, FabricaAnalizador), no de clases
 * concretas (DIP). No tiene estado mutable, por eso varios hilos pueden usarla a la vez.
 */
public class ServicioDiagnostico {
    private final RepositorioImagen repositorio;
    private final FabricaAnalizador fabrica;

    public ServicioDiagnostico(RepositorioImagen repositorio, FabricaAnalizador fabrica) {
        this.repositorio = repositorio;
        this.fabrica = fabrica;
    }

    public ResultadoAnalisis analizar(String id) throws TacException {
        return fabrica.analizar(repositorio.cargar(id));
    }

    /** Analiza varios estudios en paralelo (pool de hilos). Devuelve un mapa inmodificable. */
    public Map<String, ResultadoAnalisis> analizarLote(List<String> ids, int hilos) throws TacException {
        ExecutorService pool = Executors.newFixedThreadPool(Math.max(1, hilos));
        try {
            List<Future<ResultadoAnalisis>> futuros = new ArrayList<>();
            for (String id : ids) {
                Callable<ResultadoAnalisis> tarea = () -> analizar(id);
                futuros.add(pool.submit(tarea));
            }
            Map<String, ResultadoAnalisis> resultados = new LinkedHashMap<>();
            for (int i = 0; i < ids.size(); i++) {
                try {
                    resultados.put(ids.get(i), futuros.get(i).get());
                } catch (ExecutionException e) {
                    if (e.getCause() instanceof TacException te) {
                        throw te;
                    }
                    throw new TacException("Error analizando " + ids.get(i), e.getCause());
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    throw new TacException("Lote interrumpido", e);
                }
            }
            return Collections.unmodifiableMap(resultados);
        } finally {
            pool.shutdown();
        }
    }
}
