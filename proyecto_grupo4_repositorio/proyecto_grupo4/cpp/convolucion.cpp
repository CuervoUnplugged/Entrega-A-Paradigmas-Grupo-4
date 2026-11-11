#include "convolucion.hpp"

#include <algorithm>
#include <cmath>
#include <cstddef>

namespace conv {

Kernel gaussiano5() {
    const float f[5] = {1, 4, 6, 4, 1};  // arreglo pequeno en el Stack
    Kernel ker{5, std::vector<float>(25)};
    for (int i = 0; i < 5; ++i)
        for (int j = 0; j < 5; ++j) ker.w[i * 5 + j] = f[i] * f[j] / 256.0f;
    return ker;
}

Kernel sobelX() { return Kernel{3, {-1, 0, 1, -2, 0, 2, -1, 0, 1}}; }
Kernel sobelY() { return Kernel{3, {-1, -2, -1, 0, 0, 0, 1, 2, 1}}; }

Kernel caja(int k) {
    return Kernel{k, std::vector<float>(static_cast<size_t>(k) * k, 1.0f / (k * k))};
}

void convolucionar(const float* in, float* out, int w, int h, const Kernel& ker, bool paralelo) {
    const int k = ker.k;
    const int r = k / 2;
    const int pw = w + 2 * r;  // ancho de la imagen con borde (padding)
    const int ph = h + 2 * r;

    // Copia con bordes replicados en un bloque contiguo del Heap.
    // Asi el bucle interno no necesita ifs para los bordes y recorre filas contiguas.
    std::vector<float> pad(static_cast<size_t>(pw) * ph);
    for (int y = 0; y < ph; ++y) {
        const int sy = std::clamp(y - r, 0, h - 1);
        for (int x = 0; x < pw; ++x) {
            const int sx = std::clamp(x - r, 0, w - 1);
            pad[static_cast<size_t>(y) * pw + x] = in[static_cast<size_t>(sy) * w + sx];
        }
    }

    const float* p = pad.data();
    const float* kw = ker.w.data();

    // Cada iteracion de 'y' es independiente: escribe solo la fila y de 'out'
    // y solo lee 'pad' y 'kw'. No hay condiciones de carrera.
#pragma omp parallel for schedule(static) if (paralelo)
    for (int y = 0; y < h; ++y) {
        float* fila = out + static_cast<size_t>(y) * w;
        for (int x = 0; x < w; ++x) {
            float acc = 0.0f;
            for (int ky = 0; ky < k; ++ky) {
                const float* fp = p + static_cast<size_t>(y + ky) * pw + x;  // fila contigua
                const float* fk = kw + ky * k;
                for (int kx = 0; kx < k; ++kx) acc += fp[kx] * fk[kx];
            }
            fila[x] = acc;
        }
    }
}

void magnitudGradiente(const float* gx, const float* gy, float* out, long n, float escala, bool paralelo) {
#pragma omp parallel for schedule(static) if (paralelo)
    for (long i = 0; i < n; ++i) {
        const float m = escala * std::sqrt(gx[i] * gx[i] + gy[i] * gy[i]);
        out[i] = std::min(255.0f, m);
    }
}

std::vector<float> suavizar(const std::vector<float>& in, int w, int h, bool paralelo) {
    std::vector<float> out(in.size());
    convolucionar(in.data(), out.data(), w, h, gaussiano5(), paralelo);
    return out;
}

std::vector<float> detectarBordes(const std::vector<float>& in, int w, int h, bool paralelo) {
    const long n = static_cast<long>(w) * h;
    std::vector<float> liso = suavizar(in, w, h, paralelo);
    std::vector<float> gx(n), gy(n), mag(n);
    convolucionar(liso.data(), gx.data(), w, h, sobelX(), paralelo);
    convolucionar(liso.data(), gy.data(), w, h, sobelY(), paralelo);
    // Un escalon de 255 da gradiente 4*255 en Sobel; con escala 0.25 queda en 255.
    magnitudGradiente(gx.data(), gy.data(), mag.data(), n, 0.25f, paralelo);
    return mag;
}

}  // namespace conv
