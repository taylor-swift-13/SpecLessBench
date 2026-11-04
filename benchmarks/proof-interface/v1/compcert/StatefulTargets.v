From EqualBenchStateful Require Import FRAMESGoals TRANSACTIONSGoals LRUGoals.
Definition S_FRAME_RING_equivalence : Prop := FRAMESGoals.S_FRAME_RING_equivalence.
Definition S_FRAME_RING_refutationAt := FRAMESGoals.S_FRAME_RING_refutationAt.
Definition S_FRAME_EMPTY_equivalence : Prop := FRAMESGoals.S_FRAME_EMPTY_equivalence.
Definition S_FRAME_EMPTY_refutationAt := FRAMESGoals.S_FRAME_EMPTY_refutationAt.
Definition S_TX_JOURNAL_equivalence : Prop := TRANSACTIONSGoals.S_TX_JOURNAL_equivalence.
Definition S_TX_JOURNAL_refutationAt := TRANSACTIONSGoals.S_TX_JOURNAL_refutationAt.
Definition S_TX_COMMIT_equivalence : Prop := TRANSACTIONSGoals.S_TX_COMMIT_equivalence.
Definition S_TX_COMMIT_refutationAt := TRANSACTIONSGoals.S_TX_COMMIT_refutationAt.
Definition S_LRU_LINKS_equivalence : Prop := LRUGoals.S_LRU_LINKS_equivalence.
Definition S_LRU_LINKS_refutationAt := LRUGoals.S_LRU_LINKS_refutationAt.
Definition S_LRU_TOUCH_equivalence : Prop := LRUGoals.S_LRU_TOUCH_equivalence.
Definition S_LRU_TOUCH_refutationAt := LRUGoals.S_LRU_TOUCH_refutationAt.
