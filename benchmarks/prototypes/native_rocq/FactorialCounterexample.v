Require Import Common.

Theorem factorial_mutant_certificate :
  outcome (fun _ : nat => True) (@eq nat)
    factorial_ref (fun n => factorial_acc_mutant n 1).
Proof.
  right. exists 1. split.
  - exact I.
  - simpl. discriminate.
Qed.
