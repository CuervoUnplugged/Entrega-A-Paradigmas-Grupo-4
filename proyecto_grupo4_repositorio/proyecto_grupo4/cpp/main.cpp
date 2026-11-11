// Programa 'convolve': lee un PGM (P2) por stdin y escribe el resultado por stdout.
//   ./convolve --modo bordes|suavizar [--hilos N] [--secuencial]
#include <omp.h>

#include <algorithm>
#include <cmath>
#include <cstring>
#include <iostream>
#include <string>

#include "convolucion.hpp"
#include "pgm.hpp"

int main(int argc, char** argv) {
    std::string modo = "bordes";
    bool paralelo = true;
    int hilos = 0;
    for (int i = 1; i < argc; ++i) {
        if (!std::strcmp(argv[i], "--modo") && i + 1 < argc) modo = argv[++i];
        else if (!std::strcmp(argv[i], "--hilos") && i + 1 < argc) hilos = std::stoi(argv[++i]);
        else if (!std::strcmp(argv[i], "--secuencial")) paralelo = false;
        else {
            std::cerr << "Argumento desconocido: " << argv[i] << "\n";
            return 2;
        }
    }
    if (hilos > 0) omp_set_num_threads(hilos);

    try {
        ImagenPGM img = leerPGM(std::cin);
        std::vector<float> entrada(img.pixeles.begin(), img.pixeles.end());
        std::vector<float> salida;
        if (modo == "bordes") salida = conv::detectarBordes(entrada, img.ancho, img.alto, paralelo);
        else if (modo == "suavizar") salida = conv::suavizar(entrada, img.ancho, img.alto, paralelo);
        else {
            std::cerr << "Modo desconocido: " << modo << "\n";
            return 2;
        }
        std::vector<int> px(salida.size());
        for (size_t i = 0; i < salida.size(); ++i)
            px[i] = std::clamp(static_cast<int>(std::lround(salida[i])), 0, 255);
        escribirPGM(std::cout, img.ancho, img.alto, 255, px);
    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << "\n";
        return 1;
    }
    return 0;
}
