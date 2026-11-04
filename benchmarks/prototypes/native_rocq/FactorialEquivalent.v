From Coq Require Import Arith.PeanoNat Lia.
Require Import Common.

Lemma factorial_acc_correct :
  forall n acc, factorial_acc n acc = factorial_ref n * acc.
Proof.
  induction n as [|n IH]; intros acc; simpl.
  - rewrite Nat.add_0_r. reflexivity.
  - rewrite IH. nia.
Qed.

Theorem factorial_certificate :
  outcome (fun _ : nat => True) (@eq nat)
    factorial_ref (fun n => factorial_acc n 1).
Proof.
  left. intros n _. rewrite factorial_acc_correct. simpl.
  rewrite Nat.mul_1_r. reflexivity.
Qed.
