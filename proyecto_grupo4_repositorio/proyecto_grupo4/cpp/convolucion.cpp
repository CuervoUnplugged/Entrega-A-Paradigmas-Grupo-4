#include <algorithm>
#include <cstddef>
#ifdef _OPENMP
#include <omp.h>
#endif

// Tamaño de bloque para caché de 32KB
constexpr int TILE_SIZE = 32;

void convolve_tiled(const float* p, float* out, int w, int h, int pw, 
                    const float* kw, int k, bool paralelo) {
    
    // collapse reparte los bloques equitativamente por los hilos OpenMP
    #pragma omp parallel for collapse(2) schedule(static) if (paralelo)
    for (int ty = 0; ty < h; ty += TILE_SIZE) {
        for (int tx = 0; tx < w; tx += TILE_SIZE) {
            
            const int y_max = std::min(ty + TILE_SIZE, h);
            const int x_max = std::min(tx + TILE_SIZE, w);

            // Iteración dentro del bloque para localidad espacial y temporal
            for (int y = ty; y < y_max; ++y) {
                float* fila = out + static_cast<size_t>(y) * w;
                
                for (int x = tx; x < x_max; ++x) {
                    float acc = 0.0f;
                    
                    for (int ky = 0; ky < k; ++ky) {
                        const float* fp = p + static_cast<size_t>(y + ky) * pw + x;
                        const float* fk = kw + static_cast<size_t>(ky) * k;
                        
                        //vectorización
                        #pragma omp simd reduction(+:acc)
                        for (int kx = 0; kx < k; ++kx) {
                            acc += fp[kx] * fk[kx];
                        }
                    }
                    fila[x] = acc;
                }
            }
        }
    }
}
