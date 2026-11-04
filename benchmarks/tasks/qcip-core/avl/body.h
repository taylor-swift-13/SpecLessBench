/* QCIP-derived insert/balance/rotate family. See ../PROVENANCE.md.
 * Styles: 0 recursive/factored, 1 ancestor stack, 2 recursive/inline doubles,
 * 3 recursive with dropped middle subtree in rotate_left. */
#include "../common/io.h"
struct node { int key; int value; unsigned char height; struct node *left; struct node *right; };
static struct node arena[64];
static int used;
static struct node *root;
static int height(struct node *p) { if (p == (void *)0) return 0; return p->height; }
static void update_height(struct node *p) {
    int l = height(p->left); int r = height(p->right);
    if (l > r) p->height = (unsigned char)(l + 1);
    else p->height = (unsigned char)(r + 1);
}
static int balance_factor(struct node *p) {
    if (p == (void *)0) return 0;
    return height(p->left) - height(p->right);
}
static struct node *new_node(int k, int v) {
    struct node *p = &arena[used]; used = used + 1;
    p->key = k; p->value = v; p->height = 1;
    p->left = (void *)0; p->right = (void *)0; return p;
}
static struct node *rotate_left(struct node *p) {
    struct node *q = p->right;
#if EB_STYLE == 3
    p->right = (void *)0;
#else
    p->right = q->left;
#endif
    q->left = p; update_height(p); update_height(q); return q;
}
static struct node *rotate_right(struct node *p) {
    struct node *q = p->left;
    p->left = q->right; q->right = p;
    update_height(p); update_height(q); return q;
}
#if EB_STYLE != 2
static struct node *rotate_lr(struct node *p) {
    p->left = rotate_left(p->left); return rotate_right(p);
}
static struct node *rotate_rl(struct node *p) {
    p->right = rotate_right(p->right); return rotate_left(p);
}
#endif
static void balance(struct node **b) {
    struct node *p = *b;
    int bf = balance_factor(p);
    if (bf > 1) {
        if (balance_factor(p->left) > 0) *b = rotate_right(p);
        else if (balance_factor(p->left) < 0) {
#if EB_STYLE == 2
            p->left = rotate_left(p->left); *b = rotate_right(p);
#else
            *b = rotate_lr(p);
#endif
        }
    } else if (bf < -1) {
        if (balance_factor(p->right) < 0) *b = rotate_left(p);
        else if (balance_factor(p->right) > 0) {
#if EB_STYLE == 2
            p->right = rotate_right(p->right); *b = rotate_left(p);
#else
            *b = rotate_rl(p);
#endif
        }
    }
}
#if EB_STYLE == 1
static void insert(struct node **b, int k, int v) {
    struct node **path[64]; int depth = 0;
    while (*b != (void *)0) {
        if (k == (*b)->key) return;
        path[depth] = b; depth = depth + 1;
        if (k < (*b)->key) b = &(*b)->left;
        else b = &(*b)->right;
    }
    *b = new_node(k, v);
    while (depth > 0) {
        depth = depth - 1; update_height(*path[depth]); balance(path[depth]);
    }
}
#else
static void insert(struct node **b, int k, int v) {
    struct node *p = *b;
    if (p == (void *)0) { *b = new_node(k, v); return; }
    if (k < p->key) insert(&p->left, k, v);
    else if (k > p->key) insert(&p->right, k, v);
    else return;
    update_height(p); balance(b);
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
    int q = eb_input[0]; int pos = 1; int i; int op; int k; int v;
    begin_output(); root = (void *)0; used = 0;
    for (i = 0; i < q; i = i + 1) {
        op = eb_input[pos]; k = eb_input[pos + 1]; v = eb_input[pos + 2]; pos = pos + 3;
        emit(op);
        if (op == 0) { insert(&root, k, v); emit(0); }
        else lookup(k);
    }
    emit(-2); project(root);
    return end_output();
}
