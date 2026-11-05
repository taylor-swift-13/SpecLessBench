From Trusted Require Import Obligation.

Definition solve : Obligation.goal.
Proof.
  unfold Obligation.goal, Task.refutationAt.
  repeat split; vm_compute; discriminate || reflexivity.
Defined.
