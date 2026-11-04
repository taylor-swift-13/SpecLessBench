/* Derived XiZi/QCIP ring task, normalized API; see ../PROVENANCE.md.
 * Styles: 0 span+flag, 1 byte+flag, 2 byte+count, 3 flag/full-as-empty mutant. */
#include "../common/io.h"
struct ring {
    unsigned char data[64]; int capacity; int read; int write; int full; int count;
};
static struct ring area;
static void copy_bytes(unsigned char *dst, unsigned char *src, int n) {
    int i; for (i = 0; i < n; i = i + 1) dst[i] = src[i];
}
static int length(struct ring *p) {
#if EB_STYLE == 2
    return p->count;
#else
#if EB_STYLE != 3
    if (p->read == p->write && p->full) return p->capacity;
#endif
    return (p->write - p->read + p->capacity) % p->capacity;
#endif
}
static void put_data(struct ring *p, unsigned char *src, int n) {
    int i; int first;
#if EB_STYLE == 0 || EB_STYLE == 3
    first = p->capacity - p->write;
    if (first > n) first = n;
    copy_bytes(&p->data[p->write], src, first);
    copy_bytes(p->data, &src[first], n - first);
    p->write = (p->write + n) % p->capacity;
#else
    for (i = 0; i < n; i = i + 1) {
        p->data[p->write] = src[i]; p->write = (p->write + 1) % p->capacity;
    }
#endif
#if EB_STYLE == 2
    p->count = p->count + n;
#else
    p->full = (p->write == p->read);
#endif
}
static void get_data(struct ring *p, unsigned char *dst, int n) {
    int i; int first;
#if EB_STYLE == 0 || EB_STYLE == 3
    first = p->capacity - p->read;
    if (first > n) first = n;
    copy_bytes(dst, &p->data[p->read], first);
    copy_bytes(&dst[first], p->data, n - first);
    p->read = (p->read + n) % p->capacity;
#else
    for (i = 0; i < n; i = i + 1) {
        dst[i] = p->data[p->read]; p->read = (p->read + 1) % p->capacity;
    }
#endif
#if EB_STYLE == 2
    p->count = p->count - n;
#else
    p->full = 0;
#endif
}
static int write_bytes(struct ring *p, unsigned char *src, int n, int force) {
    int have = length(p); int free = p->capacity - have; int discard;
    if (force && n > free) {
        discard = n - free; p->read = (p->read + discard) % p->capacity;
#if EB_STYLE == 2
        p->count = p->count - discard;
#else
        p->full = 0;
#endif
    } else if (n > free) n = free;
    if (n == 0) return 0;
    put_data(p, src, n); return n;
}
static int read_bytes(struct ring *p, unsigned char *dst, int n) {
    int have = length(p);
    if (n > have) n = have;
    if (n == 0) return 0;
    get_data(p, dst, n); return n;
}
int main(void) {
    int q = eb_input[1]; int pos = 2; int i; int j; int op; int n; int actual; int remain;
    unsigned char src[64]; unsigned char dst[64];
    begin_output(); area.capacity = eb_input[0];
    area.read = 0; area.write = 0; area.full = 0; area.count = 0;
    for (i = 0; i < 64; i = i + 1) area.data[i] = 0;
    for (i = 0; i < q; i = i + 1) {
        op = eb_input[pos]; n = eb_input[pos + 1];
        for (j = 0; j < 64; j = j + 1) src[j] = (unsigned char)eb_input[pos + 2 + j];
        pos = pos + 66;
        if (op == 1) actual = read_bytes(&area, dst, n);
        else actual = write_bytes(&area, src, n, op == 2);
        emit(op); emit(actual == 0); emit(actual);
        if (op == 1) for (j = 0; j < actual; j = j + 1) emit(dst[j]);
    }
    emit(-2); remain = length(&area); emit(remain);
    for (i = 0; i < remain; i = i + 1) emit(area.data[(area.read + i) % area.capacity]);
    return end_output();
}
