#include <stdio.h>
#include <string.h>
#include <algorithm>
#include <pthread.h>
#include <math.h>

#include "CycleTimer.h"
#include "sqrt_ispc.h"

using namespace ispc;

extern void sqrtSerial(int N, float startGuess, float* values, float* output);

static void verifyResult(int N, float* result, float* gold) {
    for (int i=0; i<N; i++) {
        if (fabs(result[i] - gold[i]) > 1e-4) {
            printf("Error: [%d] Got %f expected %f\n", i, result[i], gold[i]);
            return;
        }
    }
}

void runBenchmark(const char* title, float* values, float* output, float* gold, unsigned int N, float initialGuess) {
    printf("\n=======================================================\n");
    printf("%s\n", title);
    printf("=======================================================\n");

    // Generate gold version
    for (unsigned int i = 0; i < N; i++)
        gold[i] = sqrt(values[i]);

    // Serial implementation (minimum of 3 runs)
    double minSerial = 1e30;
    for (int i = 0; i < 3; ++i) {
        double startTime = CycleTimer::currentSeconds();
        sqrtSerial(N, initialGuess, values, output);
        double endTime = CycleTimer::currentSeconds();
        minSerial = std::min(minSerial, endTime - startTime);
    }
    printf("[sqrt serial]:\t\t[%.3f] ms\n", minSerial * 1000);
    verifyResult(N, output, gold);

    // Single-core ISPC implementation (minimum of 3 runs)
    double minISPC = 1e30;
    for (int i = 0; i < 3; ++i) {
        double startTime = CycleTimer::currentSeconds();
        sqrt_ispc(N, initialGuess, values, output);
        double endTime = CycleTimer::currentSeconds();
        minISPC = std::min(minISPC, endTime - startTime);
    }
    printf("[sqrt ispc]:\t\t[%.3f] ms\n", minISPC * 1000);
    verifyResult(N, output, gold);

    // Clear output buffer
    for (unsigned int i = 0; i < N; ++i)
        output[i] = 0;

    // Multi-task ISPC implementation (minimum of 3 runs)
    double minTaskISPC = 1e30;
    for (int i = 0; i < 3; ++i) {
        double startTime = CycleTimer::currentSeconds();
        sqrt_ispc_withtasks(N, initialGuess, values, output);
        double endTime = CycleTimer::currentSeconds();
        minTaskISPC = std::min(minTaskISPC, endTime - startTime);
    }
    printf("[sqrt task ispc]:\t[%.3f] ms\n", minTaskISPC * 1000);
    verifyResult(N, output, gold);

    printf("\t\t\t\t(%.2fx speedup from ISPC)\n", minSerial / minISPC);
    printf("\t\t\t\t(%.2fx speedup from task ISPC)\n", minSerial / minTaskISPC);
}

int main(int argc, char** argv) {
    const unsigned int N = 20 * 1000 * 1000;
    const float initialGuess = 1.0f;

    float* values = new float[N];
    float* output = new float[N];
    float* gold = new float[N];

    bool runRandom = true;
    bool runBest = true;
    bool runWorst = true;

    if (argc > 1) {
        if (strcmp(argv[1], "best") == 0) {
            runRandom = false;
            runWorst = false;
        } else if (strcmp(argv[1], "worst") == 0) {
            runRandom = false;
            runBest = false;
        } else if (strcmp(argv[1], "random") == 0) {
            runBest = false;
            runWorst = false;
        }
    }

    if (runRandom) {
        for (unsigned int i = 0; i < N; i++) {
            values[i] = .001f + 2.998f * static_cast<float>(rand()) / RAND_MAX;
        }
        runBenchmark("Baseline Random Input (Uncorrelated iterations across lanes)",
                     values, output, gold, N, initialGuess);
    }

    if (runBest) {
        for (unsigned int i = 0; i < N; i++) {
            values[i] = 2.999f;
        }
        runBenchmark("Best-Case Input (Uniform 2.999f - Zero SIMD lane divergence)",
                     values, output, gold, N, initialGuess);
    }

    if (runWorst) {
        for (unsigned int i = 0; i < N; i++) {
            // In each AVX2 8-lane vector, 1 lane does full work (2.999f), 7 lanes finish immediately (1.0f)
            if (i % 8 == 0) {
                values[i] = 2.999f;
            } else {
                values[i] = 1.0f;
            }
        }
        runBenchmark("Worst-Case Input (1 active lane, 7 idle lanes - Extreme SIMD divergence)",
                     values, output, gold, N, initialGuess);
    }

    delete [] values;
    delete [] output;
    delete [] gold;

    return 0;
}
