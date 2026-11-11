// Modulo 1 (Paradigma Imperativo): kernels de convolucion 2D sobre memoria contigua.
#pragma once
#include <vector>

namespace conv {

// Kernel cuadrado k x k (k impar), pesos guardados fila por fila.
struct Kernel {
    int k;
    std::vector<float> w;
};

Kernel gaussiano5();      // suavizado 5x5 (binomial / 256)
Kernel sobelX();          // 3x3, bordes verticales
Kernel sobelY();          // 3x3, bordes horizontales
Kernel caja(int k);       // promedio k x k (para benchmarks con K variable)

// out = in (*) kernel.  Complejidad: Theta(W*H*K^2).
// 'paralelo' activa OpenMP sobre las filas; cada hilo escribe filas distintas.
void convolucionar(const float* in, float* out, int w, int h, const Kernel& ker, bool paralelo);

// out[i] = min(255, escala * sqrt(gx[i]^2 + gy[i]^2))
void magnitudGradiente(const float* gx, const float* gy, float* out, long n, float escala, bool paralelo);

// Suavizado gaussiano 5x5 -> Sobel 3x3 -> magnitud del gradiente.
std::vector<float> detectarBordes(const std::vector<float>& in, int w, int h, bool paralelo);

std::vector<float> suavizar(const std::vector<float>& in, int w, int h, bool paralelo);

}  // namespace conv
