From Coq Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words := list Z.
Definition iz (xs : words) (i : nat) := nth i xs 0%Z.
Definition finish (xs : words) := Z.of_nat (length xs)::xs.
Fixpoint factorial_rec n : Z := match n with O => 1%Z | S k => (Z.of_nat (S k)*factorial_rec k)%Z end.
Fixpoint factorial_acc (mutant : bool) n a : Z := match n with O => a | S k =>
  factorial_acc mutant k (a*Z.of_nat (if mutant then k else S k))%Z end.
Definition in_range v lo hi := Z.leb lo v && Z.leb v hi.
Definition valid (xs : words) := (Nat.eqb (length xs) 1 && in_range (iz xs 0) 0 12) = true.
Definition a (xs : words) : option words := Some (finish [factorial_rec (Z.to_nat (iz xs 0))]).
Definition b (xs : words) : option words := Some (finish [factorial_acc true (Z.to_nat (iz xs 0)) 1%Z]).
Definition equivalent : Prop := forall x, valid x -> exists o, a x=Some o /\ b x=Some o.
Definition refutationAt (x oa ob : words) : Prop := valid x /\ a x=Some oa /\ b x=Some ob /\ oa<>ob.
