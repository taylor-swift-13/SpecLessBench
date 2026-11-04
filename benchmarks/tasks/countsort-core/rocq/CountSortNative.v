From Coq Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words:=list Z.
Definition word(xs:words)i:=nth i xs 0%Z.
Definition put {A}(xs:list A)i(v:A):=firstn i xs++[v]++skipn(S i)xs.
Definition finish(xs:words):=Some(Z.of_nat(length xs)::xs).
Definition record:=(Z*Z)%type.
Fixpoint insert_record(item:record)(items:list record):list record:=match items with
| []=>[item]|x::xs=>if Z.ltb(fst item)(fst x)then item::x::xs else x::insert_record item xs end.
Definition index(x:record):=Z.to_nat(fst x+3).
Definition counting(xs:list record)(reverse:bool):list record:=
 let counts:=fold_left(fun counts x=>let k:=index x in put counts k (S(nth k counts 0)))xs(repeat 0 7)in
 let positions:=map(fun k=>fold_left Nat.add(firstn k counts)0)(seq 0 7)in
 let '(out,_):=fold_left(fun state x=>let '(out,pos):=state in let k:=index x in let slot:=nth k pos 0 in
   (put out slot x,put pos k (S slot)))(if reverse then rev xs else xs)(repeat(0%Z,0%Z)(length xs),positions)in out.
Definition entry (_family style:nat)(xs:words):option words:=
 let n:=Z.to_nat(word xs 0)in let items:=map(fun i=>(word xs(1+2*i),word xs(2+2*i)))(seq 0 n)in
 let result:=if Nat.eqb style 0 then fold_left(fun acc x=>insert_record x acc)items[] else counting items(Nat.eqb style 2)in
 finish(flat_map(fun kv=>[fst kv;snd kv])result).
Definition Equivalent(valid:words->Prop)(a b:words->option words):=forall x,valid x->exists o,a x=Some o/\b x=Some o.
Definition RefutationAt(valid:words->Prop)(a b:words->option words)(x oa ob:words):=valid x/\a x=Some oa/\b x=Some ob/\oa<>ob.
