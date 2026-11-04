From Coq Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words:=list Z.
Definition get(xs:words)i:=nth i xs 0%Z.
Definition in_range v lo hi:=Z.leb lo v&&Z.leb v hi.
Definition validb family xs:=let a:=get xs 0 in let b:=get xs 1 in let n:=Z.to_nat a in let q:=Z.to_nat b in
 match family with
 | O=>in_range a 0 64&&Nat.eqb(length xs)(1+10*n)&&forallb(fun i=>let p:=1+10*i in let op:=get xs p in let len:=get xs(p+1)in
   in_range op 0 2&&in_range len 0 8&&(Z.eqb op 0||Z.eqb len 0)&&forallb(fun j=>if Nat.ltb j(Z.to_nat len)then in_range(get xs(p+2+j))0 255 else Z.eqb(get xs(p+2+j))0)(seq 0 8))(seq 0 n)
 | S O=>in_range a 0 64&&Nat.eqb(length xs)(1+3*n)&&forallb(fun i=>let op:=get xs(1+3*i)in let key:=get xs(2+3*i)in let v:=get xs(3+3*i)in
   in_range op 0 5&&(if Z.ltb op 3 then in_range key 0 7&&(if Z.eqb op 0 then in_range v(-1000)1000 else Z.eqb v 0)else Z.eqb key 0&&Z.eqb v 0))(seq 0 n)
 | _=>in_range a 0 8&&in_range b 0 64&&Nat.eqb(length xs)(2+3*q)&&forallb(fun i=>let op:=get xs(2+3*i)in let key:=get xs(3+3*i)in let v:=get xs(4+3*i)in
   in_range op 0 4&&in_range key 0(if Z.eqb op 4 then 8%Z else 15%Z)&&(if Z.eqb op 0 then in_range v(-1000)1000 else Z.eqb v 0))(seq 0 q)
 end.
Definition valid_familyb:=validb.
Definition valid family xs:Prop:=validb family xs=true.
Definition encode(xs:words):=xs++repeat 0%Z(8192-length xs).
