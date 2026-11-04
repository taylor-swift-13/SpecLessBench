(* Protected comparison boundary. No algorithmic correctness oracle. *)
From Stdlib Require Import ZArith List.
Import ListNotations.
Open Scope Z_scope.

Definition InputWords : nat := 8192%nat.
Definition OutputWords : nat := 8192%nat.
Definition pad (n : nat) (xs : list Z) : list Z :=
  xs ++ repeat 0 (n - List.length xs).
Definition pack (xs : list Z) : list Z := pad InputWords xs.
Definition bounded_key (k : Z) : Prop := -1024 <= k <= 1024.
Definition bounded_value (v : Z) : Prop := -1000000 <= v <= 1000000.
Definition kv := (Z * Z)%type.
Definition valid_kv (x : kv) : Prop := bounded_key (fst x) /\ bounded_value (snd x).
Definition encode_kv (x : kv) : list Z := [fst x; snd x].

Module BST.
Inductive command := Delete (key : Z) | Lookup (key : Z).
Record input := { initial : list kv; commands : list command }.
Definition valid_command (c : command) : Prop :=
  match c with Delete k | Lookup k => bounded_key k end.
Definition valid (x : input) : Prop :=
  (List.length x.(initial) <= 32)%nat /\
  (List.length x.(commands) <= 64)%nat /\
  NoDup (map fst x.(initial)) /\ Forall valid_kv x.(initial) /\
  Forall valid_command x.(commands).
Definition encode_command (c : command) : list Z :=
  match c with Delete k => [0; k] | Lookup k => [1; k] end.
Definition encode (x : input) : list Z := pack
  ([Z.of_nat (List.length x.(initial)); Z.of_nat (List.length x.(commands))] ++
   flat_map encode_kv x.(initial) ++ flat_map encode_command x.(commands)).
End BST.

Module AVL.
Inductive command := Insert (key value : Z) | Lookup (key : Z).
Record input := { commands : list command }.
Definition valid_command (c : command) : Prop :=
  match c with
  | Insert k v => bounded_key k /\ bounded_value v
  | Lookup k => bounded_key k
  end.
Definition valid (x : input) : Prop :=
  (List.length x.(commands) <= 64)%nat /\ Forall valid_command x.(commands).
Definition encode_command (c : command) : list Z :=
  match c with Insert k v => [0; k; v] | Lookup k => [1; k; 0] end.
Definition encode (x : input) : list Z := pack
  ([Z.of_nat (List.length x.(commands))] ++ flat_map encode_command x.(commands)).
End AVL.

Module Ring.
Inductive command := Write (bytes : list Z) | Read (count : Z) | Force (bytes : list Z).
Record input := { capacity : Z; commands : list command }.
Definition valid_bytes (cap : Z) (xs : list Z) : Prop :=
  1 <= Z.of_nat (List.length xs) <= cap /\ Forall (fun b => 0 <= b <= 255) xs.
Definition valid_command (cap : Z) (c : command) : Prop :=
  match c with Write xs | Force xs => valid_bytes cap xs
  | Read n => 1 <= n <= cap end.
Definition valid (x : input) : Prop :=
  1 <= x.(capacity) <= 64 /\ (List.length x.(commands) <= 64)%nat /\
  Forall (valid_command x.(capacity)) x.(commands).
Definition encode_command (c : command) : list Z :=
  match c with
  | Write xs => [0; Z.of_nat (List.length xs)] ++ pad 64 xs
  | Read n => [1; n] ++ repeat 0 64
  | Force xs => [2; Z.of_nat (List.length xs)] ++ pad 64 xs
  end.
Definition encode (x : input) : list Z := pack
  ([x.(capacity); Z.of_nat (List.length x.(commands))] ++ flat_map encode_command x.(commands)).
End Ring.

Module Dijkstra.
Record edge := { source : Z; destination : Z; weight : Z }.
Record input := { vertices : Z; start : Z; edges : list edge }.
Definition valid_edge (n : Z) (e : edge) : Prop :=
  0 <= e.(source) < n /\ 0 <= e.(destination) < n /\ 0 <= e.(weight) <= 1000.
Definition valid (x : input) : Prop :=
  1 <= x.(vertices) <= 10 /\ 0 <= x.(start) < x.(vertices) /\
  (List.length x.(edges) <= 64)%nat /\ Forall (valid_edge x.(vertices)) x.(edges).
Definition encode_edge (e : edge) : list Z := [e.(source); e.(destination); e.(weight)].
Definition encode (x : input) : list Z := pack
  ([x.(vertices); Z.of_nat (List.length x.(edges)); x.(start)] ++ flat_map encode_edge x.(edges)).
End Dijkstra.
