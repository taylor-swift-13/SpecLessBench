#include "binaryTree_def.h"

/* Invert (mirror) a binary tree in place: recursively swap the two
 * children of every node. */
void invert_tree(struct tree *root)
/*@ With tr
    Require store_tree(root, tr)
    Ensure store_tree(root, tree_mirror(tr))
*/
{
    if (root == (void *)0) {
        return;
    }
    struct tree *tmp = root->lchild;
    root->lchild = root->rchild;
    root->rchild = tmp;
    invert_tree(root->lchild);
    invert_tree(root->rchild);
}
