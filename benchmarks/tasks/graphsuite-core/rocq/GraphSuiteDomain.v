From Coq Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words:=list Z.
Definition word(xs:words)i:=nth i xs 0%Z.
Definition between x lo hi:=Z.leb lo x&&Z.leb x hi.
Definition validb domain xs:=
 if Nat.eqb domain 0||Nat.eqb domain 1 then
 let n:=word xs 0 in let k:=Z.to_nat n in
 between n 1 8&&Nat.eqb(length xs)(1+k*k)&&forallb(fun p=>
   let v:=word xs(1+p)in if Nat.eqb domain 1 then between v 0 1
   else if Nat.eqb(p/k)(p mod k)then Z.eqb v (-1)else between v (-1)100)(seq 0(k*k))
 else if Nat.eqb domain 2 then let n:=word xs 0 in let m:=word xs 1 in
 between n 0 48&&between m 0 16&&Nat.eqb(length xs)(2+Z.to_nat n+Z.to_nat m)&&
 forallb(fun i=>between(word xs(2+i))0 3)(seq 0(Z.to_nat n+Z.to_nat m))
 else false.
Definition valid_familyb family xs:=validb family xs.
Definition valid domain xs:Prop:=validb domain xs=true.
Definition encode(xs:words):=xs++repeat 0%Z(8192-length xs).
