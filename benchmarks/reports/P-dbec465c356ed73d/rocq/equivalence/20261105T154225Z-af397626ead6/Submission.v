From Trusted Require Import Obligation.
From Coq Require Import ZArith List.
Import ListNotations.

Lemma factorial_acc_correct : forall n a,
  Task.factorial_acc false n a = (a * Task.factorial_rec n)%Z.
Proof.
  induction n as [|n IH]; intros a; cbn [Task.factorial_acc Task.factorial_rec].
  - ring.
  - rewrite IH. ring.
Qed.

Definition solve : Obligation.goal.
Proof.
  unfold Obligation.goal, Task.equivalent.
  intros x Hvalid.
  exists (Task.finish [Task.factorial_rec (Z.to_nat (Task.iz x 0))]).
  split.
  - reflexivity.
  - unfold Task.b. rewrite factorial_acc_correct.
    rewrite Z.mul_1_l. reflexivity.
Qed.
