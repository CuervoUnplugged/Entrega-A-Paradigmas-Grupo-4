// Lectura y escritura de imagenes PGM en formato de texto (P2).
#pragma once
#include <istream>
#include <ostream>
#include <stdexcept>
#include <string>
#include <vector>

struct ImagenPGM {
    int ancho = 0;
    int alto = 0;
    int maxval = 255;
    std::vector<int> pixeles;  // fila por fila (row-major), memoria contigua
};

// Devuelve el siguiente token ignorando comentarios que empiezan con '#'.
inline std::string siguienteToken(std::istream& in) {
    std::string tok;
    while (in >> tok) {
        if (tok[0] == '#') {
            std::string resto;
            std::getline(in, resto);
            continue;
        }
        return tok;
    }
    throw std::runtime_error("PGM incompleto");
}

inline ImagenPGM leerPGM(std::istream& in) {
    if (siguienteToken(in) != "P2") throw std::runtime_error("Se espera PGM en formato P2");
    ImagenPGM img;
    img.ancho = std::stoi(siguienteToken(in));
    img.alto = std::stoi(siguienteToken(in));
    img.maxval = std::stoi(siguienteToken(in));
    if (img.ancho <= 0 || img.alto <= 0) throw std::runtime_error("Dimensiones invalidas");
    const size_t n = static_cast<size_t>(img.ancho) * img.alto;
    img.pixeles.reserve(n);
    for (size_t i = 0; i < n; ++i) img.pixeles.push_back(std::stoi(siguienteToken(in)));
    return img;
}

inline void escribirPGM(std::ostream& out, int ancho, int alto, int maxval, const std::vector<int>& px) {
    out << "P2\n" << ancho << " " << alto << "\n" << maxval << "\n";
    for (int y = 0; y < alto; ++y) {
        for (int x = 0; x < ancho; ++x) {
            out << px[static_cast<size_t>(y) * ancho + x] << (x + 1 < ancho ? ' ' : '\n');
        }
    }
}
