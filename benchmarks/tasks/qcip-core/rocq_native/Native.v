(* Executable Rocq ports of the four fixed implementation families.
   No final task theorem is proved. Fuel exhaustion is None, never a result. *)
From Coq Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.
Definition words := list Z.
Definition iz (xs : words) (i : nat) : Z := nth i xs 0%Z.
Definition put {A} (xs : list A) (i : nat) (v : A) := firstn i xs ++ [v] ++ skipn (S i) xs.
Definition finish (xs : words) := Z.of_nat (length xs) :: xs.
Definition obind {A B} (x : option A) (f : A -> option B) : option B :=
  match x with Some a => f a | None => None end.
Notation "'let*' x ':=' c 'in' b" := (obind c (fun x => b))
  (at level 200, x ident, c at level 100, b at level 200).
Inductive tree := E | N (l : tree) (k v h : Z) (r : tree).
Definition ht t := match t with E => 0%Z | N _ _ _ h _ => h end.
Definition mk l k v r := N l k v (Z.max (ht l) (ht r) + 1)%Z r.
Definition bf t := match t with E => 0%Z | N l _ _ _ r => (ht l - ht r)%Z end.
Fixpoint lookup k t : words := match t with
| E => [0%Z;0%Z]
| N l x v _ r => if Z.ltb k x then lookup k l else if Z.ltb x k then lookup k r else [1%Z;v]
end.
Fixpoint project t : words := match t with E => []
| N l k v _ r => project l ++ [k;v] ++ project r end.
Fixpoint insert_bst k v t := match t with
| E => mk E k v E
| N l x y _ r => if Z.ltb k x then mk (insert_bst k v l) x y r else mk l x y (insert_bst k v r)
end.
Fixpoint take_max fuel t : option ((Z*Z)*tree) := match fuel,t with
| O,_ => None | S _,E => None
| S _,N l k v _ E => Some ((k,v),l)
| S n,N l k v _ r => let* result := take_max n r in
    let '(kv,r') := result in Some (kv,mk l k v r') end.
Fixpoint take_min fuel t : option ((Z*Z)*tree) := match fuel,t with
| O,_ => None | S _,E => None
| S _,N E k v _ r => Some ((k,v),r)
| S n,N l k v _ r => let* result := take_min n l in
    let '(kv,l') := result in Some (kv,mk l' k v r) end.
Fixpoint pushdown fuel t : option tree := match fuel,t with
| O,_ => None | S _,E => Some E
| S _,N l _ _ _ E => Some l
| S n,N l k v _ (N rl rk rv _ rr) => let* l' := pushdown n (mk l k v rl) in Some (mk l' rk rv rr)
end.
Fixpoint erase_bst style fuel t x : option tree := match fuel,t with
| _,E => Some E | O,_ => None
| S n,N l k v h r =>
  if Z.ltb x k then let* l' := erase_bst style n l x in Some (N l' k v h r)
  else if Z.ltb k x then let* r' := erase_bst style n r x in Some (N l k v h r')
  else if Nat.eqb style 2 then pushdown 64 (N l k v h r)
  else if Nat.eqb style 1 then match r,l with
    | E,_ => Some l | _,E => Some r | _,_ =>
      let* result := take_min 64 r in let '((rk,rv),r') := result in Some (mk l rk rv r') end
  else match l with E => Some r | _ =>
    let* result := take_max 64 l in let '((lk,lv),l') := result in
    Some (mk l' lk (if Nat.eqb style 3 then v else lv) r) end
end.
Fixpoint bst_loop style q t xs out : option words := match q with
| O => Some (finish (out ++ [(-2)%Z] ++ project t))
| S q' => let op := iz xs 0 in let k := iz xs 1 in
  if Z.eqb op 0 then let* t' := erase_bst style 64 t k in bst_loop style q' t' (skipn 2 xs) (out ++ [0%Z;0%Z])
  else bst_loop style q' t (skipn 2 xs) (out ++ [1%Z] ++ lookup k t) end.
Definition bst style xs :=
  let n := Z.to_nat (iz xs 0) in
  let initial := fold_left (fun t i => insert_bst (iz xs (2+2*i)) (iz xs (3+2*i)) t) (seq 0 n) E in
  bst_loop style (Z.to_nat (iz xs 1)) initial (skipn (2+2*n) xs) [].

Definition rot_l (mutant : bool) t : option tree := match t with
| N l k v _ (N mid rk rv _ rr) => Some (mk (mk l k v (if mutant then E else mid)) rk rv rr)
| _ => None end.
Definition rot_r t : option tree := match t with
| N (N ll lk lv _ mid) k v _ r => Some (mk ll lk lv (mk mid k v r)) | _ => None end.
Definition rot_lr mutant t := match t with
| N l k v _ r => let* l' := rot_l mutant l in rot_r (mk l' k v r) | _ => None end.
Definition rot_rl mutant t := match t with
| N l k v _ r => let* r' := rot_r r in rot_l mutant (mk l k v r') | _ => None end.
Definition balance style t : option tree := match t with
| E => Some E
| N l k v _ r =>
  if Z.gtb (bf t) 1 then
    if Z.gtb (bf l) 0 then rot_r t else if Z.ltb (bf l) 0 then
      if Nat.eqb style 2 then let* l' := rot_l false l in rot_r (mk l' k v r)
      else rot_lr (Nat.eqb style 3) t
    else Some t
  else if Z.ltb (bf t) (-1) then
    if Z.ltb (bf r) 0 then rot_l (Nat.eqb style 3) t else if Z.gtb (bf r) 0 then
      if Nat.eqb style 2 then let* r' := rot_r r in rot_l false (mk l k v r')
      else rot_rl (Nat.eqb style 3) t
    else Some t
  else Some t end.
Fixpoint insert_avl style fuel t x y := match fuel,t with
| _,E => Some (mk E x y E) | O,_ => None
| S n,N l k v h r =>
  if Z.ltb x k then let* l' := insert_avl style n l x y in balance style (mk l' k v r)
  else if Z.gtb x k then let* r' := insert_avl style n r x y in balance style (mk l k v r')
  else Some (N l k v h r) end.
Record crumb := { leftward : bool; ck : Z; cv : Z; sibling : tree }.
Fixpoint rebuild style path t := match path with
| [] => Some t
| c::rest => let* p := balance style (if c.(leftward) then mk t c.(ck) c.(cv) c.(sibling)
                                                   else mk c.(sibling) c.(ck) c.(cv) t) in
  rebuild style rest p end.
Fixpoint insert_stack fuel t x y path := match fuel,t with
| _,E => rebuild 1 path (mk E x y E) | O,_ => None
| S n,N l k v h r =>
  if Z.ltb x k then insert_stack n l x y ({|leftward:=true;ck:=k;cv:=v;sibling:=r|}::path)
  else if Z.gtb x k then insert_stack n r x y ({|leftward:=false;ck:=k;cv:=v;sibling:=l|}::path)
  else rebuild 1 path (N l k v h r) end.
Fixpoint avl_loop style q t xs out : option words := match q with
| O => Some (finish (out ++ [(-2)%Z] ++ project t))
| S q' => let op := iz xs 0 in let k := iz xs 1 in let v := iz xs 2 in
  if Z.eqb op 0 then
    let* t' := if Nat.eqb style 1 then insert_stack 64 t k v [] else insert_avl style 64 t k v in
    avl_loop style q' t' (skipn 3 xs) (out ++ [0%Z;0%Z])
  else avl_loop style q' t (skipn 3 xs) (out ++ [1%Z] ++ lookup k t) end.
Definition avl style xs := avl_loop style (Z.to_nat (iz xs 0)) E (skipn 1 xs) [].

Record ring_state := { data : words; capacity : nat; rd : nat; wr : nat; full : bool; count : nat }.
Definition ring_length style s :=
  if Nat.eqb style 2 then s.(count)
  else if negb (Nat.eqb style 3) && Nat.eqb s.(rd) s.(wr) && s.(full) then s.(capacity)
  else (s.(wr)+s.(capacity)-s.(rd)) mod s.(capacity).
Definition write_at (bytes : words) start (data : words) :=
  fold_left (fun a ib => put a (start+fst ib) (snd ib)) (combine (seq 0 (length bytes)) bytes) data.
Definition put_ring style s bytes :=
  let n := length bytes in
  let d := if Nat.eqb style 0 || Nat.eqb style 3 then
      let first := Nat.min n (s.(capacity)-s.(wr)) in
      write_at (skipn first bytes) 0 (write_at (firstn first bytes) s.(wr) s.(data))
    else fold_left (fun a ib => put a ((s.(wr)+fst ib) mod s.(capacity)) (snd ib))
                   (combine (seq 0 n) bytes) s.(data) in
  let w := (s.(wr)+n) mod s.(capacity) in
  {|data:=d;capacity:=s.(capacity);rd:=s.(rd);wr:=w;full:=Nat.eqb w s.(rd);count:=s.(count)+n|}.
Definition read_ring style s n :=
  let bytes := if Nat.eqb style 0 || Nat.eqb style 3 then
      let first := Nat.min n (s.(capacity)-s.(rd)) in firstn first (skipn s.(rd) s.(data)) ++ firstn (n-first) s.(data)
    else map (fun i => iz s.(data) ((s.(rd)+i) mod s.(capacity))) (seq 0 n) in
  (bytes,{|data:=s.(data);capacity:=s.(capacity);rd:=(s.(rd)+n) mod s.(capacity);wr:=s.(wr);full:=false;count:=s.(count)-n|}).
Fixpoint ring_loop style q s xs out : option words := match q with
| O => let n := ring_length style s in Some (finish (out ++ [(-2)%Z;Z.of_nat n] ++
    map (fun i => iz s.(data) ((s.(rd)+i) mod s.(capacity))) (seq 0 n)))
| S q' => let op := iz xs 0 in let n := Z.to_nat (iz xs 1) in let have := ring_length style s in
  if Z.eqb op 1 then
    let actual := Nat.min n have in let '(bytes,s') := read_ring style s actual in
    ring_loop style q' s' (skipn 66 xs) (out ++ [op;if Nat.eqb actual 0 then 1%Z else 0%Z;Z.of_nat actual] ++ bytes)
  else let free := s.(capacity)-have in let discard := if Z.eqb op 2 then n-free else 0 in
    let s' := if Nat.ltb 0 discard then
      {|data:=s.(data);capacity:=s.(capacity);rd:=(s.(rd)+discard) mod s.(capacity);wr:=s.(wr);full:=false;count:=s.(count)-discard|} else s in
    let actual := if Z.eqb op 2 then n else Nat.min n free in
    let s'' := if Nat.eqb actual 0 then s' else put_ring style s' (firstn actual (skipn 2 xs)) in
    ring_loop style q' s'' (skipn 66 xs) (out ++ [op;if Nat.eqb actual 0 then 1%Z else 0%Z;Z.of_nat actual]) end.
Definition ring style xs := ring_loop style (Z.to_nat (iz xs 1))
  {|data:=repeat 0%Z 64;capacity:=Z.to_nat (iz xs 0);rd:=0;wr:=0;full:=false;count:=0|} (skipn 2 xs) [].

Definition item := (Z*Z)%type.
Definition edge := (Z*Z*Z)%type.
Definition qi (q : list item) i := nth i q (0%Z,0%Z).
Fixpoint sorted_push (x : item) q := match q with [] => [x] | y::ys =>
  if Z.ltb (snd x) (snd y) then x::y::ys else y::sorted_push x ys end.
Fixpoint sift_up fuel i q := match fuel with O => q | S n =>
  if Nat.eqb i 0 then q else let p := (i-1)/2 in
  if Z.leb (snd (qi q p)) (snd (qi q i)) then q
  else sift_up n p (put (put q p (qi q i)) i (qi q p)) end.
Fixpoint sift_down fuel i q := match fuel with O => q | S n =>
  let l := 2*i+1 in if Nat.leb (length q) l then q else
  let c := if Nat.ltb (l+1) (length q) && Z.ltb (snd (qi q (l+1))) (snd (qi q l)) then l+1 else l in
  if Z.leb (snd (qi q i)) (snd (qi q c)) then q
  else sift_down n c (put (put q i (qi q c)) c (qi q i)) end.
Definition queue_push style x q := if Nat.eqb style 2 then sift_up 64 (length q) (q++[x]) else sorted_push x q.
Definition queue_pop style q :=
  if Nat.eqb style 2 then (qi q 0, if Nat.leb (length q) 1 then [] else
    sift_down 64 0 (put (firstn (length q-1) q) 0 (qi q (length q-1))))
  else (qi q 0,skipn 1 q).
Definition relax style (edges : list edge) u d dist queue :=
  fold_left (fun dq e => let '(ds,qu) := dq in let '(a,v,w) := e in let candidate := (d+w)%Z in
    if Z.eqb a u && Z.geb w 0 && Z.leb d (1000000000-w) && Z.ltb candidate (iz ds (Z.to_nat v)) &&
       (negb (Nat.eqb style 3) || Z.eqb (iz ds (Z.to_nat v)) 1000000000)
    then (put ds (Z.to_nat v) candidate,queue_push style (v,candidate) qu) else (ds,qu)) edges (dist,queue).
Fixpoint queue_solve style edges fuel dist q : option words := match fuel with
| O => None | S f => match q with [] => Some dist | _ =>
  let '((u,d),rest) := queue_pop style q in
  let '(ds,qs) := if Z.eqb d (iz dist (Z.to_nat u)) then relax style edges u d dist rest else (dist,rest) in
  queue_solve style edges f ds qs end end.
Fixpoint scan_solve edges n fuel dist settled := match fuel with O => dist | S f =>
  let u := fold_left (fun best i =>
    if existsb (Nat.eqb i) settled || Z.geb (iz dist i) 1000000000 then best
    else match best with None => Some i | Some j => if Z.ltb (iz dist i) (iz dist j) then Some i else best end) (seq 0 n) None in
  match u with None => dist | Some i =>
    let ds := fold_left (fun ds e => let '(a,v,w) := e in
      if Z.eqb a (Z.of_nat i) && Z.ltb (iz dist i+w) (iz ds (Z.to_nat v))
      then put ds (Z.to_nat v) (iz dist i+w)%Z else ds) edges dist in
    scan_solve edges n f ds (i::settled) end end.
Definition dijkstra style xs :=
  let n := Z.to_nat (iz xs 0) in let m := Z.to_nat (iz xs 1) in let s := iz xs 2 in
  let edges := rev (map (fun i => (iz xs (3+3*i),iz xs (4+3*i),iz xs (5+3*i))) (seq 0 m)) in
  let initial := put (repeat 1000000000%Z 10) (Z.to_nat s) 0%Z in
  let result := if Nat.eqb style 1 then Some (scan_solve edges n n initial []) else queue_solve style edges 2048 initial [(s,0%Z)] in
  let* dist := result in Some (finish (firstn n dist)).
Definition entry family style xs := match family with
| O => bst style xs | S O => avl style xs | S (S O) => ring style xs | _ => dijkstra style xs end.
Definition Equivalent {I} (valid : I -> Prop) (a b : I -> option words) :=
  forall x, valid x -> exists o, a x = Some o /\ b x = Some o.
Definition Counterexample {I} (valid : I -> Prop) (a b : I -> option words) :=
  exists x oa ob, valid x /\ a x = Some oa /\ b x = Some ob /\ oa <> ob.
Definition Certificate {I} (valid : I -> Prop) (a b : I -> option words) :=
  Equivalent valid a b \/ Counterexample valid a b.
