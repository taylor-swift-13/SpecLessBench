From Coq Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words := list Z.
Definition get (xs : words) i := nth i xs 0%Z.
Definition in_range v lo hi := Z.leb lo v && Z.leb v hi.
Definition validb family xs :=
  let a := get xs 0 in let b := get xs 1 in let c := get xs 2 in
  let n := Z.to_nat a in let m := Z.to_nat b in let z := Z.to_nat c in
  match family with
  | O => Nat.eqb (length xs) 1 && in_range a 0 12
  | S O | S (S O) => in_range a 0 64 && Nat.eqb (length xs) (1+n) && forallb (fun v => in_range v (-1000000) 1000000) (skipn 1 xs)
  | S (S (S O)) => in_range a 0 6 && in_range b 0 6 && in_range c 0 6 && Nat.eqb (length xs) (3+n*m+m*z) &&
      forallb (fun v => in_range v (-1000) 1000) (skipn 3 xs)
  | S (S (S (S O))) => in_range a 0 64 && in_range b 0 32 && Nat.eqb (length xs) (2+n+m) &&
      forallb (fun v => in_range v 0 255) (skipn 2 xs)
  | _ => in_range a 0 64 && Nat.eqb (length xs) (1+2*n) && forallb (fun i =>
      let op := get xs (1+2*i) in let v := get xs (2+2*i) in in_range op 0 2 &&
      (if Z.eqb op 0 then in_range v (-1000000) 1000000 else Z.eqb v 0)) (seq 0 n)
  end.
Definition valid family xs : Prop := validb family xs = true.
Definition encode (xs : words) := xs ++ repeat 0%Z (8192-length xs).
