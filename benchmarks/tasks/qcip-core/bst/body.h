/* Derived from QCIP predecessor/successor deletion and VST pushdown deletion.
 * See ../PROVENANCE.md and ../NOTICE.md. EB_STYLE: 0 pred, 1 succ, 2 rotate,
 * 3 pred with one value-copy mutation. All included code is protected. */
#include "../common/io.h"
struct node { int key; int value; int live; struct node *left; struct node *right; };
static struct node arena[32];
static int used;
static struct node *root;
static struct node *new_node(int k, int v) {
    struct node *p = &arena[used];
    used = used + 1;
    p->key = k; p->value = v; p->live = 1;
    p->left = (void *)0; p->right = (void *)0;
    return p;
}
static void retire(struct node *p) { p->live = 0; }
static void initial_insert(int k, int v) {
    struct node **p = &root;
    while (*p != (void *)0) {
        if (k < (*p)->key) p = &(*p)->left;
        else p = &(*p)->right;
    }
    *p = new_node(k, v);
}
#if EB_STYLE == 0 || EB_STYLE == 3
static struct node **get_pre(struct node **p) {
    if ((*p)->right == (void *)0) return p;
    return get_pre(&(*p)->right);
}
static void erase(struct node **b, int k) {
    struct node *p = *b;
    struct node **pre;
    struct node *old;
    if (p == (void *)0) return;
    if (k < p->key) erase(&p->left, k);
    else if (k > p->key) erase(&p->right, k);
    else if (p->left == (void *)0) { *b = p->right; retire(p); }
    else {
        pre = get_pre(&p->left);
        p->key = (*pre)->key;
#if EB_STYLE == 0
        p->value = (*pre)->value;
#endif
        old = *pre; *pre = old->left; retire(old);
    }
}
#elif EB_STYLE == 1
static void erase(struct node **b, int k) {
    struct node **cur = b;
    struct node **succ;
    struct node *target;
    struct node *p;
    while (*cur != (void *)0) {
        if (k < (*cur)->key) cur = &(*cur)->left;
        else if (k > (*cur)->key) cur = &(*cur)->right;
        else {
            target = *cur;
            if (target->left == (void *)0) *cur = target->right;
            else if (target->right == (void *)0) *cur = target->left;
            else {
                succ = &target->right;
                while ((*succ)->left != (void *)0) succ = &(*succ)->left;
                p = *succ; *succ = p->right;
                p->left = target->left; p->right = target->right; *cur = p;
            }
            retire(target); return;
        }
    }
}
#else
static void turn_left(struct node **b, struct node *p, struct node *q) {
    p->right = q->left; q->left = p; *b = q;
}
static void pushdown_left(struct node **b) {
    struct node *p;
    struct node *q;
    for (;;) {
        p = *b; q = p->right;
        if (q == (void *)0) { *b = p->left; retire(p); return; }
        turn_left(b, p, q); b = &q->left;
    }
}
static void erase(struct node **b, int k) {
    while (*b != (void *)0) {
        if (k < (*b)->key) b = &(*b)->left;
        else if (k > (*b)->key) b = &(*b)->right;
        else { pushdown_left(b); return; }
    }
}
#endif
static void lookup(int k) {
    struct node *p = root;
    while (p != (void *)0) {
        if (k < p->key) p = p->left;
        else if (k > p->key) p = p->right;
        else { emit(1); emit(p->value); return; }
    }
    emit(0); emit(0);
}
static void project(struct node *p) {
    if (p != (void *)0) {
        project(p->left); emit(p->key); emit(p->value); project(p->right);
    }
}
int main(void) {
    int n = eb_input[0]; int q = eb_input[1]; int pos = 2; int i; int op; int k;
    begin_output(); root = (void *)0; used = 0;
    for (i = 0; i < n; i = i + 1) {
        initial_insert(eb_input[pos], eb_input[pos + 1]); pos = pos + 2;
    }
    for (i = 0; i < q; i = i + 1) {
        op = eb_input[pos]; k = eb_input[pos + 1]; pos = pos + 2;
        emit(op);
        if (op == 0) { erase(&root, k); emit(0); }
        else lookup(k);
    }
    emit(-2); project(root);
    return end_output();
}
