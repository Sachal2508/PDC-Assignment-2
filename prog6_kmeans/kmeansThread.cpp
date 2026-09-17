#include <algorithm>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <thread>

#include "CycleTimer.h"

using namespace std;

typedef struct {
  int start, end;
  double *data;
  double *clusterCentroids;
  int *clusterAssignments;
  double *currCost;
  int M, N, K;
} WorkerArgs;

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
    accum += pow((x[i] - y[i]), 2);
  }
  return sqrt(accum);
}

void computeAssignments(WorkerArgs *const args) {
  double *minDist = new double[args->M];
  for (int m = 0; m < args->M; m++) {
    minDist[m] = 1e30;
    args->clusterAssignments[m] = -1;
  }
  for (int k = args->start; k < args->end; k++) {
    for (int m = 0; m < args->M; m++) {
      double d = dist(&args->data[m * args->N],
                      &args->clusterCentroids[k * args->N], args->N);
      if (d < minDist[m]) {
        minDist[m] = d;
        args->clusterAssignments[m] = k;
      }
    }
  }
  delete[] minDist;
}

void computeCentroids(WorkerArgs *const args) {
  int *counts = new int[args->K];
  for (int k = 0; k < args->K; k++) {
    counts[k] = 0;
    for (int n = 0; n < args->N; n++) {
      args->clusterCentroids[k * args->N + n] = 0.0;
    }
  }
  for (int m = 0; m < args->M; m++) {
    int k = args->clusterAssignments[m];
    for (int n = 0; n < args->N; n++) {
      args->clusterCentroids[k * args->N + n] += args->data[m * args->N + n];
    }
    counts[k]++;
  }
  for (int k = 0; k < args->K; k++) {
    counts[k] = max(counts[k], 1);
    for (int n = 0; n < args->N; n++) {
      args->clusterCentroids[k * args->N + n] /= counts[k];
    }
  }
  delete[] counts;
}

void computeCost(WorkerArgs *const args) {
  double *accum = new double[args->K];
  for (int k = 0; k < args->K; k++) {
    accum[k] = 0.0;
  }
  for (int m = 0; m < args->M; m++) {
    int k = args->clusterAssignments[m];
    accum[k] += dist(&args->data[m * args->N],
                     &args->clusterCentroids[k * args->N], args->N);
  }
  for (int k = args->start; k < args->end; k++) {
    args->currCost[k] = accum[k];
  }
  delete[] accum;
}

void kMeansThread(double *data, double *clusterCentroids, int *clusterAssignments,
                  int M, int N, int K, double epsilon) {
  double *prevCost = new double[K];
  double *currCost = new double[K];

  WorkerArgs args;
  args.data = data;
  args.clusterCentroids = clusterCentroids;
  args.clusterAssignments = clusterAssignments;
  args.currCost = currCost;
  args.M = M;
  args.N = N;
  args.K = K;

  for (int k = 0; k < K; k++) {
    prevCost[k] = 1e30;
    currCost[k] = 0.0;
  }

  double totalAssignmentsTime = 0.0;
  double totalCentroidsTime = 0.0;
  double totalCostTime = 0.0;

  int iter = 0;
  while (!stoppingConditionMet(prevCost, currCost, epsilon, K)) {
    for (int k = 0; k < K; k++) {
      prevCost[k] = currCost[k];
    }
    args.start = 0;
    args.end = K;

    double t0 = CycleTimer::currentSeconds();
    computeAssignments(&args);
    double t1 = CycleTimer::currentSeconds();
    computeCentroids(&args);
    double t2 = CycleTimer::currentSeconds();
    computeCost(&args);
    double t3 = CycleTimer::currentSeconds();

    totalAssignmentsTime += (t1 - t0);
    totalCentroidsTime += (t2 - t1);
    totalCostTime += (t3 - t2);
    iter++;
  }

  double totalLoopTime = totalAssignmentsTime + totalCentroidsTime + totalCostTime;
  printf("\n=== Serial K-Means Profiling Breakdown (%d iterations) ===\n", iter);
  printf("  computeAssignments: %.3f s (%.1f%%)\n", totalAssignmentsTime, (totalAssignmentsTime / totalLoopTime) * 100.0);
  printf("  computeCentroids  : %.3f s (%.1f%%)\n", totalCentroidsTime, (totalCentroidsTime / totalLoopTime) * 100.0);
  printf("  computeCost       : %.3f s (%.1f%%)\n", totalCostTime, (totalCostTime / totalLoopTime) * 100.0);
  printf("  Hotspot fraction f (computeAssignments): %.4f\n", totalAssignmentsTime / totalLoopTime);
  printf("=========================================================\n\n");

  delete[] currCost;
  delete[] prevCost;
}
