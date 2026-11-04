From Coq Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words:=list Z.
Definition word(xs:words)i:=nth i xs 0%Z.
Definition put {A}(xs:list A)i(v:A):=firstn i xs++[v]++skipn(S i)xs.
Definition finish(xs:words):=Some(Z.of_nat(length xs)::xs).
Definition obind {A B}(x:option A)(f:A->option B):=match x with Some a=>f a|None=>None end.
Notation "'let*' x ':=' c 'in' b" := (obind c (fun x=>b)) (at level 200,x ident,c at level 100,b at level 200).
Definition lim:=1000000%Z.
Definition init_dist n xs:=map(fun p=>let v:=word xs(1+p)in if Nat.eqb(p/n)(p mod n)then 0%Z else if Z.ltb v 0 then lim else v)(seq 0(n*n)).
Definition floyd n xs:=fold_left(fun d k=>fold_left(fun d i=>fold_left(fun d j=>
 let x:=word d(i*n+k)in let y:=word d(k*n+j)in let z:=word d(i*n+j)in
 if negb(Z.eqb x lim)&&negb(Z.eqb y lim)&&Z.ltb(x+y)z then put d(i*n+j)(x+y)%Z else d)(seq 0 n)d)(seq 0 n)d)(seq 0 n)(init_dist n xs).
Definition dijkstra_one n xs mutant source:=
 let start:=put(repeat lim n)source 0%Z in
 let '(d,_):=fold_left(fun state _=>let '(d,seen):=state in
   let best:=fold_left(fun best j=>if nth j seen false||Z.eqb(word d j)lim then best else
     match best with None=>Some j|Some b=>if Z.ltb(word d j)(word d b)then Some j else best end)(seq 0 n)(@None nat)in
   match best with None=>(d,seen)|Some u=>
     let d:=fold_left(fun d j=>let w:=word xs(1+u*n+j)in
       if Z.leb 0 w&&negb(mutant&&Z.eqb w 0)&&Z.ltb(word d u+w)(word d j)
       then put d j(word d u+w)%Z else d)(seq 0 n)d in (d,put seen u true)end)
   (seq 0 n)(start,repeat false n)in d.
Definition apsp style xs:=let n:=Z.to_nat(word xs 0)in
 let d:=if Nat.eqb style 0 then floyd n xs else flat_map(dijkstra_one n xs(Nat.eqb style 2))(seq 0 n)in
 finish(map(fun v=>if Z.eqb v lim then (-1)%Z else v)d).

(* Mutable state is encoded as a bounded word vector: idx, low, onstack,
   component, stack, top, clock, component count. *)
Definition gs s off i:=word s(off+i).
Definition ss (s:words) off i (v:Z):=put s(off+i)v.
Fixpoint pop_tarjan fuel n v (s:words):option words:=match fuel with
| O=>None | S fuel=>
 let top:=Z.to_nat(gs s (5*n) 0)in
 match top with O=>None|S t=>
 let x:=Z.to_nat(gs s (4*n) t)in
 let s:=ss s (5*n) 0 (Z.of_nat t)in
 let s:=ss (ss s (2*n) x 0%Z) (3*n) x (gs s (5*n+2) 0)in
 if Nat.eqb x v then Some(ss s (5*n+2) 0 (gs s (5*n+2) 0+1)%Z)
 else pop_tarjan fuel n v s end end.
Fixpoint tarjan_visit fuel n xs v (s:words):option words:=match fuel with
| O=>None|S fuel=>
 let clk:=gs s (5*n+1) 0 in let top:=Z.to_nat(gs s (5*n) 0)in
 let s:=ss (ss s 0 v clk) n v clk in
 let s:=ss (ss s (4*n) top (Z.of_nat v)) (2*n) v 1%Z in
 let s:=ss (ss s (5*n) 0 (Z.of_nat(S top))) (5*n+1) 0 (clk+1)%Z in
 let* s:=fold_left(fun state w=>let* s:=state in
   if Z.eqb(word xs(1+v*n+w))0 then Some s else
   if Z.ltb(gs s 0 w)0 then let* s:=tarjan_visit fuel n xs w s in
      Some(ss s n v (Z.min(gs s n v)(gs s n w)))
   else if Z.eqb(gs s (2*n) w)1 then Some(ss s n v (Z.min(gs s n v)(gs s 0 w)))
   else Some s)(seq 0 n)(Some s)in
 if Z.eqb(gs s n v)(gs s 0 v)then pop_tarjan 9 n v s else Some s end.
Definition tarjan n xs:option words:=
 let initial:=repeat (-1)%Z n++repeat 0%Z (4*n+3)in
 let* state:=fold_left(fun state v=>let* s:=state in if Z.ltb(gs s 0 v)0 then tarjan_visit 9 n xs v s else Some s)(seq 0 n)(Some initial)in
 Some(firstn n(skipn(3*n)state)).
Fixpoint first_visit fuel n xs v (seen:list bool)(order:list nat):option(list bool*list nat):=match fuel with
| O=>None|S fuel=>
 let* state:=fold_left(fun state w=>let* state:=state in let '(seen,order):=state in
   if negb(Z.eqb(word xs(1+v*n+w))0)&&negb(nth w seen false)
   then first_visit fuel n xs w seen order else Some(seen,order))
   (seq 0 n)(Some(put seen v true,order))in
 let '(seen,order):=state in Some(seen,v::order)end.
Fixpoint second_visit fuel n xs (mutant:bool) v c (comp:words):option words:=match fuel with
| O=>None|S fuel=>fold_left(fun state w=>let* comp:=state in
 let p:=if mutant then v*n+w else w*n+v in
 if negb(Z.eqb(word xs(1+p))0)&&Z.ltb(word comp w)0 then second_visit fuel n xs mutant w c comp else Some comp)
 (seq 0 n)(Some(put comp v c))end.
Definition kosaraju n xs mutant:option words:=
 let* first:=fold_left(fun state v=>let* state:=state in let '(seen,order):=state in
 if nth v seen false then Some(seen,order)else first_visit 9 n xs v seen order)(seq 0 n)(Some(repeat false n,[]))in
 let '(_,order):=first in
 let* result:=fold_left(fun state v=>let* state:=state in let '(comp,c):=state in
 if Z.leb 0(word comp v)then Some(comp,c)else let* comp:=second_visit 9 n xs mutant v c comp in Some(comp,(c+1)%Z))
 order(Some(repeat (-1)%Z n,0%Z))in let '(comp,_):=result in Some comp.
Definition scc style xs:=let n:=Z.to_nat(word xs 0)in
 let* comp:=if Nat.eqb style 0 then tarjan n xs else kosaraju n xs(Nat.eqb style 2)in
 finish(flat_map(fun i=>map(fun j=>if Z.eqb(word comp i)(word comp j)then 1%Z else 0%Z)(seq 0 n))(seq 0 n)).

Definition brute text pattern:=
 if Nat.ltb(length text)(length pattern)then (-1)%Z else
 fold_left(fun result i=>if Z.eqb result (-1)&&if list_eq_dec Z.eq_dec(firstn(length pattern)(skipn i text))pattern then true else false
 then Z.of_nat i else result)(seq 0(S(length text-length pattern)))(-1)%Z.
Fixpoint bm_loop fuel i text pattern (mutant:bool):Z:=match fuel with O=>(-1)%Z|S fuel=>
 if Nat.ltb(length text)(i+length pattern)then (-1)%Z else
 match find(fun j=>negb(Z.eqb(word text(i+j))(word pattern j)))(rev(seq 0(length pattern)))with
 | None=>Z.of_nat i|Some j=>
   let right:=fold_left(fun r k=>if Z.eqb(word pattern k)(word text(i+j))then Z.of_nat k else r)(seq 0(length pattern))(-1)%Z in
   let skip:=if mutant then length pattern else Z.to_nat(Z.max 1 (Z.of_nat j-right))in
   bm_loop fuel (i+skip) text pattern mutant end end.
Definition search style xs:=let n:=Z.to_nat(word xs 0)in let m:=Z.to_nat(word xs 1)in
 let text:=firstn n(skipn 2 xs)in let pattern:=firstn m(skipn(2+n)xs)in
 finish[if Nat.eqb style 0 then brute text pattern else if Nat.eqb m 0 then 0%Z else bm_loop 49 0 text pattern(Nat.eqb style 2)].
Definition entry family style xs:=if Nat.eqb family 0 then apsp style xs else if Nat.eqb family 1 then scc style xs else search style xs.
Definition Equivalent(valid:words->Prop)(a b:words->option words):=forall x,valid x->exists o,a x=Some o/\b x=Some o.
Definition RefutationAt(valid:words->Prop)(a b:words->option words)(x oa ob:words):=valid x/\a x=Some oa/\b x=Some ob/\oa<>ob.
