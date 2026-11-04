From Coq Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words:=list Z.
Definition word(xs:words)i:=nth i xs 0%Z.
Definition between x lo hi:=Z.leb lo x&&Z.leb x hi.
Definition validb domain xs:=
 if Nat.eqb domain 2 then let n:=word xs 0 in between n 0 64&&Nat.eqb(length xs)(1+2*Z.to_nat n)&&
   forallb(fun i=>between(word xs(1+2*i))(-1000)1000&&between(word xs(2+2*i))(-1000)1000)(seq 0(Z.to_nat n))
 else let mode:=word xs 0 in let n:=word xs 1 in let m:=word xs 2 in
   Z.eqb mode(Z.of_nat domain)&&between n 1 8&&between m 0 28&&Nat.eqb(length xs)(3+3*Z.to_nat m)&&
   forallb(fun i=>let u:=word xs(3+3*i)in let v:=word xs(4+3*i)in let w:=word xs(5+3*i)in
     Z.leb 0 u&&Z.ltb u v&&Z.ltb v n&&between w(-1000)1000&&forallb(fun j=>
       (negb(Z.eqb u(word xs(3+3*j)))||negb(Z.eqb v(word xs(4+3*j))))&&
       (negb(Nat.eqb domain 1)||negb(Z.eqb w(word xs(5+3*j)))))(seq 0 i))(seq 0(Z.to_nat m)).
Definition valid_familyb family xs:=if Nat.eqb family 0 then validb(Z.to_nat(word xs 0))xs else validb 2 xs.
Definition valid domain xs:Prop:=validb domain xs=true.
Definition encode(xs:words):=xs++repeat 0%Z(8192-length xs).
