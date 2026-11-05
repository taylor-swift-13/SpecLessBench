From Coq Require Import ZArith List.
From Trusted Require Import Obligation.
Import ListNotations.

Module Submission.
Theorem solve : Obligation.goal.
Proof.
  exists [1%Z], [1%Z; 1%Z], [1%Z; 0%Z].
  vm_compute.
  repeat split; congruence.
Qed.
End Submission.
