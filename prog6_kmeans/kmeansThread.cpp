#include <algorithm>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <thread>
#include <vector>

#include "CycleTimer.h"

using namespace std;

// Number of worker threads matching hardware thread count T = 8
static const int NUM_THREADS = 8;

static bool stoppingConditionMet(double *prevCost, double *currCost,
                                 double epsilon, int K) {
  for (int k = 0; k < K; k++) {
    if (abs(prevCost[k] - currCost[k]) > epsilon)
      return false;
  }
  return true;
}

double dist(double *x, double *y, int nDim) {
  double accum = 0.0;
  for (int i = 0; i < nDim; i++) {
    double diff = x[i] - y[i];
    accum += diff * diff;
  }
  return sqrt(accum);
}

void computeAssignmentsParallel(double *data, double *clusterCentroids,
                                int *clusterAssignments, int M, int N, int K,
                                int numThreads) {
  std::vector<std::thread> workers;
  int chunkSize = (M + numThreads - 1) / numThreads;

  for (int t = 0; t < numThreads; t++) {
    int start = t * chunkSize;
    int end = std::min(start + chunkSize, M);
    if (start >= end) break;

    workers.emplace_back([=]() {
      for (int m = start; m < end; m++) {
        double minDist = 1e30;
        int bestAssignment = -1;
        const double *point = &data[m * N];

        for (int k = 0; k < K; k++) {
          const double *centroid = &clusterCentroids[k * N];
          double accum = 0.0;
          for (int i = 0; i < N; i++) {
            double diff = point[i] - centroid[i];
            accum += diff * diff;
          }
          if (accum < minDist) {
            minDist = accum;
            bestAssignment = k;
          }
        }
        clusterAssignments[m] = bestAssignment;
      }
    });
  }

  for (auto &w : workers) {
    w.join();
  }
}

void computeCentroidsParallel(double *data, double *clusterCentroids,
                              int *clusterAssignments, int M, int N, int K,
                              int numThreads) {
  std::vector<std::thread> workers;
  std::vector<std::vector<double>> localCentroids(numThreads, std::vector<double>(K * N, 0.0));
  std::vector<std::vector<int>> localCounts(numThreads, std::vector<int>(K, 0));
  int chunkSize = (M + numThreads - 1) / numThreads;

  for (int t = 0; t < numThreads; t++) {
    int start = t * chunkSize;
    int end = std::min(start + chunkSize, M);
    if (start >= end) break;

    workers.emplace_back([=, &localCentroids, &localCounts]() {
      for (int m = start; m < end; m++) {
        int k = clusterAssignments[m];
        const double *point = &data[m * N];
        double *myCentroid = &localCentroids[t][k * N];
        for (int n = 0; n < N; n++) {
          myCentroid[n] += point[n];
        }
        localCounts[t][k]++;
      }
    });
  }

  for (auto &w : workers) {
    w.join();
  }

  std::vector<int> totalCounts(K, 0);
  for (int k = 0; k < K; k++) {
    for (int n = 0; n < N; n++) {
      clusterCentroids[k * N + n] = 0.0;
    }
  }

  for (int t = 0; t < numThreads; t++) {
    for (int k = 0; k < K; k++) {
      totalCounts[k] += localCounts[t][k];
      for (int n = 0; n < N; n++) {
        clusterCentroids[k * N + n] += localCentroids[t][k * N + n];
      }
    }
  }

  for (int k = 0; k < K; k++) {
    int count = std::max(totalCounts[k], 1);
    for (int n = 0; n < N; n++) {
      clusterCentroids[k * N + n] /= count;
    }
  }
}

void computeCostParallel(double *data, double *clusterCentroids,
                         int *clusterAssignments, double *currCost,
                         int M, int N, int K, int numThreads) {
  std::vector<std::thread> workers;
  std::vector<std::vector<double>> localCosts(numThreads, std::vector<double>(K, 0.0));
  int chunkSize = (M + numThreads - 1) / numThreads;

  for (int t = 0; t < numThreads; t++) {
    int start = t * chunkSize;
    int end = std::min(start + chunkSize, M);
    if (start >= end) break;

    workers.emplace_back([=, &localCosts]() {
      for (int m = start; m < end; m++) {
        int k = clusterAssignments[m];
        const double *point = &data[m * N];
        const double *centroid = &clusterCentroids[k * N];
        double accum = 0.0;
        for (int i = 0; i < N; i++) {
          double diff = point[i] - centroid[i];
          accum += diff * diff;
        }
        localCosts[t][k] += sqrt(accum);
      }
    });
  }

  for (auto &w : workers) {
    w.join();
  }

  for (int k = 0; k < K; k++) {
    currCost[k] = 0.0;
    for (int t = 0; t < numThreads; t++) {
      currCost[k] += localCosts[t][k];
    }
  }
}

void kMeansThread(double *data, double *clusterCentroids, int *clusterAssignments,
                  int M, int N, int K, double epsilon) {

  double *prevCost = new double[K];
  double *currCost = new double[K];

  for (int k = 0; k < K; k++) {
    prevCost[k] = 1e30;
    currCost[k] = 0.0;
  }

  int iter = 0;
  while (!stoppingConditionMet(prevCost, currCost, epsilon, K)) {
    for (int k = 0; k < K; k++) {
      prevCost[k] = currCost[k];
    }

    computeAssignmentsParallel(data, clusterCentroids, clusterAssignments, M, N, K, NUM_THREADS);
    computeCentroidsParallel(data, clusterCentroids, clusterAssignments, M, N, K, NUM_THREADS);
    computeCostParallel(data, clusterCentroids, clusterAssignments, currCost, M, N, K, NUM_THREADS);

    iter++;
  }

  printf("K-Means converged in %d iterations using %d threads.\n", iter, NUM_THREADS);

  delete[] currCost;
  delete[] prevCost;
}
