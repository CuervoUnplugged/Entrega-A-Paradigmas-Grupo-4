// Benchmark Secuencial vs Paralelo (OpenMP). Imprime tablas en Markdown.
//   ./bench [--rapido]
#include <omp.h>

#include <algorithm>
#include <cmath>
#include <cstdio>
#include <cstring>
#include <random>
#include <vector>

#include "convolucion.hpp"

static double mejorTiempo(int reps, bool paralelo, const std::vector<float>& in, std::vector<float>& out,
                          int w, int h, const conv::Kernel& ker) {
    double mejor = 1e30;
    for (int r = 0; r < reps; ++r) {
        const double t0 = omp_get_wtime();
        conv::convolucionar(in.data(), out.data(), w, h, ker, paralelo);
        mejor = std::min(mejor, omp_get_wtime() - t0);
    }
    return mejor * 1000.0;  // ms
}

int main(int argc, char** argv) {
    const bool rapido = argc > 1 && !std::strcmp(argv[1], "--rapido");
    const int maxHilos = omp_get_max_threads();
    std::printf("Hilos maximos de OpenMP en esta maquina: %d\n\n", maxHilos);
    std::printf("| Tamano | K | Hilos | T secuencial (ms) | T paralelo (ms) | Speedup | Eficiencia | Resultado igual |\n");
    std::printf("|---|---|---|---|---|---|---|---|\n");

    std::vector<int> tamanos = rapido ? std::vector<int>{512, 1024} : std::vector<int>{512, 1024, 2048};
    std::vector<int> ks = {3, 5, 9};
    std::vector<int> hilosLista = {2, 4};
    if (maxHilos > 4) hilosLista.push_back(maxHilos);

    std::mt19937 gen(42);
    std::uniform_real_distribution<float> dist(0.0f, 255.0f);

    for (int n : tamanos) {
        std::vector<float> in(static_cast<size_t>(n) * n);
        for (auto& v : in) v = dist(gen);
        std::vector<float> outSeq(in.size()), outPar(in.size());
        for (int k : ks) {
            conv::Kernel ker = conv::caja(k);
            const double tSeq = mejorTiempo(3, false, in, outSeq, n, n, ker);
            for (int t : hilosLista) {
                omp_set_num_threads(t);
                const double tPar = mejorTiempo(3, true, in, outPar, n, n, ker);
                const bool igual = (outSeq == outPar);  // cada pixel se calcula en el mismo orden
                const double speedup = tSeq / tPar;
                std::printf("| %dx%d | %d | %d | %.1f | %.1f | %.2fx | %.0f%% | %s |\n", n, n, k, t, tSeq, tPar,
                            speedup, 100.0 * speedup / t, igual ? "si" : "NO");
            }
        }
    }
    return 0;
}
