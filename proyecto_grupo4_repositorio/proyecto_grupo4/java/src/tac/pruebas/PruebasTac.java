package tac.pruebas;

import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;

import tac.analisis.AnalizadorMedico;
import tac.analisis.FabricaAnalizador;
import tac.analisis.FabricaAnalizadorOseo;
import tac.analisis.FabricaAnalizadorTumoral;
import tac.analisis.ServicioDiagnostico;
import tac.dominio.EstudioMedico;
import tac.dominio.ParametrosSegmentacion;
import tac.dominio.RegionTumoral;
import tac.dominio.ResultadoAnalisis;
import tac.dominio.ResultadoSegmentacion;
import tac.integracion.IntegracionException;
import tac.integracion.NucleoConvolucion;
import tac.integracion.NucleoConvolucionCpp;
import tac.integracion.PipelineFuncional;
import tac.integracion.PipelineFuncionalPython;
import tac.repositorio.RepositorioImagenArchivo;
import tac.repositorio.RepositorioImagenEnMemoria;

/** Pruebas sin librerias externas. Ejecutar desde la raiz del proyecto: make test. */
public final class PruebasTac {
    private static int fallos = 0;
    private static int total = 0;

    private PruebasTac() {
    }

    private static void verificar(String nombre, boolean ok) {
        total++;
        if (!ok) {
            fallos++;
        }
        System.out.println((ok ? "[OK]    " : "[FALLO] ") + nombre);
    }

    private static NucleoConvolucion nucleo() {
        return new NucleoConvolucionCpp(Path.of("build/convolve"), 0);
    }

    private static PipelineFuncional pipeline() {
        return new PipelineFuncionalPython("python3", Path.of("funcional/cli.py"));
    }

    public static void main(String[] args) throws Exception {
        pruebasAliasing();
        pruebasFabrica();
        pruebasIntegracion();
        pruebasDIPconFalsos();
        pruebasThreadSafety();
        System.out.println("\n" + (total - fallos) + "/" + total + " pruebas correctas");
        System.exit(fallos == 0 ? 0 : 1);
    }

    // ---- Inmutabilidad y prevencion de aliasing ----
    static void pruebasAliasing() {
        int[] original = {1, 2, 3, 4};
        EstudioMedico e = new EstudioMedico("p1", "TAC", 2, 2, 255, original);
        original[0] = 99; // el que creo el estudio intenta cambiarlo despues
        verificar("Copia defensiva de entrada (constructor)", e.getPixel(0, 0) == 1);

        int[] salida = e.getPixeles();
        salida[1] = 77; // el que lee intenta cambiarlo
        verificar("Copia defensiva de salida (getPixeles)", e.getPixel(1, 0) == 2);
        verificar("getPixeles devuelve objetos distintos", e.getPixeles() != e.getPixeles());

        List<RegionTumoral> regiones = new ArrayList<>(List.of(new RegionTumoral(1, 5, 0, 0, 1, 1, 0.5, 0.5)));
        ResultadoAnalisis r = new ResultadoAnalisis("p1", 2, 2, new int[4], new int[4], regiones);
        regiones.clear();
        verificar("Lista copiada: vaciar la original no afecta al resultado", r.regiones().size() == 1);
        boolean lanzo = false;
        try {
            r.regiones().add(new RegionTumoral(2, 5, 0, 0, 1, 1, 0.5, 0.5));
        } catch (UnsupportedOperationException ex) {
            lanzo = true;
        }
        verificar("Lista del resultado es inmodificable", lanzo);
        int[] m = r.mascara();
        m[0] = 5;
        verificar("Mascara del resultado protegida con copia", r.mascara()[0] == 0);

        boolean invalido = false;
        try {
            new EstudioMedico("p", "TAC", 2, 2, 255, new int[3]);
        } catch (IllegalArgumentException ex) {
            invalido = true;
        }
        verificar("El constructor protege el invariante ancho*alto", invalido);
    }

    // ---- Factory Method y polimorfismo ----
    static void pruebasFabrica() {
        FabricaAnalizador t = new FabricaAnalizadorTumoral(nucleo(), pipeline());
        FabricaAnalizador o = new FabricaAnalizadorOseo(nucleo(), pipeline());
        verificar("Fabrica tumoral crea AnalizadorTumoral", t.nombreAnalizador().equals("Analizador tumoral"));
        verificar("Fabrica osea crea AnalizadorOseo", o.nombreAnalizador().equals("Analizador oseo"));
    }

    // ---- Integracion real: Java -> Python -> C++ -> Python ----
    static void pruebasIntegracion() throws Exception {
        var repo = new RepositorioImagenArchivo(Path.of("datos"));
        var servicio = new ServicioDiagnostico(repo, new FabricaAnalizadorTumoral(nucleo(), pipeline()));
        ResultadoAnalisis r1 = servicio.analizar("tac_01");
        verificar("tac_01 tiene 2 regiones", r1.regiones().size() == 2);
        verificar("tac_01: region mayor cerca de (100,108)",
                r1.regionMayor().map(g -> Math.abs(g.cx() - 100) < 3 && Math.abs(g.cy() - 108) < 3).orElse(false));
        verificar("tac_02 tiene 1 region (tumor irregular unido)", servicio.analizar("tac_02").regiones().size() == 1);
        verificar("tac_03 (sano) no tiene regiones", !servicio.analizar("tac_03").hayRegiones());
        var oseo = new ServicioDiagnostico(repo, new FabricaAnalizadorOseo(nucleo(), pipeline()));
        verificar("Analizador oseo encuentra el craneo (1 region grande)",
                oseo.analizar("tac_03").regionMayor().map(g -> g.area() > 3000).orElse(false));
    }

    // ---- DIP: el servicio funciona con falsos, sin C++ ni Python ----
    static void pruebasDIPconFalsos() throws Exception {
        NucleoConvolucion nucleoFalso = (ancho, alto, px) -> new int[px.length];
        PipelineFuncional pipelineFalso = new PipelineFuncional() {
            @Override
            public int[] normalizar(int ancho, int alto, int maxval, int[] px, int nivel, int anchoVentana) {
                return px;
            }

            @Override
            public ResultadoSegmentacion segmentar(int ancho, int alto, int[] n, int[] b,
                                                   ParametrosSegmentacion p) {
                return new ResultadoSegmentacion(List.of(new RegionTumoral(1, 4, 0, 0, 1, 1, 0.5, 0.5)), n);
            }
        };
        var repo = new RepositorioImagenEnMemoria();
        repo.guardar(new EstudioMedico("falso", "TAC", 16, 16, 255, new int[256]));
        var servicio = new ServicioDiagnostico(repo, new FabricaAnalizadorTumoral(nucleoFalso, pipelineFalso));
        verificar("DIP: el servicio funciona con dependencias falsas",
                servicio.analizar("falso").regiones().size() == 1);
    }

    // ---- Thread safety ----
    static void pruebasThreadSafety() throws Exception {
        var repo = new RepositorioImagenArchivo(Path.of("datos"));
        var servicio = new ServicioDiagnostico(repo, new FabricaAnalizadorTumoral(nucleo(), pipeline()));
        List<String> ids = repo.listarIds();

        Map<String, ResultadoAnalisis> secuencial = servicio.analizarLote(ids, 1);
        Map<String, ResultadoAnalisis> paralelo = servicio.analizarLote(ids, 4);
        boolean iguales = secuencial.keySet().equals(paralelo.keySet());
        for (String id : ids) {
            iguales &= secuencial.get(id).regiones().equals(paralelo.get(id).regiones())
                    && Arrays.equals(secuencial.get(id).mascara(), paralelo.get(id).mascara());
        }
        verificar("Lote con 4 hilos da el mismo resultado que con 1 hilo", iguales);

        // Estres: 8 hilos escribiendo y leyendo el repositorio concurrente.
        var memoria = new RepositorioImagenEnMemoria();
        int hilos = 8;
        int porHilo = 500;
        ExecutorService pool = Executors.newFixedThreadPool(hilos);
        CountDownLatch salida = new CountDownLatch(hilos);
        for (int h = 0; h < hilos; h++) {
            final int hh = h;
            pool.submit(() -> {
                for (int i = 0; i < porHilo; i++) {
                    memoria.guardar(new EstudioMedico("h" + hh + "_" + i, "TAC", 1, 1, 255, new int[] {i % 256}));
                }
                salida.countDown();
            });
        }
        salida.await(30, TimeUnit.SECONDS);
        pool.shutdown();
        verificar("Repositorio concurrente: no se pierde ninguna escritura",
                memoria.listarIds().size() == hilos * porHilo);

        boolean propaga = false;
        try {
            servicio.analizarLote(List.of("tac_01", "no_existe"), 2);
        } catch (Exception e) {
            propaga = e instanceof tac.dominio.TacException;
        }
        verificar("Un error en un hilo se propaga como TacException", propaga);
    }
}
