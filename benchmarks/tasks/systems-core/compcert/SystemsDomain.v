From Stdlib Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.

Definition words := list Z.
Definition word (xs : words) i := nth i xs 0%Z.
Definition between x lo hi := Z.leb lo x && Z.leb x hi.
Definition valid_command family op a b c :=
  match family with
  | O => between op 0 4 && between a 0 7 && Z.eqb c 0 &&
    (if Z.leb op 1 then between b 0 7 else Z.eqb b 0)
  | S O => between op 0 4 && Z.eqb c 0 &&
    (if Z.leb op 2 then between a 0 7 else Z.eqb a 0) &&
    (if Z.eqb op 0 then between b (-1000) 1000 else Z.eqb b 0)
  | _ => between op 0 3 && between a 0 (if Z.eqb op 3 then 4%Z else 7%Z) &&
    (if Z.eqb op 0 then between b (-1000) 1000 && between c 1 8 else Z.eqb b 0 && Z.eqb c 0)
  end.
Definition valid_familyb family xs :=
  let q := word xs 0 in
  if Nat.eqb family 3 then
    let m := word xs 1 in
    between q 0 12 && between m 0 12 && between (word xs 2) 0 12 &&
    between (word xs 3) 1 10 && between (word xs 4) 0 (word xs 3) &&
    between (word xs 5) 0 10 && Nat.eqb (length xs) (6+Z.to_nat q+Z.to_nat m) &&
    forallb (fun x => between x 0 4) (skipn 6 xs)
  else if Nat.eqb family 4 then
    between q 1 16 && between (word xs 1) 0 32 && between (word xs 2) (-24) 24 &&
    between (word xs 3) 1 16 && between (word xs 4) (-64) 128 &&
    between (word xs 5) (-512) (word xs 6) && between (word xs 6) (word xs 5) 512 &&
    Nat.eqb (length xs) (7+Z.to_nat q) && forallb (fun x => between x (-512) 512) (skipn 7 xs)
  else
    between q 0 64 && Nat.eqb (length xs) (1+4*Z.to_nat q) &&
    forallb (fun i =>
      let p := 1+4*i in
      valid_command family (word xs p) (word xs (p+1)) (word xs (p+2)) (word xs (p+3)))
      (seq 0 (Z.to_nat q)).
Definition valid family xs : Prop := valid_familyb family xs = true.
Definition encode (xs : words) := xs ++ repeat 0%Z (8192-length xs).
