#include "bst_def_new.h"

void free_tree_node(struct tree *b)
/*@ With g
    Require tree_node_store(g, b)
    Ensure emp
*/;

void delete(struct tree **b, int x)
/*@ With g
    Require INT_MIN <= x && x <= INT_MAX &&
            bst_gvalid(g) &&
            store(b, ptr_of(bst_root(g))) *
            tree_store(g)
    Ensure exists g' v,
           bst_gvalid(g') &&
           bst_delete(g, g', v, x) &&
           store(b, ptr_of(bst_root(g'))) *
           tree_store(g')
*/
{
  struct tree **cur = b;
  /*@ Inv Assert
      exists cur_src cur_v,
      b == b@pre &&
      INT_MIN <= x@pre && x@pre <= INT_MAX &&
      bst_gvalid(g) &&
      has_cur_source2(b, bst_root(g), g, cur_src, cur_v) &&
      cur_source_search_valid(g, cur_src, bst_root(g), x@pre) &&
      store(b, ptr_of(bst_root(g))) *
      store(&cur, cur_v) *
      store(&x, x@pre) *
      tree_store(g) */
  while (*cur != (void *)0) {
    if (x < (*cur)->key) {
      cur = &((*cur)->left);
    } else if ((*cur)->key < x) {
      cur = &((*cur)->right);
      } else {
        struct tree *target = *cur;
        if (target->left == (void *)0) {
          *cur = target->right;
          free_tree_node(target);
          return;
      }
      if (target->right == (void *)0) {
        *cur = target->left;
        free_tree_node(target);
        return;
      }
      struct tree **pre = &(target->right);
      /*@ Inv Assert
          exists pre_src pre_v target_v cur_src cur_v,
          b == b@pre &&
          INT_MIN <= x@pre && x@pre <= INT_MAX &&
          bst_gvalid(g) &&
          has_cur_source2(b, bst_root(g), g, cur_src, cur_v) &&
          bst_key_of(g, ptr_of(cur_source_value(g, cur_src, bst_root(g)))) == x@pre &&
          target_v == ptr_of(cur_source_value(g, cur_src, bst_root(g))) &&
          target_v != 0 &&
          has_cur_source2(b, bst_root(g), g, pre_src, pre_v) &&
          ptr_of(cur_source_value(g, pre_src, bst_root(g))) != 0 &&
          cur_src != pre_src &&
          target_v != ptr_of(cur_source_value(g, pre_src, bst_root(g))) &&
          cur_source_reachable(g, cur_src, pre_src, bst_root(g)) &&
          cur_source_successor_valid(g, target_v, ptr_of(cur_source_value(g, pre_src, bst_root(g)))) &&
          store(&cur, cur_v) *
          store(&target, target_v) *
          store(&x, x@pre) *
          store(&pre, pre_v) *
          store(b, ptr_of(bst_root(g))) *
          tree_store(g) */
      while ((*pre)->left != (void *)0) {
        pre = &((*pre)->left);
      }
      struct tree *pre_node = *pre;
      *pre = pre_node->right;
      pre_node->left = target->left;
      pre_node->right = target->right;
      *cur = pre_node;
      free_tree_node(target);
      return;
    }
  }
}
