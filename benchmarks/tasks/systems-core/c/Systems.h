#include "../../qcip-core/common/io.h"

#if EB_FAMILY == 0

static int edges[8][8], dirty[8], reached[8];

static int eligible_edge(int from, int to) {
    if (!edges[from][to] || reached[to]) return 0;
#if EB_STYLE == 2
    if (dirty[to]) return 0;
#endif
    return 1;
}

#if EB_STYLE == 0
static void scan_neighbors(int from) {
    int to;
    for (to = 0; to < 8; ++to)
        if (eligible_edge(from, to)) reached[to] = 1;
}
static void propagate(int root) {
    int pass, from;
    reached[root] = 1;
    for (pass = 0; pass < 8; ++pass)
        for (from = 0; from < 8; ++from)
            if (reached[from]) scan_neighbors(from);
}
#else
static int enqueue_neighbors(int from, int *queue, int end) {
    int to;
    for (to = 0; to < 8; ++to) {
        if (eligible_edge(from, to)) {
            reached[to] = 1;
            queue[end++] = to;
        }
    }
    return end;
}
static void propagate(int root) {
    int queue[8], head = 0, end = 1;
    reached[root] = 1;
    queue[0] = root;
    while (head < end) {
        end = enqueue_neighbors(queue[head], queue, end);
        ++head;
    }
}
#endif

static void invalidate(int root) {
    int node;
    for (node = 0; node < 8; ++node) reached[node] = 0;
    propagate(root);
    for (node = 0; node < 8; ++node)
        if (reached[node]) dirty[node] = 1;
}

static int dirty_mask(void) {
    int node, mask = 0;
    for (node = 0; node < 8; ++node) mask += dirty[node] << node;
    return mask;
}

static void graph_command(int op, int a, int b) {
    int result = 0;
    if (op <= 1) edges[a][b] = op == 0;
    else if (op == 2) invalidate(a);
    else if (op == 3) dirty[a] = 0;
    else result = dirty[a];
    emit(op);
    emit(result);
    emit(dirty_mask());
}

int main(void) {
    int i, j, p;
    begin_output();
    for (i = 0; i < 8; ++i) {
        dirty[i] = 0;
        for (j = 0; j < 8; ++j) edges[i][j] = 0;
    }
    for (i = 0; i < eb_input[0]; ++i) {
        p = 1 + 4 * i;
        graph_command(eb_input[p], eb_input[p+1], eb_input[p+2]);
    }
    return end_output();
}

#elif EB_FAMILY == 1

struct Binding { int tag, value; };
static struct Binding layers[5][8];
static int depth;

static void write_binding(int level, int key, int tag, int value) {
    layers[level][key].tag = tag;
    layers[level][key].value = value;
}

static void init_layer(int level) {
    int key;
    for (key = 0; key < 8; ++key) {
#if EB_STYLE == 0
        write_binding(level, key, layers[level-1][key].tag,
                      layers[level-1][key].value);
#else
        write_binding(level, key, -1, 0);
#endif
    }
}

static int push_scope(void) {
    if (depth == 4) return 2;
    ++depth;
    init_layer(depth);
    return 0;
}

static int pop_scope(void) {
    if (depth == 0) return 1;
    --depth;
    return 0;
}

static int resolve_binding(int key, int *value) {
    int level = depth;
#if EB_STYLE != 0
    while (layers[level][key].tag < 0 && level > 0) --level;
#endif
    *value = layers[level][key].value;
    return layers[level][key].tag == 1;
}

static void hide_binding(int key) {
#if EB_STYLE == 2
    write_binding(depth, key, depth == 0 ? 0 : -1, 0);
#else
    write_binding(depth, key, 0, 0);
#endif
}

static void scope_command(int op, int key, int value) {
    int status = 0, found = 0, result = 0;
    if (op == 0) write_binding(depth, key, 1, value);
    else if (op == 1) hide_binding(key);
    else if (op == 2) found = resolve_binding(key, &result);
    else if (op == 3) status = push_scope();
    else status = pop_scope();
    emit(op); emit(status); emit(found); emit(result); emit(depth);
}

static void observe_bindings(void) {
    int key, value, found;
    for (key = 0; key < 8; ++key) {
        found = resolve_binding(key, &value);
        emit(found); emit(value);
    }
}

int main(void) {
    int i, p;
    begin_output();
    depth = 0;
    for (i = 0; i < 8; ++i) write_binding(0, i, 0, 0);
    for (i = 0; i < eb_input[0]; ++i) {
        p = 1 + 4 * i;
        scope_command(eb_input[p], eb_input[p+1], eb_input[p+2]);
    }
    observe_bindings();
    return end_output();
}

#elif EB_FAMILY == 2

struct Lease { int live, value, deadline; };
static struct Lease leases[8];
static int clock_now;
#if EB_STYLE != 0
static int wheel[9][8];
#endif

static void clear_lease(int key) {
#if EB_STYLE != 0
    if (leases[key].live) wheel[leases[key].deadline % 9][key] = 0;
#endif
    leases[key].live = 0;
    leases[key].value = 0;
    leases[key].deadline = 0;
}

static void set_lease(int key, int value, int ttl) {
#if EB_STYLE == 1
    clear_lease(key);
#endif
    leases[key].live = 1;
    leases[key].value = value;
    leases[key].deadline = clock_now + ttl;
#if EB_STYLE != 0
    wheel[leases[key].deadline % 9][key] = 1;
#endif
}

static int is_due(int key) {
#if EB_STYLE == 0
    return leases[key].deadline == clock_now;
#else
    int due = wheel[clock_now % 9][key];
    wheel[clock_now % 9][key] = 0;
    return due;
#endif
}

static int expire_at_tick(int *keys, int count) {
    int key;
    ++clock_now;
    for (key = 0; key < 8; ++key) {
        if (is_due(key) && leases[key].live) {
            keys[count++] = key;
            clear_lease(key);
        }
    }
    return count;
}

static int advance_clock(int ticks, int *keys) {
    int i, count = 0;
    for (i = 0; i < ticks; ++i) count = expire_at_tick(keys, count);
    return count;
}

static void lease_command(int op, int a, int b, int c) {
    int keys[8], count = 0, found = 0, value = 0, i;
    if (op == 0) set_lease(a, b, c);
    else if (op == 3) count = advance_clock(a, keys);
    else {
        found = leases[a].live;
        value = leases[a].value;
        if (op == 2) clear_lease(a);
    }
    emit(op); emit(found); emit(value); emit(count);
    for (i = 0; i < count; ++i) emit(keys[i]);
}

int main(void) {
    int i, j, p;
    begin_output();
    clock_now = 0;
#if EB_STYLE != 0
    for (i = 0; i < 9; ++i)
        for (j = 0; j < 8; ++j) wheel[i][j] = 0;
#endif
    for (i = 0; i < 8; ++i) {
        leases[i].live = 0;
        clear_lease(i);
    }
    for (i = 0; i < eb_input[0]; ++i) {
        p = 1 + 4 * i;
        lease_command(eb_input[p], eb_input[p+1], eb_input[p+2], eb_input[p+3]);
    }
    emit(clock_now);
    for (i = 0; i < 8; ++i) {
        emit(leases[i].live); emit(leases[i].value);
    }
    return end_output();
}
#else
#include "Numerical.h"
#endif
