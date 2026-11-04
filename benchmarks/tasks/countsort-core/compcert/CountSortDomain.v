From Stdlib Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words:=list Z.
Definition word(xs:words)i:=nth i xs 0%Z.
Definition between x lo hi:=Z.leb lo x&&Z.leb x hi.
Definition validb domain xs:=let n:=word xs 0 in Nat.eqb domain 0&&between n 0 64&&
 Nat.eqb(length xs)(1+2*Z.to_nat n)&&forallb(fun i=>between(word xs(1+2*i))(-3)3&&between(word xs(2+2*i))(-1000)1000)(seq 0(Z.to_nat n)).
Definition valid_familyb family xs:=validb family xs.
Definition valid domain xs:Prop:=validb domain xs=true.
Definition encode(xs:words):=xs++repeat 0%Z(8192-length xs).
