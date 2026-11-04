From Coq Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words:=list Z.
Definition iz(xs:words)i:=nth i xs 0%Z.
Definition put{A}(xs:list A)i(v:A):=firstn i xs++[v]++skipn(S i)xs.
Definition finish(xs:words):=Z.of_nat(length xs)::xs.
Definition obind{A B}(x:option A)(f:A->option B):=match x with Some a=>f a|None=>None end.
Notation "'let*' x ':=' c 'in' b" := (obind c (fun x=>b)) (at level 200,x ident,c at level 100,b at level 200).
Record stream_state:={sd:words;sh:nat;sn:nat;sb:nat;sc:Z;sp:Z}.
Definition smake d h n b c p:stream_state:={|sd:=d;sh:=h;sn:=n;sb:=b;sc:=c;sp:=p|}.
Definition stream_init style:=smake(if Nat.eqb style 0 then[]else repeat 0%Z 32)0 0 0 0%Z(-1)%Z.
Definition peek_byte style s i:=iz s.(sd)(if Nat.eqb style 0 then i else(s.(sh)+i)mod 32).
Definition push_byte style s c:=smake(if Nat.eqb style 0 then s.(sd)++[c]else put s.(sd)((s.(sh)+s.(sn))mod 32)c)s.(sh)(s.(sn)+1)s.(sb)s.(sc)s.(sp).
Definition drop_bytes style s n:=smake(if Nat.eqb style 0 then skipn n s.(sd)else s.(sd))
 (if Nat.eqb style 0 then 0 else(s.(sh)+n)mod 32)(s.(sn)-n)(s.(sb)+n)s.(sc)s.(sp).
Definition stream_error s c p:=smake s.(sd)s.(sh)s.(sn)s.(sb)c(Z.of_nat p).
Definition checksum_frame style s size:=fold_left(fun x i=>Z.lxor x(peek_byte style s i))(seq 0(size-1))0%Z.
Fixpoint drain_frames style fuel s n(out:words):option(stream_state*nat*words):=
 if Nat.eqb s.(sn)0||negb(Z.eqb s.(sc)0)then Some(s,n,out)else match fuel with
 | O=>None|S f=>let tag:=peek_byte style s 0 in
   if Z.ltb tag 1||Z.gtb tag 3 then Some(stream_error s 1%Z s.(sb),n,out)
   else if Nat.ltb s.(sn)2 then Some(s,n,out)else
   let len:=Z.to_nat(peek_byte style s 1)in let size:=len+3 in
   if Nat.ltb 8 len then Some(stream_error s 2%Z(s.(sb)+1),n,out)
   else if Nat.ltb s.(sn)size then Some(s,n,out)
   else if negb(Z.eqb(checksum_frame style s size)(peek_byte style s(size-1)))then Some(stream_error s 3%Z(s.(sb)+size-1),n,out)
   else drain_frames style f(drop_bytes style s size)(n+1)(out++[tag;Z.of_nat len]++map(fun i=>peek_byte style s(2+i))(seq 0 len))end.
Definition feed_chunk style s(data:words):=
 if negb(Z.eqb s.(sc)0)then Some(s,0,([]:words))else
 let first:=if Nat.eqb style 2&&Nat.eqb(length data)0 then smake s.(sd)s.(sh)0 s.(sb)s.(sc)s.(sp)else s in
 drain_frames style 32(fold_left(push_byte style)data first)0[].
Definition finish_stream s:=if Z.eqb s.(sc)0&&Nat.ltb 0 s.(sn)then stream_error s 4%Z s.(sb)else s.
Definition stream_observe style op s n(out:words):=[op;s.(sc);s.(sp);Z.of_nat s.(sb);Z.of_nat n]++out++[Z.of_nat s.(sn)]++map(peek_byte style s)(seq 0 s.(sn)).
Definition frames style xs:=
 let* result:=fold_left(fun state i=>let* state:=state in let '(s,out):=state in
   let p:=1+10*i in let op:=iz xs p in let len:=Z.to_nat(iz xs(p+1))in
   let* result:=if Z.eqb op 0 then feed_chunk style s(firstn len(skipn(p+2)xs))
     else Some(if Z.eqb op 1 then finish_stream s else stream_init style,0,([]:words))in
   let '(next,n,data):=result in Some(next,out++stream_observe style op next n data))
   (seq 0(Z.to_nat(iz xs 0)))(Some(stream_init style,([]:words)))in Some(finish(snd result)).

Record tx_state:={ts:words;tt:list words;tu:list(Z*Z*Z);tm:list nat}.
Definition tmake slots snaps undo marks:tx_state:={|ts:=slots;tt:=snaps;tu:=undo;tm:=marks|}.
Definition tx_initial:=tmake(repeat 0%Z 16)[][][].
Definition tx_depth style s:=if Nat.eqb style 0 then length s.(tt)else length s.(tm).
Definition read_slot s key:=(iz s.(ts)(2*key),iz s.(ts)(2*key+1)).
Definition write_slot s key f v:=tmake(put(put s.(ts)(2*key)f)(2*key+1)v)s.(tt)s.(tu)s.(tm).
Definition append_undo style s key:=if negb(Nat.eqb style 0)&&Nat.ltb 0(tx_depth style s)then
 let '(f,v):=read_slot s key in tmake s.(ts)s.(tt)(s.(tu)++[(Z.of_nat key,f,v)])s.(tm)else s.
Definition tx_write style s key f v:=write_slot(append_undo style s key)key f v.
Definition tx_begin style s:tx_state*Z:=if Nat.eqb(tx_depth style s)8 then(s,2%Z)else
 (if Nat.eqb style 0 then tmake s.(ts)(s.(ts)::s.(tt))s.(tu)s.(tm)else tmake s.(ts)s.(tt)s.(tu)(length s.(tu)::s.(tm)),0%Z).
Definition tx_commit style s:tx_state*Z:=if Nat.eqb(tx_depth style s)0 then(s,1%Z)else
 if Nat.eqb style 0 then(tmake s.(ts)(skipn 1 s.(tt))s.(tu)s.(tm),0%Z)else
 let mark:=nth 0 s.(tm)0 in let rest:=skipn 1 s.(tm)in
 (tmake s.(ts)s.(tt)(if Nat.eqb style 2 then firstn mark s.(tu)else if Nat.eqb(length rest)0 then[]else s.(tu))rest,0%Z).
Definition restore_undo s(u:Z*Z*Z):=let '(key,f,v):=u in write_slot s(Z.to_nat key)f v.
Definition undo_to s mark:=let restored:=fold_left restore_undo(rev(skipn mark s.(tu)))s in tmake restored.(ts)restored.(tt)(firstn mark s.(tu))restored.(tm).
Definition tx_rollback style s:tx_state*Z:=if Nat.eqb(tx_depth style s)0 then(s,1%Z)else
 if Nat.eqb style 0 then(tmake(nth 0 s.(tt)(repeat 0%Z 16))(skipn 1 s.(tt))s.(tu)s.(tm),0%Z)else
 let restored:=undo_to s(nth 0 s.(tm)0)in(tmake restored.(ts)restored.(tt)restored.(tu)(skipn 1 s.(tm)),0%Z).
Definition execute_tx style s op key value:=
 let '(next,code):=if Z.eqb op 0 then(tx_write style s(Z.to_nat key)1%Z value,0%Z)
   else if Z.eqb op 1 then(tx_write style s(Z.to_nat key)0%Z 0%Z,0%Z)
   else if Z.eqb op 3 then tx_begin style s else if Z.eqb op 4 then tx_commit style s
   else if Z.eqb op 5 then tx_rollback style s else(s,0%Z)in
 let '(f,v):=if Z.eqb op 2 then read_slot s(Z.to_nat key)else(0%Z,0%Z)in
 (next,[op;code;f;v;Z.of_nat(tx_depth style next)]).
Definition transactions style xs:=let '(s,out):=fold_left(fun state i=>let '(s,out):=state in
 let '(next,data):=execute_tx style s(iz xs(1+3*i))(iz xs(2+3*i))(iz xs(3+3*i))in(next,out++data))
 (seq 0(Z.to_nat(iz xs 0)))(tx_initial,([]:words))in Some(finish(out++[Z.of_nat(tx_depth style s)]++s.(ts))).

Record cache_node:={nk:Z;nv:Z;np:Z;nn:Z;nl:bool}.
Definition nmake k v p n l:cache_node:={|nk:=k;nv:=v;np:=p;nn:=n;nl:=l|}.
Definition empty_node:=nmake 0%Z 0%Z(-1)%Z(-1)%Z false.
Record cache_state:={cc:nat;co:list(Z*Z);cn:list cache_node;ch:Z;ct:Z}.
Definition cmake cap order nodes head tail:cache_state:={|cc:=cap;co:=order;cn:=nodes;ch:=head;ct:=tail|}.
Definition cache_initial cap:=cmake cap[](repeat empty_node 8)(-1)%Z(-1)%Z.
Definition node_at s id:=nth(Z.to_nat id)s.(cn)empty_node.
Definition set_node s id v:=cmake s.(cc)s.(co)(put s.(cn)(Z.to_nat id)v)s.(ch)s.(ct).
Definition cache_size style s:=if Nat.eqb style 0 then length s.(co)else length(filter nl s.(cn)).
Definition lookup_key style s key:Z:=let ids:=if Nat.eqb style 0 then seq 0(length s.(co))else seq 0 8 in
 match find(fun i=>if Nat.eqb style 0 then Z.eqb(fst(nth i s.(co)(0%Z,0%Z)))key else
   let node:=nth i s.(cn)empty_node in node.(nl)&&Z.eqb node.(nk)key)ids with None=>(-1)%Z|Some i=>Z.of_nat i end.
Definition item_at style s id:=if Nat.eqb style 0 then nth(Z.to_nat id)s.(co)(0%Z,0%Z)else let n:=node_at s id in(n.(nk),n.(nv)).
Definition detach s id:=let n:=node_at s id in
 let first:=if Z.ltb n.(np)0 then cmake s.(cc)s.(co)s.(cn)n.(nn)s.(ct)else
   let p:=node_at s n.(np)in set_node s n.(np)(nmake p.(nk)p.(nv)p.(np)n.(nn)p.(nl))in
 if Z.ltb n.(nn)0 then cmake first.(cc)first.(co)first.(cn)first.(ch)n.(np)else
 let r:=node_at first n.(nn)in set_node first n.(nn)(nmake r.(nk)r.(nv)n.(np)r.(nn)r.(nl)).
Definition link_front s id:=let n:=node_at s id in let first:=set_node s id(nmake n.(nk)n.(nv)(-1)%Z s.(ch)n.(nl))in
 let second:=if Z.ltb s.(ch)0 then cmake first.(cc)first.(co)first.(cn)first.(ch)id else
   let h:=node_at first s.(ch)in set_node first s.(ch)(nmake h.(nk)h.(nv)id h.(nn)h.(nl))in
 cmake second.(cc)second.(co)second.(cn)id second.(ct).
Definition erase_at style s id:=if Nat.eqb style 0 then cmake s.(cc)(firstn(Z.to_nat id)s.(co)++skipn(Z.to_nat id+1)s.(co))s.(cn)s.(ch)s.(ct)
 else let first:=detach s id in let n:=node_at first id in set_node first id(nmake n.(nk)n.(nv)n.(np)n.(nn)false).
Definition touch style s id:=if Nat.eqb style 0 then cmake s.(cc)(item_at style s id::(firstn(Z.to_nat id)s.(co)++skipn(Z.to_nat id+1)s.(co)))s.(cn)s.(ch)s.(ct)
 else link_front(detach s id)id.
Definition set_value style s id v:=if Nat.eqb style 0 then cmake s.(cc)(put s.(co)(Z.to_nat id)(fst(item_at style s id),v))s.(cn)s.(ch)s.(ct)
 else let n:=node_at s id in set_node s id(nmake n.(nk)v n.(np)n.(nn)n.(nl)).
Definition insert_front style s key value:=if Nat.eqb style 0 then cmake s.(cc)((key,value)::s.(co))s.(cn)s.(ch)s.(ct)else
 let id:=Z.of_nat(match find(fun i=>negb(nth i s.(cn)empty_node).(nl))(seq 0 8)with Some i=>i|None=>0 end)in
 let n:=node_at s id in link_front(set_node s id(nmake key value n.(np)n.(nn)true))id.
Definition evict_tail style s:=let id:=if Nat.eqb style 0 then Z.of_nat(length s.(co)-1)else s.(ct)in(erase_at style s id,item_at style s id).
Definition cache_put style s key value:=let id:=lookup_key style s key in
 if Z.geb id 0 then(touch style(set_value style s id value)id,1%Z,([]:list(Z*Z)))
 else if Nat.eqb s.(cc)0 then(s,0%Z,[])else
 let '(first,evicted):=if Nat.eqb(cache_size style s)s.(cc)then let '(t,item):=evict_tail style s in(t,[item])else(s,[])in
 (insert_front style first key value,1%Z,evicted).
Definition cache_query style s key(update:bool):=let id:=lookup_key style s key in
 if Z.ltb id 0 then(s,0%Z,0%Z)else(if update&&negb(Nat.eqb style 2)then touch style s id else s,1%Z,snd(item_at style s id)).
Fixpoint shrink_cache style fuel s(out:list(Z*Z)):=if Nat.leb(cache_size style s)s.(cc)then Some(s,out)else match fuel with
 | O=>None|S f=>let '(next,item):=evict_tail style s in shrink_cache style f next(out++[item])end.
Definition execute_cache style s op key value:=
 let* result:=if Z.eqb op 0 then let '(next,status,out):=cache_put style s key value in Some(next,status,0%Z,out)
 else if Z.eqb op 1||Z.eqb op 2 then let '(next,status,v):=cache_query style s key(Z.eqb op 1)in Some(next,status,v,[])
 else if Z.eqb op 3 then let id:=lookup_key style s key in Some(if Z.ltb id 0 then(s,0%Z,0%Z,[])else(erase_at style s id,1%Z,snd(item_at style s id),[]))
 else let* shrunk:=shrink_cache style 8(cmake(Z.to_nat key)s.(co)s.(cn)s.(ch)s.(ct))[]in Some(fst shrunk,1%Z,key,snd shrunk)in
 let '(next,status,v,evicted):=result in Some(next,[op;status;v;Z.of_nat(length evicted)]++flat_map(fun kv=>[fst kv;snd kv])evicted).
Fixpoint linked_view fuel s id:=if Z.ltb id 0 then Some([]:words)else match fuel with O=>None|S f=>
 let n:=node_at s id in let* rest:=linked_view f s n.(nn)in Some([n.(nk);n.(nv)]++rest)end.
Definition lru style xs:=let* result:=fold_left(fun state i=>let* state:=state in let '(s,out):=state in
 let* result:=execute_cache style s(iz xs(2+3*i))(iz xs(3+3*i))(iz xs(4+3*i))in Some(fst result,out++snd result))
 (seq 0(Z.to_nat(iz xs 1)))(Some(cache_initial(Z.to_nat(iz xs 0)),([]:words)))in
 let '(s,out):=result in let* data:=if Nat.eqb style 0 then Some(flat_map(fun kv=>[fst kv;snd kv])s.(co))else linked_view 8 s s.(ch)in
 Some(finish(out++[Z.of_nat s.(cc);Z.of_nat(cache_size style s)]++data)).
Definition entry family style xs:=match family with O=>frames style xs|S O=>transactions style xs|_=>lru style xs end.
Definition Equivalent(valid:words->Prop)(a b:words->option words):=forall x,valid x->exists o,a x=Some o/\b x=Some o.
Definition RefutationAt(valid:words->Prop)(a b:words->option words)(x oa ob:words):=valid x/\a x=Some oa/\b x=Some ob/\oa<>ob.
