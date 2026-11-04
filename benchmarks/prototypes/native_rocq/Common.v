From Coq Require Import Arith.PeanoNat Lists.List.
Import ListNotations.

(* Candidate reference and replacement implementations.  No independent
   functional specification is supplied. *)
Fixpoint factorial_ref (n : nat) : nat :=
  match n with
  | O => 1
  | S k => factorial_ref k * (S k)
  end.

Fixpoint factorial_acc (n acc : nat) : nat :=
  match n with
  | O => acc
  | S k => factorial_acc k ((S k) * acc)
  end.

(* A deliberately incorrect near-miss implementation for the negative task. *)
Fixpoint factorial_acc_mutant (n acc : nat) : nat :=
  match n with
  | O => acc
  | S k => factorial_acc_mutant k (acc * k)
  end.

Fixpoint reverse_ref {A : Type} (xs : list A) : list A :=
  match xs with
  | [] => []
  | x :: rest => reverse_ref rest ++ [x]
  end.

Fixpoint reverse_acc {A : Type} (xs acc : list A) : list A :=
  match xs with
  | [] => acc
  | x :: rest => reverse_acc rest (x :: acc)
  end.

Definition reverse_candidate {A : Type} (xs : list A) : list A :=
  reverse_acc xs [].

(* The only problem-level specification is relational: either prove equality
   for all admitted inputs or provide a valid input with different outputs. *)
Definition outcome {A B : Type}
    (pre : A -> Prop) (obs : B -> B -> Prop) (f g : A -> B) : Prop :=
  (forall x, pre x -> obs (f x) (g x)) \/
  (exists x, pre x /\ ~ obs (f x) (g x)).
