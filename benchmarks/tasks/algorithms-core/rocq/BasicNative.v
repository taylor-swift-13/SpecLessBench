From Coq Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words := list Z.
Definition iz (xs : words) (i : nat) := nth i xs 0%Z.
Definition put (xs : words) i v := firstn i xs ++ [v] ++ skipn (S i) xs.
Definition finish (xs : words) := Z.of_nat (length xs)::xs.
Definition obind {A B} (x : option A) (f : A -> option B) := match x with Some a => f a | None => None end.
Notation "'let*' x ':=' c 'in' b" := (obind c (fun x => b)) (at level 200, x ident, c at level 100, b at level 200).
Fixpoint factorial_rec n : Z := match n with O => 1%Z | S k => (Z.of_nat (S k)*factorial_rec k)%Z end.
Fixpoint factorial_acc (mutant : bool) n a : Z := match n with O => a | S k =>
  factorial_acc mutant k (a*Z.of_nat (if mutant then k else S k))%Z end.
Fixpoint reverse_rec (xs : words) := match xs with [] => [] | x::tail => reverse_rec tail ++ [x] end.
Fixpoint reverse_acc (xs a : words) := match xs with [] => a | x::tail => reverse_acc tail (x::a) end.
Fixpoint sum_rec (xs : words) : Z := match xs with [] => 0%Z | x::tail => (x+sum_rec tail)%Z end.
Fixpoint sum_acc (xs : words) a : Z := match xs with [] => a | x::tail => sum_acc tail (a+x)%Z end.
Definition matrix style xs :=
  let r := Z.to_nat (iz xs 0) in let k := Z.to_nat (iz xs 1) in let c := Z.to_nat (iz xs 2) in
  if Nat.eqb style 1 then
    fold_left (fun out i => fold_left (fun out t => fold_left (fun out j =>
      put out (i*c+j) (iz out (i*c+j)+iz xs (3+i*k+t)*iz xs (3+r*k+t*c+j))%Z) (seq 0 c) out) (seq 0 k) out)
      (seq 0 r) (repeat 0%Z (r*c))
  else map (fun pos => let i := pos/c in let j := pos mod c in
    fold_left (fun a t => (a+iz xs (3+i*k+t)*iz xs (3+r*k+(if Nat.eqb style 2 then j*k+t else t*c+j)))%Z) (seq 0 k) 0%Z) (seq 0 (r*c)).
Definition matches text pat pos := forallb (fun j => Z.eqb (iz text (pos+j)) (iz pat j)) (seq 0 (length pat)).
Definition naive_search text pat : Z :=
  if Nat.ltb (length text) (length pat) then (-1)%Z else
  match find (matches text pat) (seq 0 (length text-length pat+1)) with None => (-1)%Z | Some i => Z.of_nat i end.
Fixpoint fallback (mutant : bool) pat (prefix : list nat) b fuel j := match fuel with
| O => None | S f => if Nat.ltb 0 j && negb (Z.eqb b (iz pat j)) then
  fallback mutant pat prefix b f (if mutant then 0 else nth (j-1) prefix 0) else Some j end.
Definition prefix_table pat := fold_left (fun state z => let* tab := state in
  let i := z+1 in let* j := fallback false pat tab (iz pat i) 34 (nth (i-1) tab 0) in
  Some (tab ++ [if Z.eqb (iz pat i) (iz pat j) then j+1 else j])) (seq 0 (length pat-1)) (Some [0]).
Fixpoint kmp_loop mutant text pat tab fuel i j : option Z := match fuel with
| O => Some (-1)%Z | S f =>
  let* j' := fallback mutant pat tab (iz text i) 34 j in
  let next := if Z.eqb (iz text i) (iz pat j') then j'+1 else j' in
  if Nat.eqb next (length pat) then Some (Z.of_nat (i+1)-Z.of_nat (length pat))%Z
  else kmp_loop mutant text pat tab f (i+1) next end.
Definition kmp mutant text pat := if Nat.eqb (length pat) 0 then Some 0%Z else
  let* tab := prefix_table pat in kmp_loop mutant text pat tab (length text) 0 0.
Definition queue style xs :=
  let '(_,_,out) := fold_left (fun state i => let '(front,rear,out) := state in
    let op := iz xs (1+2*i) in let v := iz xs (2+2*i) in
    if Z.eqb op 0 then if Nat.eqb style 0 then (front++[v],rear,out++[0%Z;0%Z])
      else (front,v::rear,out++[0%Z;0%Z])
    else let '(f,r) := if negb (Nat.eqb style 0) && Nat.eqb (length front) 0 then
      (reverse_rec rear,if Nat.eqb style 2 then rear else []) else (front,rear) in
    match f with [] => (f,r,out++[op;0%Z;0%Z]) | a::rest =>
      (if Z.eqb op 1 then rest else f,r,out++[op;1%Z;a]) end)
    (seq 0 (Z.to_nat (iz xs 0))) (([]:words),([]:words),([]:words)) in out.
Definition entry family style xs : option words := match family with
| O => Some (finish [if Nat.eqb style 0 then factorial_rec (Z.to_nat (iz xs 0)) else factorial_acc (Nat.eqb style 2) (Z.to_nat (iz xs 0)) 1%Z])
| S O => let data := firstn (Z.to_nat (iz xs 0)) (skipn 1 xs) in
    Some (finish (if Nat.eqb style 0 then reverse_rec data else reverse_acc data (if Nat.eqb style 2 then [0%Z] else [])))
| S (S O) => let data := firstn (Z.to_nat (iz xs 0)) (skipn 1 xs) in
    Some (finish [if Nat.eqb style 0 then sum_rec data else sum_acc (if Nat.eqb style 2 then firstn (length data-1) data else data) 0%Z])
| S (S (S O)) => Some (finish (matrix style xs))
| S (S (S (S O))) => let n := Z.to_nat (iz xs 0) in let m := Z.to_nat (iz xs 1) in
    let text := firstn n (skipn 2 xs) in let pat := firstn m (skipn (2+n) xs) in
    let* result := if Nat.eqb style 0 then Some (naive_search text pat) else kmp (Nat.eqb style 2) text pat in Some (finish [result])
| _ => Some (finish (queue style xs)) end.
Definition Equivalent (valid : words -> Prop) (a b : words -> option words) :=
  forall x, valid x -> exists o, a x=Some o /\ b x=Some o.
Definition Counterexample (valid : words -> Prop) (a b : words -> option words) :=
  exists x oa ob, valid x /\ a x=Some oa /\ b x=Some ob /\ oa<>ob.
Definition Certificate (valid : words -> Prop) (a b : words -> option words) := Equivalent valid a b \/ Counterexample valid a b.
