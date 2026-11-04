#include "../../qcip-core/common/io.h"

#if EB_FAMILY == 0
struct Edge { int u, v, weight, id; };
static struct Edge edges[28];
static int parent[8], visited[8], selected[28];
static int vertices, edge_count;

static int root(int x) {
    while (parent[x] != x) x = parent[x];
    return x;
}
static void choose_edge(int id, int *total) {
    selected[id] = 1;
    *total += edges[id].weight;
}
static int better(int a, int b) {
    if (b < 0) return 1;
#if EB_STYLE == 2
    return edges[a].weight > edges[b].weight;
#else
    return edges[a].weight < edges[b].weight;
#endif
}
#if EB_STYLE == 1
static int crossing_edge(void) {
    int e, best = -1;
    for (e = 0; e < edge_count; ++e)
        if (visited[edges[e].u] != visited[edges[e].v] && better(e,best)) best = e;
    return best;
}
static int spanning_forest(int *total) {
    int start, best, components = 0;
    for (start = 0; start < vertices; ++start) {
        if (visited[start]) continue;
        ++components;
        visited[start] = 1;
        while ((best = crossing_edge()) >= 0) {
            choose_edge(best,total);
            visited[edges[best].u] = 1;
            visited[edges[best].v] = 1;
        }
    }
    return components;
}
#else
static int spanning_forest(int *total) {
    int order[28], i, j, x, a, b, components = vertices;
    for (i=0; i<edge_count; ++i) order[i]=i;
    for (i=1; i<edge_count; ++i) {
        x=order[i]; j=i;
        while (j>0 && better(x,order[j-1])) {
            order[j]=order[j-1]; --j;
        }
        order[j]=x;
    }
    for (i=0; i<edge_count; ++i) {
        x=order[i]; a=root(edges[x].u); b=root(edges[x].v);
        if (a != b) {
            parent[a]=b; --components;
            choose_edge(x,total);
        }
    }
    return components;
}
#endif
int main(void) {
    int i, p, total=0, components, mask=0, mode=eb_input[0];
    begin_output();
    vertices=eb_input[1]; edge_count=eb_input[2];
    for (i=0; i<8; ++i) { parent[i]=i; visited[i]=0; }
    for (i=0; i<28; ++i) selected[i]=0;
    for (i=0; i<edge_count; ++i) {
        p=3+3*i; edges[i].u=eb_input[p]; edges[i].v=eb_input[p+1];
        edges[i].weight=eb_input[p+2]; edges[i].id=i;
    }
    components=spanning_forest(&total);
    emit(total); emit(components);
    if (mode==1) {
        for (i=0; i<edge_count; ++i) if (selected[i]) mask += 1<<i;
        emit(mask);
    }
    return end_output();
}
#else
struct Record { int key, payload; };
static struct Record data[64], temp[64];

#if EB_STYLE == 0
static void sort_records(int n) {
    int i, j;
    struct Record item;
    for (i=1; i<n; ++i) {
        item=data[i]; j=i;
        while (j>0 && item.key<data[j-1].key) { data[j]=data[j-1]; --j; }
        data[j]=item;
    }
}
#elif EB_STYLE == 1
static void merge_range(int left, int middle, int right) {
    int i=left, j=middle, k=left;
    while (i<middle && j<right) {
        if (data[i].key<=data[j].key) temp[k++]=data[i++];
        else temp[k++]=data[j++];
    }
    while (i<middle) temp[k++]=data[i++];
    while (j<right) temp[k++]=data[j++];
    for (k=left; k<right; ++k) data[k]=temp[k];
}
static void sort_range(int left, int right) {
    int middle;
    if (right-left<=1) return;
    middle=left+(right-left)/2;
    sort_range(left,middle); sort_range(middle,right);
    merge_range(left,middle,right);
}
static void sort_records(int n) { sort_range(0,n); }
#else
static void sort_records(int n) {
    int i, j, best;
    struct Record item;
    for (i=0; i<n; ++i) {
        best=i;
        for (j=i+1; j<n; ++j) if (data[j].key<data[best].key) best=j;
        item=data[i]; data[i]=data[best]; data[best]=item;
    }
}
#endif
int main(void) {
    int i, n=eb_input[0];
    begin_output();
    for (i=0; i<n; ++i) { data[i].key=eb_input[1+2*i]; data[i].payload=eb_input[2+2*i]; }
    sort_records(n);
    for (i=0; i<n; ++i) { emit(data[i].key); emit(data[i].payload); }
    return end_output();
}
#endif
