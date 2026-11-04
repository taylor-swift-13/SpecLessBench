From Coq Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words:=list Z.
Definition iz (xs:words) i:=nth i xs 0%Z.
Definition put {A}(xs:list A)i(v:A):=firstn i xs++[v]++skipn(S i)xs.
Definition finish(xs:words):=Z.of_nat(length xs)::xs.
Definition obind {A B}(x:option A)(f:A->option B):=match x with Some a=>f a|None=>None end.
Notation "'let*' x ':=' c 'in' b" := (obind c (fun x=>b)) (at level 200,x ident,c at level 100,b at level 200).
Definition node:=(Z*Z*Z)%type.
Definition node_at(ns:list node)i:=nth i ns (0%Z,(-1)%Z,(-1)%Z).
Fixpoint mirror_rec(mutant:bool)fuel(ns:list node)id:option(list node):=
  if Z.ltb id 0 then Some ns else match fuel with O=>None|S f=>
    let '(v,l,r):=node_at ns (Z.to_nat id) in
    let* first:=mirror_rec mutant f (put ns (Z.to_nat id)(v,r,l))r in
    if mutant then Some first else mirror_rec mutant f first l end.
Fixpoint mirror_stack fuel(ns:list node)todo:=match todo,fuel with
| [],_=>Some ns|_,O=>None|id::rest,S f=>if Z.ltb id 0 then mirror_stack f ns rest else
  let '(v,l,r):=node_at ns (Z.to_nat id) in mirror_stack f (put ns (Z.to_nat id)(v,r,l))(l::r::rest)end.
Fixpoint project_tree fuel(ns:list node)id:option(nat*words):=
  if Z.ltb id 0 then Some(0,[(-1)%Z])else match fuel with O=>None|S f=>
    let '(v,l,r):=node_at ns(Z.to_nat id)in
    let* left:=project_tree f ns l in let* right:=project_tree f ns r in
    Some(Nat.max(fst left)(fst right)+1,[id;v]++snd left++snd right)end.
Definition tree style xs:=let n:=Z.to_nat(iz xs 0)in
  let ns:=map(fun i=>(iz xs(1+3*i),iz xs(2+3*i),iz xs(3+3*i)))(seq 0 n)in
  let root:=(Z.of_nat n-1)%Z in
  let* result:=if Nat.eqb style 1 then mirror_stack 256 ns[root]else mirror_rec(Nat.eqb style 2)64 ns root in
  let* projection:=project_tree 64 result root in Some(finish(Z.of_nat(fst projection)::snd projection)).

Fixpoint find_uf style fuel(p:words)x:option(nat*words):=match fuel with O=>None|S f=>
  let parent:=Z.to_nat(iz p x)in if Nat.eqb style 2 then Some(parent,p)
  else if Nat.eqb parent x then Some(x,p)
  else if Nat.eqb style 1 then let grand:=Z.to_nat(iz p parent)in find_uf style f(put p x(Z.of_nat grand))grand
  else let* result:=find_uf style f p parent in Some(fst result,put(snd result)x(Z.of_nat(fst result)))end.
Definition unionfind style xs:=let n:=Z.to_nat(iz xs 0)in let q:=Z.to_nat(iz xs 1)in
  let* state:=fold_left(fun state i=>let* s:=state in let '(p,r,out):=s in
    let op:=iz xs(2+3*i)in let a:=Z.to_nat(iz xs(3+3*i))in let b:=Z.to_nat(iz xs(4+3*i))in
    let* first:=find_uf style 128 p a in let* second:=find_uf style 128(snd first)b in
    let x:=fst first in let y:=fst second in let p':=snd second in
    if Z.eqb op 1 then Some(p',r,out++[1%Z;if Nat.eqb x y then 1%Z else 0%Z])
    else if Nat.eqb x y then Some(p',r,out++[0%Z;0%Z])
    else if Z.gtb(iz r x)(iz r y)then Some(put p' y(Z.of_nat x),r,out++[0%Z;0%Z])
    else Some(put p' x(Z.of_nat y),if Z.eqb(iz r x)(iz r y)then put r y(iz r y+1)%Z else r,out++[0%Z;0%Z]))
    (seq 0 q)(Some(map Z.of_nat(seq 0 n),repeat 0%Z n,([]:words)))in
  let '(_,_,out):=state in Some(finish out).
Fixpoint sorted_push v(q:words):=match q with []=>[v]|x::xs=>if Z.gtb v x then v::x::xs else x::sorted_push v xs end.
Fixpoint sift_up fuel(q:words)i:=match fuel with O=>None|S f=>if Nat.eqb i 0 then Some q else
  let p:=(i-1)/2 in if Z.geb(iz q p)(iz q i)then Some q else sift_up f(put(put q p(iz q i))i(iz q p))p end.
Fixpoint sift_down(mutant:bool)fuel(q:words)i:=match fuel with O=>None|S f=>
  let l:=2*i+1 in if Nat.leb(length q)l then Some q else
  let c:=if negb mutant&&Nat.ltb(l+1)(length q)&&Z.gtb(iz q(l+1))(iz q l)then l+1 else l in
  if Z.geb(iz q i)(iz q c)then Some q else sift_down mutant f(put(put q i(iz q c))c(iz q i))c end.
Definition pq_push style q v:=if Nat.eqb style 1 then Some(sorted_push v q)else sift_up 64(q++[v])(length q).
Definition pq_pop style q:=if Nat.leb(length q)1 then Some(iz q 0,([]:words))
  else if Nat.eqb style 1 then Some(iz q 0,skipn 1 q)
  else let* next:=sift_down(Nat.eqb style 2)64(put(firstn(length q-1)q)0(iz q(length q-1)))0 in Some(iz q 0,next).
Fixpoint pq_drain style fuel q out:=match q,fuel with [],_=>Some out|_,O=>None|_,S f=>
  let* result:=pq_pop style q in pq_drain style f(snd result)(out++[fst result])end.
Definition priority style xs:=let n:=Z.to_nat(iz xs 1)in
  if Z.eqb(iz xs 0)1 then let* q:=fold_left(fun state i=>let* q:=state in pq_push style q(iz xs(2+i)))(seq 0 n)(Some[])in
    let* out:=pq_drain style 65 q[]in Some(finish out)
  else let* result:=fold_left(fun state i=>let* s:=state in let '(q,out):=s in
    let op:=iz xs(2+2*i)in let v:=iz xs(3+2*i)in
    if Z.eqb op 0 then let* next:=pq_push style q v in Some(next,out++[0%Z;0%Z])
    else if Z.eqb op 3 then Some(q,out++[3%Z;if Nat.eqb(length q)0 then 1%Z else 0%Z])
    else if Nat.eqb(length q)0 then Some(q,out++[op;0%Z;0%Z])
    else if Z.eqb op 2 then Some(q,out++[2%Z;1%Z;iz q 0])
    else let* next:=pq_pop style q in Some(snd next,out++[1%Z;1%Z;fst next]))(seq 0 n)(Some(([]:words),([]:words)))in
    Some(finish(snd result)).

Record result:={rc:Z;re:Z;rv:Z}.
Definition missing:result:={|rc:=(-1)%Z;re:=(-1)%Z;rv:=0%Z|}.
Definition ok v:result:={|rc:=0%Z;re:=(-1)%Z;rv:=v|}.
Definition failure c i:result:={|rc:=c;re:=Z.of_nat i;rv:=0%Z|}.
Definition expr xs i:node:=let p:=2+Z.to_nat(iz xs 1)+3*i in(iz xs p,iz xs(p+1),iz xs(p+2)).
Definition leaf xs i:=let '(tag,a,_):=expr xs i in
  if Z.eqb tag 0 then Some(ok a)else if Z.eqb tag 1 then Some(if Z.geb a(iz xs 1)then failure 1%Z i else ok(iz xs(2+Z.to_nat a)))
  else if Z.gtb tag 10 then Some(failure 4%Z i)else None.
Definition combine(mutant:bool)xs i(cache:list result):result:=let '(tag,a,b):=expr xs i in
  let l:=nth(Z.to_nat a)cache missing in let r:=nth(Z.to_nat b)cache missing in
  if negb(Z.eqb l.(rc)0)then l
  else if mutant&&(Z.eqb tag 6||Z.eqb tag 7)&&negb(Z.eqb r.(rc)0)then r
  else if Z.eqb tag 6&&Z.eqb l.(rv)0 then ok 0%Z
  else if Z.eqb tag 7&&negb(Z.eqb l.(rv)0)then ok 1%Z
  else if negb(Z.eqb tag 8)&&negb(Z.eqb tag 9)&&negb(Z.eqb r.(rc)0)then r
  else if Z.eqb tag 10&&Z.eqb r.(rv)0 then failure 3%Z i
  else let v:=if Z.eqb tag 2 then(l.(rv)+r.(rv))%Z else if Z.eqb tag 3 then(l.(rv)-r.(rv))%Z
    else if Z.eqb tag 4 then(if Z.ltb l.(rv)r.(rv)then 1%Z else 0%Z)
    else if Z.eqb tag 5 then(if Z.eqb l.(rv)r.(rv)then 1%Z else 0%Z)
    else if Z.eqb tag 6 then(if negb(Z.eqb l.(rv)0)&&negb(Z.eqb r.(rv)0)then 1%Z else 0%Z)
    else if Z.eqb tag 7 then(if negb(Z.eqb l.(rv)0)||negb(Z.eqb r.(rv)0)then 1%Z else 0%Z)
    else if Z.eqb tag 8 then(-l.(rv))%Z else if Z.eqb tag 9 then(if Z.eqb l.(rv)0 then 1%Z else 0%Z)
    else Z.quot l.(rv)r.(rv)in if Z.ltb v(-32768)||Z.gtb v 32767 then failure 2%Z i else ok v.
Fixpoint eval_rec xs fuel i(cache:list result):option(list result):=
  if Z.geb(nth i cache missing).(rc)0 then Some cache else match fuel with O=>None|S f=>
    match leaf xs i with Some value=>Some(put cache i value)|None=>
      let '(tag,a,b):=expr xs i in let* first:=eval_rec xs f(Z.to_nat a)cache in
      let l:=nth(Z.to_nat a)first missing in
      let skip:=negb(Z.eqb l.(rc)0)||Z.eqb tag 8||Z.eqb tag 9||(Z.eqb tag 6&&Z.eqb l.(rv)0)||(Z.eqb tag 7&&negb(Z.eqb l.(rv)0))in
      let* second:=if skip then Some first else eval_rec xs f(Z.to_nat b)first in Some(put second i(combine false xs i second))end end.
Definition evaluator style xs:=let n:=Z.to_nat(iz xs 0)in let initial:=repeat missing n in
  let* cache:=if Nat.eqb style 0 then eval_rec xs 64(n-1)initial
    else Some(fold_left(fun cache i=>put cache i(match leaf xs i with Some v=>v|None=>combine(Nat.eqb style 2)xs i cache end))(seq 0 n)initial)in
  let value:=nth(n-1)cache missing in Some(finish[value.(rc);value.(re);value.(rv)]).

Definition parse_error:=(Z*nat)%type.
Definition xor_bytes(xs:words):=fold_left Z.lxor xs 0%Z.
Definition tlv_record(mutant:bool)(src:words)start:sum parse_error(nat*words):=
  if Nat.ltb(length src)3 then inl(1%Z,start)else
  let tag:=iz src 0 in let len:=Z.to_nat(iz src 1+256*iz src 2)%Z in
  if Z.ltb tag 1||Z.gtb tag 3 then inl(2%Z,start)
  else if Nat.ltb 32 len then inl(3%Z,start)
  else if Nat.ltb(length src)(len+4)then inl(4%Z,start)
  else if(Z.eqb tag 1&&negb(Nat.eqb len 2))||(Z.eqb tag 3&&negb(Nat.eqb len 1))then inl(5%Z,start)
  else if negb(Z.eqb(xor_bytes(firstn(3+len)src))(iz src(3+len)))then inl(7%Z,start+3+len)
  else if Z.eqb tag 3&&Z.gtb(iz src 3)1 then inl(6%Z,start+3)
  else let out:=if Z.eqb tag 1 then[tag;if mutant then(256*iz src 3+iz src 4)%Z else(iz src 3+256*iz src 4)%Z]
    else if Z.eqb tag 3 then[tag;iz src 3]else[tag;Z.of_nat len]++firstn len(skipn 3 src)in inr(len+4,out).
Fixpoint tlv_suffix mutant fuel src p count out:=
  if Nat.eqb(length src)0 then Some(finish([0%Z;Z.of_nat p;Z.of_nat count]++out))else match fuel with
  | O=>None|S f=>match tlv_record mutant src p with
    | inl(code,offset)=>Some(finish([code;Z.of_nat offset;Z.of_nat count]++out))
    | inr(used,bytes)=>tlv_suffix mutant f(skipn used src)(p+used)(count+1)(out++bytes)end end.
Fixpoint tlv_indexed mutant(data:words)fuel p count out:=
  if Nat.eqb p(length data)then Some(finish([0%Z;Z.of_nat p;Z.of_nat count]++out))else match fuel with
  | O=>None|S f=>match tlv_record mutant(skipn p data)p with
    | inl(code,offset)=>Some(finish([code;Z.of_nat offset;Z.of_nat count]++out))
    | inr(used,bytes)=>tlv_indexed mutant data f(p+used)(count+1)(out++bytes)end end.
Definition tlv style xs:=let data:=firstn(Z.to_nat(iz xs 0))(skipn 1 xs)in
  if Nat.eqb style 1 then tlv_suffix false 128 data 0 0[]else tlv_indexed(Nat.eqb style 2)data 128 0 0[].

Record quote_state:={qm:nat;qo:nat;qe:bool;qs:nat;qa:bool;qc:words;qt:list words;qcode:Z;qoffset:nat}.
Definition quote_initial:quote_state:={|qm:=0;qo:=0;qe:=false;qs:=0;qa:=false;qc:=[];qt:=[];qcode:=0%Z;qoffset:=0|}.
Definition qmake (s:quote_state) m o e slash active cur tokens code offset:quote_state:=
 {|qm:=m;qo:=o;qe:=e;qs:=slash;qa:=active;qc:=cur;qt:=tokens;qcode:=code;qoffset:=offset|}.
Definition qadd s c:=qmake s s.(qm)s.(qo)s.(qe)s.(qs)true(s.(qc)++[c])s.(qt)s.(qcode)s.(qoffset).
Definition qcommit s:=qmake s s.(qm)s.(qo)s.(qe)s.(qs)false[](if s.(qa)then s.(qt)++[s.(qc)]else s.(qt))s.(qcode)s.(qoffset).
Definition quote_step(mutant:bool)s c p:=
  if negb(Z.eqb s.(qcode)0)then s
  else if Z.eqb c 0 then qmake s s.(qm)s.(qo)s.(qe)s.(qs)s.(qa)s.(qc)s.(qt)3%Z p
  else if s.(qe)then qmake s s.(qm)s.(qo)false s.(qs)true(s.(qc)++[c])s.(qt)0%Z s.(qoffset)
  else if Nat.eqb s.(qm)1 then if Z.eqb c 39 then qmake s 0 s.(qo)s.(qe)s.(qs)s.(qa)s.(qc)s.(qt)0%Z s.(qoffset)else qadd s c
  else if Z.eqb c 92 then qmake s s.(qm)s.(qo)true p s.(qa)s.(qc)s.(qt)0%Z s.(qoffset)
  else if Nat.eqb s.(qm)2 then if Z.eqb c 34 then qmake s 0 s.(qo)s.(qe)s.(qs)s.(qa)s.(qc)s.(qt)0%Z s.(qoffset)else qadd s c
  else if Z.eqb c 9||Z.eqb c 32 then qcommit s
  else if Z.eqb c 39||Z.eqb c 34 then qmake s(if Z.eqb c 39 then 1 else 2)p s.(qe)s.(qs)(if mutant then s.(qa)else true)s.(qc)s.(qt)0%Z s.(qoffset)
  else qadd s c.
Definition ordinary c:=negb(Z.eqb c 0)&&negb(Z.eqb c 9)&&negb(Z.eqb c 32)&&negb(Z.eqb c 34)&&negb(Z.eqb c 39)&&negb(Z.eqb c 92).
Fixpoint take_ordinary(src:words):=match src with []=>[]|c::rest=>if ordinary c then c::take_ordinary rest else[]end.
Fixpoint quote_spans fuel src p s:=match src,fuel with [],_=>Some s|_,O=>None|_,S f=>
  if negb(Z.eqb s.(qcode)0)then Some s else
  if Nat.eqb s.(qm)0&&negb s.(qe)&&ordinary(iz src 0)then let span:=take_ordinary src in
    quote_spans f(skipn(length span)src)(p+length span)(qmake s s.(qm)s.(qo)s.(qe)s.(qs)true(s.(qc)++span)s.(qt)0%Z s.(qoffset))
  else quote_spans f(skipn 1 src)(p+1)(quote_step false s(iz src 0)p)end.
Definition quotes style xs:=let data:=firstn(Z.to_nat(iz xs 0))(skipn 1 xs)in
  let* s:=if Nat.eqb style 1 then quote_spans 128 data 0 quote_initial
    else Some(fold_left(fun s cp=>quote_step(Nat.eqb style 2)s(snd cp)(fst cp))(List.combine(seq 0(length data))data)quote_initial)in
  let final:=if negb(Z.eqb s.(qcode)0)then s else if s.(qe)then
    qmake s s.(qm)s.(qo)s.(qe)s.(qs)s.(qa)s.(qc)s.(qt)1%Z s.(qs)
    else if negb(Nat.eqb s.(qm)0)then qmake s s.(qm)s.(qo)s.(qe)s.(qs)s.(qa)s.(qc)s.(qt)2%Z s.(qo)
    else let committed:=qcommit s in qmake committed committed.(qm)committed.(qo)committed.(qe)committed.(qs)committed.(qa)committed.(qc)committed.(qt)0%Z(length data)in
  Some(finish([final.(qcode);Z.of_nat final.(qoffset);Z.of_nat(length final.(qt))]++flat_map(fun token=>Z.of_nat(length token)::token)final.(qt))).

Definition pack_block(mutant:bool)(src:words)start cap produced:sum parse_error(nat*words):=
  let control:=Z.to_nat(iz src 0)in if Nat.eqb control 128 then inr(1,[])else
  let count:=if Nat.ltb control 128 then control+1 else 257-control-(if mutant then 1 else 0)in
  let used:=if Nat.ltb control 128 then count+1 else 2 in
  if Nat.ltb(length src)used then inl(1%Z,start)
  else if Nat.ltb cap(produced+count)then inl(2%Z,start)
  else inr(used,if Nat.ltb control 128 then firstn count(skipn 1 src)else repeat(iz src 1)count).
Fixpoint pack_suffix mutant cap fuel src p out:=
  if Nat.eqb(length src)0 then Some(finish([0%Z;Z.of_nat p;Z.of_nat(length out)]++out))else match fuel with
  | O=>None|S f=>match pack_block mutant src p cap(length out)with
    | inl(code,offset)=>Some(finish([code;Z.of_nat offset;Z.of_nat(length out)]++out))
    | inr(used,bytes)=>pack_suffix mutant cap f(skipn used src)(p+used)(out++bytes)end end.
Fixpoint pack_indexed mutant cap(data:words)fuel p out:=
  if Nat.eqb p(length data)then Some(finish([0%Z;Z.of_nat p;Z.of_nat(length out)]++out))else match fuel with
  | O=>None|S f=>match pack_block mutant(skipn p data)p cap(length out)with
    | inl(code,offset)=>Some(finish([code;Z.of_nat offset;Z.of_nat(length out)]++out))
    | inr(used,bytes)=>pack_indexed mutant cap data f(p+used)(out++bytes)end end.
Definition packbits style xs:=let data:=firstn(Z.to_nat(iz xs 0))(skipn 2 xs)in let cap:=Z.to_nat(iz xs 1)in
  if Nat.eqb style 1 then pack_suffix false cap 128 data 0[]else pack_indexed(Nat.eqb style 2)cap data 128 0[].

Definition words_eqb(a b:words):=list_eq_dec Z.eq_dec a b.
Definition is_dot p:=if words_eqb p[46%Z]then true else false.
Definition is_parent p:=if words_eqb p[46%Z;46%Z]then true else false.
Definition split_path(data:words):=let '(parts,cur):=fold_left(fun state c=>let '(parts,cur):=state in
  if Z.eqb c 47 then(if Nat.eqb(length cur)0 then parts else parts++[cur],[])else(parts,cur++[c]))data(([]:list words),([]:words))in
  if Nat.eqb(length cur)0 then parts else parts++[cur].
Definition join_path(parts:list words):=match parts with []=>[]|x::xs=>x++flat_map(fun s=>47%Z::s)xs end.
Definition path style xs:=let data:=firstn(Z.to_nat(iz xs 0))(skipn 1 xs)in
  match find(fun i=>Z.eqb(iz data i)0)(seq 0(length data))with
  | Some p=>Some(finish[1%Z;Z.of_nat p;0%Z])
  | None=>let absolute:=Z.eqb(iz data 0)47 in let parts:=split_path data in
    let kept:=if Nat.eqb style 1 then
      let '(pending,result):=fold_right(fun part state=>let '(pending,result):=state in
        if is_dot part then(pending,result)else if is_parent part then(pending+1,result)
        else if Nat.ltb 0 pending then(pending-1,result)else(pending,part::result))(0,([]:list words))parts in
      (if absolute then[]else repeat[46%Z;46%Z]pending)++result
    else rev(fold_left(fun stack part=>if is_dot part then stack else if is_parent part then
      if negb(Nat.eqb(length stack)0)&&(Nat.eqb style 2||negb(is_parent(nth 0 stack[])))then skipn 1 stack
      else if absolute then stack else part::stack else part::stack)parts([]:list words))in
    let output:=if absolute then 47%Z::join_path kept else if Nat.eqb(length kept)0 then[46%Z]else join_path kept in
    Some(finish([0%Z;Z.of_nat(length data);Z.of_nat(length output)]++output))end.
Definition entry family style xs:=match family with
| O=>tree style xs|S O=>unionfind style xs|S(S O)=>priority style xs|S(S(S O))=>evaluator style xs
| S(S(S(S O)))=>tlv style xs|S(S(S(S(S O))))=>quotes style xs|S(S(S(S(S(S O)))))=>packbits style xs|_=>path style xs end.
Definition Equivalent(valid:words->Prop)(a b:words->option words):=forall x,valid x->exists o,a x=Some o/\b x=Some o.
Definition RefutationAt(valid:words->Prop)(a b:words->option words)(x oa ob:words):=valid x/\a x=Some oa/\b x=Some ob/\oa<>ob.
