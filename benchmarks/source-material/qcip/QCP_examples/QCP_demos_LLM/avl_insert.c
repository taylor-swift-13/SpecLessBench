#include "avl_def.h"



struct tree *malloc_tree_node()
/*@
    Require emp
    Ensure __return != 0 &&
    has_permission(&(__return -> key)) *
    has_permission(&(__return -> height)) *
    has_permission(&(__return -> value)) *
    has_permission(&(__return -> lchild)) *
    has_permission(&(__return -> rchild))
*/
;

void update_height(struct tree *root) 
/*@ 
    Require store_non_empty_tree(root)
    Ensure store_non_empty_tree(root)
*/
{
    unsigned char lh = (unsigned char)0, rh = (unsigned char)0;
    if (root->lchild != (void *)0) {
        lh = root->lchild->height;
    }
    if (root->rchild != (void *)0) {
        rh = root->rchild->height;
    }
    if (lh > rh) {
        root->height = (unsigned char)(lh + (unsigned char)1);
    } else {
        root->height = (unsigned char)(rh + (unsigned char)1);
    }
}

struct tree *rotateR(struct tree *root) 
/*@
    With l r k v h
    Require root != 0 &&
            single_tree_node(root,k,v,h,l,r) *
            store_non_empty_tree(l) *
            store_tree_shape(r)
    Ensure  __return == l &&
            store_non_empty_tree(l)
            
*/
{
    struct tree *temp = root->lchild;
    root->lchild = temp->rchild;
    temp->rchild = root;
    update_height(root);
    update_height(temp);
    return temp;
}

struct tree *rotateL(struct tree *root)
/*@
    With l r k v h
    Require root != 0 &&
            single_tree_node(root,k,v,h,l,r) *
            store_tree_shape(l) *
            store_non_empty_tree(r) 
    Ensure  __return == r &&
            store_non_empty_tree(r)
            
*/
{
    struct tree *temp = root->rchild;
    root->rchild = temp->lchild;
    temp->lchild = root;
    update_height(root);
    update_height(temp);
    return temp;
}

struct tree *rotateRL(struct tree *root) 
/*@
    With k v h l r k1 v1 h1 l1 r1
    Require root != 0 &&
            r != 0 &&
            single_tree_node(root,k,v,h,l,r) *
            single_tree_node(r,k1,v1,h1,l1,r1) *
            store_tree_shape(l) *
            store_non_empty_tree(l1) *
            store_tree_shape(r1)
    Ensure __return == l1 &&
            store_non_empty_tree(l1)
*/
{
    root->rchild = rotateR(root->rchild)/*@ where k=k1, v = v1, h=h1,l=l1,r=r1 */;
    struct tree *temp = rotateL(root)/*@ where r=l1*/;
    return temp;
}

struct tree *rotateLR(struct tree *root)
/*@
    With k v h l r k1 v1 h1 l1 r1
    Require root != 0 &&
            l != 0 &&
            single_tree_node(root,k,v,h,l,r) *
            single_tree_node(l,k1,v1,h1,l1,r1) *
            store_tree_shape(r) *
            store_tree_shape(l1) *
            store_non_empty_tree(r1)
    Ensure  __return == r1 &&
            store_non_empty_tree(r1)
*/
{
    root->lchild = rotateL(root->lchild)/*@ where k=k1, v = v1, h=h1,l=l1,r=r1 */;
    struct tree *temp = rotateR(root)/*@ where l=r1*/;
    return temp;
}


int balance_factor(struct tree *root)
/*@ Require store_tree_shape(root)
    Ensure  (__return == 0 && (store_tree_shape(root) )) ||
            (__return >= 0 && exists k v h l r,
                            root != 0 &&
                             single_tree_node(root,k,v,h,l,r) *
                             store_non_empty_tree(l) *
                             store_tree_shape(r))  ||
            (__return <= 0 && exists k v h l r,
                            root != 0 &&
                            single_tree_node(root,k,v,h,l,r) *
                            store_tree_shape(l) *
                            store_non_empty_tree(r)) ||
            (exists k v h l r x,
                __return == x &&
                root != 0 &&
                single_tree_node(root,k,v,h,l,r) *
                store_non_empty_tree(l) *
                store_non_empty_tree(r))
*/
{
    unsigned char lh = (unsigned char)0, rh = (unsigned char)0;
    if(root == (void *)0){
        return 0;
    }
    if (root->lchild != (void *)0) {
        lh = root->lchild->height;
    }
    if (root->rchild != (void *)0) {
        rh = root->rchild->height;
    }
    return (int)(lh) - (int)(rh);
}

void balance(struct tree **p)
/*@ 
    Require store_tree_shape(*p)
    Ensure store_tree_shape(*p)  
*/
{
    struct tree *root = *p;
    int lh =0,rh=0;
    int bf = balance_factor(root);
    if(bf>1){
        int lbf = balance_factor(root->lchild);
        if(lbf>0){
            *p = rotateR(root)/*@ where l=(root->lchild) */;
            return;
        }
        if(lbf<0){
            *p = rotateLR(root)/*@ where l=(root->lchild),r1=((root->lchild)->rchild) */;
            return;
        }
        return;   
    }
    if(bf<-1){
        int rbf = balance_factor(root->rchild);
        if(rbf<0){
            *p = rotateL(root)/*@ where r=(root->rchild) */;
            return;
        }
        if(rbf>0){
            *p = rotateRL(root)/*@ where r=(root->rchild), l1=((root->rchild)->lchild) */;
            return;
        }
        return;
    }
}

void insert(struct tree **p, int key,int value)
/*@ 
    Require store_tree_shape(*p)
    Ensure  store_tree_shape(*p)
*/
{
    struct tree *root = *p;
    if (root == (void *)0) {
        root = malloc_tree_node();
        root->key = key;
        root->value = value;
        root->lchild = (void *)0;
        root->rchild = (void *)0;
        root->height = (unsigned char)1;
        *p = root;
        return;
    }
    if (key < root->key) {
        insert(&root->lchild, key, value);
    } else if (key > root->key) {
        insert(&root->rchild, key, value);
    } else {
        return;
    }
    update_height(root);
    balance(p);
}

