From Stdlib Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words := list Z.
Definition get (xs : words) i := nth i xs 0%Z.
Definition valid_familyb (_family:nat) xs :=
 let n:=get xs 0 in Z.leb 0 n && Z.leb n 64 &&
 Nat.eqb (length xs) (1+Z.to_nat n) &&
 forallb (fun b=>Z.leb 0 b && Z.leb b 255) (skipn 1 xs).
Definition valid family xs : Prop := valid_familyb family xs=true.
Definition encode (xs:words) := xs++repeat 0%Z (8192-length xs).
