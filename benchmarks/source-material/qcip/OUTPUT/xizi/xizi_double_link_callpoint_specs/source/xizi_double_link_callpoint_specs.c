#include "xizi_double_link_def.h"

/*@ Import Coq From SimpleC.EE.OUTPUT.xizi.xizi_double_link_callpoint_specs.source
      Require Import xizi_double_link_callpoint_specs_lib */
/*@ Extern Coq (XiziStoreADLL::DL_Node :: * => *) */
/*@ Extern Coq
      (xizi_store_dll : {A} -> (Z -> A -> Assertion) -> Z -> list (XiziStoreADLL::DL_Node A) -> Assertion)
      (xizi_dll_ptrs : {A} -> list (XiziStoreADLL::DL_Node A) -> list Z)
      (XiziStoreADLL::Build_DL_Node : {A} -> A -> Z -> XiziStoreADLL::DL_Node A)
      (XiziStoreADLL::getPtr : {A} -> XiziStoreADLL::DL_Node A -> Z)
      (XiziStoreADLL::getData : {A} -> XiziStoreADLL::DL_Node A -> A)
      (xizi_double_link_first_value : list Z -> Z)
      (xizi_double_link_call_empty_result : Z -> Prop)
      (xizi_double_link_call_null_result : Z -> Prop)
      (xizi_double_link_call_len_result : Z -> Prop)
      (xizi_double_link_singleton_nodes : {A} -> XiziStoreADLL::DL_Node A -> list (XiziStoreADLL::DL_Node A))
 */

void InitDoubleLinkList(DoubleLinklistType *linklist_head)
/*@ With {A} (storeA : Z -> A -> Assertion)
    Require
      xizi_dll_node(linklist_head)
    Ensure
      xizi_store_dll(storeA, linklist_head, nil)
*/;

int IsDoubleLinkListEmpty(const DoubleLinklistType *linklist)
/*@ nil_case
    With {A} (storeA : Z -> A -> Assertion)
    Require
      xizi_store_dll(storeA, linklist, nil)
    Ensure
      __return == 1 &&
      xizi_store_dll(storeA, linklist, nil)
*/;

struct SysDoubleLinklistNode *DoubleLinkListGetHead(
    const DoubleLinklistType *linklist)
/*@ nil_case
    With {A} (storeA : Z -> A -> Assertion)
    Require xizi_store_dll(storeA, linklist, nil)
    Ensure __return == 0 &&
           xizi_store_dll(storeA, linklist, nil)
 */;

unsigned int DoubleLinkListLenGet(const DoubleLinklistType *linklist)
/*@ nil_case
    With {A} (storeA : Z -> A -> Assertion)
    Require
      xizi_store_dll(storeA, linklist, nil)
    Ensure
      __return == 0 &&
      xizi_store_dll(storeA, linklist, nil)
*/;

struct SysDoubleLinklistNode *DoubleLinkListGetNext(
    const DoubleLinklistType *linklist,
    const struct SysDoubleLinklistNode *linklist_node)
/*@ sentinel_case
    With {A} (storeA : Z -> A -> Assertion)
         (nodes : list (XiziStoreADLL::DL_Node A))
    Require linklist_node == linklist &&
            xizi_store_dll(storeA, linklist, nodes)
    Ensure __return == xizi_double_link_first_value(xizi_dll_ptrs(nodes)) &&
           xizi_store_dll(storeA, linklist, nodes)
*/;

void DoubleLinkListInsertNodeAfter(DoubleLinklistType *linklist,
                                   DoubleLinklistType *linklist_node)
/*@ sentinel_case
    With {A} (storeA : Z -> A -> Assertion) (data : A) (nodes: list (XiziStoreADLL::DL_Node A))
    Require xizi_store_dll(storeA, linklist, nodes) *
            xizi_dll_node(linklist_node) * storeA(linklist_node, data)
    Ensure xizi_store_dll(storeA, linklist,
                    cons(XiziStoreADLL::Build_DL_Node(data, linklist_node), nodes))
*/;

void DoubleLinkListRmNode(DoubleLinklistType *linklist_node)
/*@ remove_front_spec
    With {A} (storeA : Z -> A -> Assertion)
         (head : Z) (removed : XiziStoreADLL::DL_Node A)
         (suffix : list (XiziStoreADLL::DL_Node A))
    Require XiziStoreADLL::getPtr(removed) == linklist_node &&
            xizi_store_dll(storeA, head, cons(removed, suffix))
    Ensure xizi_store_dll(storeA, head, suffix) *
           xizi_dll(linklist_node, nil) *
           storeA(linklist_node, XiziStoreADLL::getData(removed))
*/;

void DoubleLinkListRmNode(DoubleLinklistType *linklist_node)
/*@ remove_tail_spec
    With {A} (storeA : Z -> A -> Assertion)
         (head : Z) (removed : XiziStoreADLL::DL_Node A)
         (prefix : list (XiziStoreADLL::DL_Node A))
    Require XiziStoreADLL::getPtr(removed) == linklist_node &&
            xizi_store_dll(storeA, head, app(prefix, cons(removed, nil)))
    Ensure xizi_store_dll(storeA, head, prefix) *
           xizi_dll(linklist_node, nil) *
           storeA(linklist_node, XiziStoreADLL::getData(removed))
*/;

int xizi_double_link_call_empty_after_init(DoubleLinklistType *head)
/*@ With {A} (storeA : Z -> A -> Assertion)
    Require
      xizi_dll_node(head)
    Ensure
      xizi_double_link_call_empty_result(__return) &&
      xizi_store_dll(storeA, head, nil)
*/
{
    InitDoubleLinkList(head) /*@ where storeA = storeA; A = A */;
    return IsDoubleLinkListEmpty(head) /*@ where (nil_case) storeA = storeA; A = A */;
}

int xizi_double_link_call_empty_rec_after_init(DoubleLinklistType *head)
/*@ With {A} (storeA : Z -> A -> Assertion)
    Require
      xizi_dll_node(head)
    Ensure
      xizi_double_link_call_empty_result(__return) &&
      xizi_store_dll(storeA, head, nil)
*/
{
    InitDoubleLinkList(head) /*@ where storeA = storeA; A = A */;
    return IsDoubleLinkListEmpty(head) /*@ where (nil_case) storeA = storeA; A = A */;
}

struct SysDoubleLinklistNode *xizi_double_link_call_head_after_init(
    DoubleLinklistType *head)
/*@ With {A} (storeA : Z -> A -> Assertion)
    Require
      xizi_dll_node(head)
    Ensure
      xizi_double_link_call_null_result(__return) &&
      xizi_store_dll(storeA, head, nil)
*/
{
    InitDoubleLinkList(head) /*@ where storeA = storeA; A = A */;
    return DoubleLinkListGetHead(head) /*@ where (nil_case) storeA = storeA; A = A */;
}

struct SysDoubleLinklistNode *xizi_double_link_call_head_rec_after_init(
    DoubleLinklistType *head)
/*@ With {A} (storeA : Z -> A -> Assertion)
    Require
      xizi_dll_node(head)
    Ensure
      xizi_double_link_call_null_result(__return) &&
      xizi_store_dll(storeA, head, nil)
*/
{
    InitDoubleLinkList(head) /*@ where storeA = storeA; A = A */;
    return DoubleLinkListGetHead(head) /*@ where (nil_case) storeA = storeA; A = A */;
}

unsigned int xizi_double_link_call_len_after_init(DoubleLinklistType *head)
/*@ With {A} (storeA : Z -> A -> Assertion)
    Require
      xizi_dll_node(head)
    Ensure
      xizi_double_link_call_len_result(__return) &&
      xizi_store_dll(storeA, head, nil)
*/
{
    InitDoubleLinkList(head) /*@ where storeA = storeA; A = A */;
    return DoubleLinkListLenGet(head) /*@ where (nil_case) storeA = storeA; A = A */;
}

struct SysDoubleLinklistNode *xizi_double_link_call_next_after_init(
    DoubleLinklistType *head)
/*@ With {A} (storeA : Z -> A -> Assertion)
    Require
      xizi_dll_node(head)
    Ensure
      xizi_double_link_call_null_result(__return) &&
      xizi_store_dll(storeA, head, nil)
*/
{
    InitDoubleLinkList(head) /*@ where storeA = storeA; A = A */;
    /*@ Assert
            head == head@pre &&
            xizi_store_dll(storeA, head, nil)
    */
    return DoubleLinkListGetNext(head, head) /*@ where (sentinel_case) storeA = storeA; A = A */;
}

struct SysDoubleLinklistNode *xizi_double_link_call_next_rec_last_after_init(
    DoubleLinklistType *head)
/*@ With {A} (storeA : Z -> A -> Assertion)
    Require
      xizi_dll_node(head)
    Ensure
      xizi_double_link_call_null_result(__return) &&
      xizi_store_dll(storeA, head, nil)
*/
{
    InitDoubleLinkList(head) /*@ where storeA = storeA; A = A */;
    /*@ Assert
            head == head@pre &&
            xizi_store_dll(storeA, head, nil)
    */
    return DoubleLinkListGetNext(head, head)
      /*@ where (sentinel_case) storeA = storeA; A = A */;
}

struct SysDoubleLinklistNode *xizi_double_link_call_next_rec_middle_after_init(
    DoubleLinklistType *head)
/*@ With {A} (storeA : Z -> A -> Assertion)
    Require
      xizi_dll_node(head)
    Ensure
      xizi_double_link_call_null_result(__return) &&
      xizi_store_dll(storeA, head, nil)
*/
{
    InitDoubleLinkList(head) /*@ where storeA = storeA; A = A */;
    /*@ Assert
            head == head@pre &&
            xizi_store_dll(storeA, head, nil)
    */
    return DoubleLinkListGetNext(head, head)
      /*@ where (sentinel_case) storeA = storeA; A = A */;
}

void xizi_double_link_call_insert_after_init(DoubleLinklistType *head,
                                             DoubleLinklistType *node)
/*@ With {A} (storeA : Z -> A -> Assertion) (data : A)
    Require
      xizi_dll_node(head) *
      xizi_dll_node(node) * storeA(node, data)
    Ensure
      xizi_store_dll(storeA, head,
               xizi_double_link_singleton_nodes(XiziStoreADLL::Build_DL_Node(data, node)))
*/
{
    InitDoubleLinkList(head) /*@ where storeA = storeA; A = A */;
    /*@ Assert
            head == head@pre &&
            node == node@pre &&
            xizi_store_dll(storeA, head, nil) *
            xizi_dll_node(node) * storeA(node, data)
    */
    DoubleLinkListInsertNodeAfter(head, node)
      /*@ where (sentinel_case) storeA = storeA, data = data; A = A */;
}

void xizi_double_link_call_remove_front_singleton(DoubleLinklistType *head,
                                                  DoubleLinklistType *node)
/*@ With {A} (storeA : Z -> A -> Assertion) (data : A)
    Require
      xizi_dll_node(head) *
      xizi_dll_node(node) * storeA(node, data)
    Ensure
      xizi_store_dll(storeA, head, nil) *
      xizi_dll(node, nil) * storeA(node, data)
*/
{
    InitDoubleLinkList(head) /*@ where storeA = storeA; A = A */;
    /*@ Assert
            head == head@pre &&
            node == node@pre &&
            xizi_store_dll(storeA, head, nil) *
            xizi_dll_node(node) * storeA(node, data)
    */
    DoubleLinkListInsertNodeAfter(head, node)
      /*@ where (sentinel_case) storeA = storeA, data = data; A = A */;
    /*@ Assert
            head == head@pre &&
            node == node@pre &&
            xizi_store_dll(storeA, head, cons(XiziStoreADLL::Build_DL_Node(data, node), nil))
    */
    DoubleLinkListRmNode(node)
      /*@ where (remove_front_spec) storeA = storeA, head = head, removed = XiziStoreADLL::Build_DL_Node(data, node); A = A */;
}

void xizi_double_link_call_remove_tail_singleton(DoubleLinklistType *head,
                                                 DoubleLinklistType *node)
/*@ With {A} (storeA : Z -> A -> Assertion) (data : A)
    Require
      xizi_dll_node(head) *
      xizi_dll_node(node) * storeA(node, data)
    Ensure
      xizi_store_dll(storeA, head, nil) *
      xizi_dll(node, nil) * storeA(node, data)
*/
{
    InitDoubleLinkList(head) /*@ where storeA = storeA; A = A */;
    /*@ Assert
            head == head@pre &&
            node == node@pre &&
            xizi_store_dll(storeA, head, nil) *
            xizi_dll_node(node) * storeA(node, data)
    */
    DoubleLinkListInsertNodeAfter(head, node)
      /*@ where (sentinel_case) storeA = storeA, data = data; A = A */;
    /*@ Assert
            head == head@pre &&
            node == node@pre &&
            xizi_store_dll(storeA, head, app(nil, cons(XiziStoreADLL::Build_DL_Node(data, node), nil)))
    */
    DoubleLinkListRmNode(node)
      /*@ where (remove_tail_spec) storeA = storeA, head = head, removed = XiziStoreADLL::Build_DL_Node(data, node); A = A */;
}
