From Coq Require Import ZArith List.
Import ListNotations.
From Trusted Require Import Task.
Definition goal : Prop := Task.refutationAt [1%Z] [1%Z;1%Z] [1%Z;0%Z].
