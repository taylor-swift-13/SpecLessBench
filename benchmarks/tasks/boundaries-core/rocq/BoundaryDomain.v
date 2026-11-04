From Coq Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words:=list Z.
Definition get(xs:words)i:=nth i xs 0%Z.
Definition in_range v lo hi:=Z.leb lo v&&Z.leb v hi.
Definition validb domain xs:=let a:=get xs 0 in let b:=get xs 1 in let n:=Z.to_nat a in let q:=Z.to_nat b in
  match domain with
  | O=>in_range a 0 64&&Nat.eqb(length xs)(1+3*n)&&forallb(fun i=>
      in_range(get xs(1+3*i))(-1000)1000&&forallb(fun c=>Z.eqb c(-1)||(Z.leb 0 c&&Z.ltb c(Z.of_nat i)))
      [get xs(2+3*i);get xs(3+3*i)])(seq 0 n)&&forallb(fun j=>Nat.leb(length(filter(fun k=>
      Z.eqb(get xs(2+3*(k/2)+k mod 2))(Z.of_nat j))(seq 0(2*n))))1)(seq 0 n)
  | S O=>in_range a 1 64&&in_range b 0 64&&Nat.eqb(length xs)(2+3*q)&&forallb(fun i=>
      in_range(get xs(2+3*i))0 1&&in_range(get xs(3+3*i))0(a-1)&&in_range(get xs(4+3*i))0(a-1))(seq 0 q)
  | S(S O)=>Z.eqb a 0&&in_range b 0 64&&Nat.eqb(length xs)(2+2*q)&&forallb(fun i=>
      let op:=get xs(2+2*i)in let v:=get xs(3+2*i)in in_range op 0 3&&
      (if Z.eqb op 0 then in_range v(-1000000)1000000 else Z.eqb v 0))(seq 0 q)
  | S(S(S O))=>Z.eqb a 1&&in_range b 0 64&&Nat.eqb(length xs)(2+q)&&forallb(fun v=>in_range v(-1000000)1000000)(skipn 2 xs)
  | S(S(S(S O)))=>in_range a 1 64&&in_range b 0 8&&Nat.eqb(length xs)(2+q+3*n)&&
      forallb(fun v=>in_range v(-1000)1000)(firstn q(skipn 2 xs))&&forallb(fun i=>
      let p:=2+q+3*i in let tag:=get xs p in let l:=get xs(p+1)in let r:=get xs(p+2)in
      in_range tag 0 255&&(if Z.eqb tag 0 then in_range l(-1000)1000&&Z.eqb r 0
      else if Z.eqb tag 1 then in_range l 0 15&&Z.eqb r 0
      else if Z.gtb tag 10 then in_range l(-1000)1000&&in_range r(-1000)1000
      else Z.leb 0 l&&Z.ltb l(Z.of_nat i)&&(if Z.eqb tag 8||Z.eqb tag 9 then Z.eqb r 0 else Z.leb 0 r&&Z.ltb r(Z.of_nat i))))(seq 0 n)
  | S(S(S(S(S O))))=>in_range a 0 96&&Nat.eqb(length xs)(1+n)&&forallb(fun v=>in_range v 0 255)(skipn 1 xs)
  | S(S(S(S(S(S(S O))))))=>in_range a 0 64&&in_range b 0 96&&Nat.eqb(length xs)(2+n)&&forallb(fun v=>in_range v 0 255)(skipn 2 xs)
  | _=>in_range a 0 64&&Nat.eqb(length xs)(1+n)&&forallb(fun v=>in_range v 0 255)(skipn 1 xs)
  end.
Definition family_domain family xs:=if Nat.ltb family 2 then family else if Nat.eqb family 2 then(if Z.eqb(get xs 0)0 then 2 else 3)else family+1.
Definition valid_familyb family xs:=validb(family_domain family xs)xs.
Definition valid domain xs:Prop:=validb domain xs=true.
Definition encode(xs:words):=xs++repeat 0%Z(8192-length xs).
