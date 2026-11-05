From Coq Require Import ZArith List.
Import ListNotations.
From Trusted Require Import Task.
Definition goal : Prop := Task.equivalent.
