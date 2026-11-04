/* QCIP forward-star client, plus scan alternative. See ../PROVENANCE.md.
 * Styles: 0 sorted queue, 1 scan, 2 heap queue, 3 freeze-first-distance mutant. */
#include "../common/io.h"
#define INF 1000000000
static int head[10]; static int to[64]; static int weight[64]; static int next[64];
static int dist[10];
#if EB_STYLE != 1
#include "queue.h"
static void solve(int n, int source) {
    int i; int u; int d; int e; int v; int candidate;
    for (i = 0; i < 10; i = i + 1) dist[i] = INF;
    dist[source] = 0; queue_clear(); queue_push(source, 0);
    while (!queue_empty()) {
        queue_pop(&u, &d);
        if (d == dist[u]) {
            for (e = head[u]; e != -1; e = next[e]) {
                v = to[e];
                if (weight[e] >= 0 && d <= INF - weight[e]) {
                    candidate = d + weight[e];
                    if (candidate < dist[v]
#if EB_STYLE == 3
                        && dist[v] == INF
#endif
                    ) { dist[v] = candidate; queue_push(v, candidate); }
                }
            }
        }
    }
}
#else
static void solve(int n, int source) {
    int settled[10]; int i; int j; int u; int e; int v; int candidate;
    for (i = 0; i < 10; i = i + 1) { dist[i] = INF; settled[i] = 0; }
    dist[source] = 0;
    for (j = 0; j < n; j = j + 1) {
        u = -1;
        for (i = 0; i < n; i = i + 1) {
            if (!settled[i] && dist[i] < INF) {
                if (u == -1 || dist[i] < dist[u]) u = i;
            }
        }
        if (u == -1) break;
        settled[u] = 1;
        for (e = head[u]; e != -1; e = next[e]) {
            v = to[e]; candidate = dist[u] + weight[e];
            if (candidate < dist[v]) dist[v] = candidate;
        }
    }
}
#endif
static void build_graph(int n, int m) {
    int i; int pos = 3; int u;
    for (i = 0; i < 10; i = i + 1) head[i] = -1;
    for (i = 0; i < m; i = i + 1) {
        u = eb_input[pos]; to[i] = eb_input[pos + 1]; weight[i] = eb_input[pos + 2]; pos = pos + 3;
        next[i] = head[u]; head[u] = i;
    }
}
int main(void) {
    int n = eb_input[0]; int m = eb_input[1]; int source = eb_input[2]; int i;
    begin_output(); build_graph(n, m); solve(n, source);
    for (i = 0; i < n; i = i + 1) emit(dist[i]);
    return end_output();
}
