From Trusted Require Import Obligation.
From Coq Require Import ZArith Ring List.

Lemma factorial_acc_correct : forall n a,
  BasicNative.factorial_acc false n a =
  (a * BasicNative.factorial_rec n)%Z.
Proof.
  induction n as [|n IH]; intro a.
  - change (a = a * 1)%Z. ring.
  - change (BasicNative.factorial_acc false n (a * Z.of_nat (S n)) =
      a * (Z.of_nat (S n) * BasicNative.factorial_rec n))%Z.
    rewrite IH. ring.
Qed.

Definition solve : Obligation.goal.
Proof.
  unfold Obligation.goal, BasicNative.Equivalent.
  intros x Hvalid.
  exists (BasicNative.finish
    (BasicNative.factorial_rec (Z.to_nat (BasicNative.iz x 0)) :: nil)).
  split.
  - reflexivity.
  - cbn [BasicNative.entry].
    rewrite factorial_acc_correct, Z.mul_1_l.
    reflexivity.
Qed.
