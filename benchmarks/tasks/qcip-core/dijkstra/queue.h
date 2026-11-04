/* Frozen queue providers: QCIP-style sorted min queue or authored min heap. */
#define QUEUE_CAPACITY 641
static int queue_vertex[QUEUE_CAPACITY];
static int queue_distance[QUEUE_CAPACITY];
static int queue_size;
static void queue_clear(void) { queue_size = 0; }
static int queue_empty(void) { return queue_size == 0; }
static void queue_push(int v, int d) {
    int i = queue_size; int parent;
#if EB_STYLE == 2
    while (i > 0) {
        parent = (i - 1) / 2;
        if (queue_distance[parent] <= d) break;
        queue_vertex[i] = queue_vertex[parent]; queue_distance[i] = queue_distance[parent]; i = parent;
    }
#else
    while (i > 0 && queue_distance[i - 1] > d) {
        queue_vertex[i] = queue_vertex[i - 1]; queue_distance[i] = queue_distance[i - 1]; i = i - 1;
    }
#endif
    queue_vertex[i] = v; queue_distance[i] = d; queue_size = queue_size + 1;
}
static void queue_pop(int *v, int *d) {
    int i; int child; int last_v; int last_d;
    *v = queue_vertex[0]; *d = queue_distance[0];
#if EB_STYLE == 2
    queue_size = queue_size - 1;
    if (queue_size == 0) return;
    last_v = queue_vertex[queue_size]; last_d = queue_distance[queue_size]; i = 0;
    while (2 * i + 1 < queue_size) {
        child = 2 * i + 1;
        if (child + 1 < queue_size && queue_distance[child + 1] < queue_distance[child]) child = child + 1;
        if (last_d <= queue_distance[child]) break;
        queue_vertex[i] = queue_vertex[child]; queue_distance[i] = queue_distance[child]; i = child;
    }
    queue_vertex[i] = last_v; queue_distance[i] = last_d;
#else
    for (i = 1; i < queue_size; i = i + 1) {
        queue_vertex[i - 1] = queue_vertex[i]; queue_distance[i - 1] = queue_distance[i];
    }
    queue_size = queue_size - 1;
#endif
}
