From Coq Require Import ZArith List Bool.
Import ListNotations.
Open Scope nat_scope.

Definition words := list Z.
Definition word (xs : words) i := nth i xs 0%Z.
Definition replace_at {A} (xs : list A) i (value : A) :=
  firstn i xs ++ [value] ++ skipn (S i) xs.
Definition finish (out : words) := Some (Z.of_nat (length out) :: out).
Definition obind {A B} (x : option A) (f : A -> option B) :=
  match x with Some a => f a | None => None end.
Notation "'let*' x ':=' c 'in' b" := (obind c (fun x => b))
  (at level 200, x ident, c at level 100, b at level 200).
Definition commands input :=
  map (fun i =>
    let p := 1+4*i in
    (word input p, Z.to_nat (word input (p+1)), word input (p+2), Z.to_nat (word input (p+3))))
    (seq 0 (Z.to_nat (word input 0))).
Definition nodes := seq 0 8.
Definition zeroes n := repeat 0%Z n.

Definition eligible_edge edges dirty seen (skip_dirty : bool) src dst :=
  Z.eqb (word edges (8*src+dst)) 1 && Z.eqb (word seen dst) 0 &&
  (negb skip_dirty || Z.eqb (word dirty dst) 0).
Definition scan_neighbors edges seen src :=
  fold_left (fun acc dst =>
    if eligible_edge edges [] acc false src dst then replace_at acc dst 1%Z else acc)
    nodes seen.
Definition scan_pass edges seen :=
  fold_left (fun acc src =>
    if Z.eqb (word acc src) 1 then scan_neighbors edges acc src else acc) nodes seen.
Definition enqueue_neighbors edges dirty skip_dirty src seen (todo : list nat) :=
  fold_left (fun state dst =>
    let '(acc,queue) := state in
    if eligible_edge edges dirty acc skip_dirty src dst then (replace_at acc dst 1%Z,queue++[dst])
    else (acc,queue)) nodes (seen,todo).
Fixpoint flood edges dirty skip_dirty fuel seen todo :=
  match todo with
  | [] => Some seen
  | src::rest =>
    match fuel with
    | O => None
    | S fuel' =>
      let '(next,queue) := enqueue_neighbors edges dirty skip_dirty src seen rest in
      flood edges dirty skip_dirty fuel' next queue
    end
  end.
Definition invalidate style edges dirty root :=
  let seed := replace_at (zeroes 8) root 1%Z in
  let* reached := if Nat.eqb style 0
    then Some (fold_left (fun acc _ => scan_pass edges acc) nodes seed)
    else flood edges dirty (Nat.eqb style 2) 8 seed [root] in
  Some (map (fun i => Z.max (word dirty i) (word reached i)) nodes).
Definition dirty_mask dirty :=
  fold_left (fun mask i => (mask + word dirty i * Z.of_nat (2^i))%Z) nodes 0%Z.
Definition graph style input :=
  let* result := fold_left (fun state cmd =>
    let* state := state in
    let '(edges,dirty,out) := state in
    let '(op,a,b,_) := cmd in
    let next_edges := if Z.leb op 1 then
      replace_at edges (8*a+Z.to_nat b) (if Z.eqb op 0 then 1%Z else 0%Z) else edges in
    let* next_dirty := if Z.eqb op 2 then invalidate style edges dirty a
      else Some (if Z.eqb op 3 then replace_at dirty a 0%Z else dirty) in
    let value := if Z.eqb op 4 then word dirty a else 0%Z in
    Some (next_edges,next_dirty,out++[op;value;dirty_mask next_dirty]))
    (commands input) (Some (zeroes 64,zeroes 8,([] : words))) in
  let '(_,_,out) := result in finish out.

Definition binding := (Z*Z)%type.
Definition layers := list (list binding).
Definition absent : binding := (0%Z,0%Z).
Definition inherited : binding := ((-1)%Z,0%Z).
Definition top_layer (stack : layers) := nth 0 stack (repeat absent 8).
Fixpoint resolve_binding key (stack : layers) :=
  match stack with
  | [] => absent
  | layer::rest =>
    let cell := nth key layer absent in
    if Z.ltb (fst cell) 0 then resolve_binding key rest else cell
  end.
Definition write_binding stack key cell :=
  replace_at (top_layer stack) key cell :: skipn 1 stack.
Definition scope_step style (stack : layers) op key value : layers * Z * binding :=
  if Z.eqb op 0 then (write_binding stack key (1%Z,value),0%Z,absent)
  else if Z.eqb op 1 then
    let cell := if Nat.eqb style 2 && Nat.ltb 1 (length stack) then inherited else absent in
    (write_binding stack key cell,0%Z,absent)
  else if Z.eqb op 2 then (stack,0%Z,resolve_binding key stack)
  else if Z.eqb op 3 then
    if Nat.eqb (length stack) 5 then (stack,2%Z,absent)
    else let layer := if Nat.eqb style 0 then top_layer stack else repeat inherited 8 in
    (layer::stack,0%Z,absent)
  else if Nat.leb (length stack) 1 then (stack,1%Z,absent)
  else (skipn 1 stack,0%Z,absent).
Definition scopes style input :=
  let '(stack,out) := fold_left (fun state cmd =>
    let '(stack,out) := state in
    let '(op,key,value,_) := cmd in
    let '(next,status,cell) := scope_step style stack op key value in
    (next,out++[op;status;fst cell;snd cell;Z.of_nat (length next-1)]))
    (commands input) ([repeat absent 8],([] : words)) in
  finish (out++flat_map (fun key =>
    let cell := resolve_binding key stack in [fst cell;snd cell]) nodes).

Record lease := Lease { live : Z; value : Z; deadline : nat }.
Record table := Table { clock : nat; entries : list lease; wheel : words }.
Definition no_lease := Lease 0%Z 0%Z 0.
Definition lease_at s key := nth key (entries s) no_lease.
Definition wheel_index time key := (time mod 9)*8+key.
Definition clear_lease style s key :=
  let old := lease_at s key in
  let w := if negb (Nat.eqb style 0) && Z.eqb (live old) 1
    then replace_at (wheel s) (wheel_index (deadline old) key) 0%Z else wheel s in
  Table (clock s) (replace_at (entries s) key no_lease) w.
Definition set_lease style s key v ttl :=
  let next := if Nat.eqb style 1 then clear_lease style s key else s in
  let expires := clock s+ttl in
  let w := if Nat.eqb style 0 then wheel next else
    replace_at (wheel next) (wheel_index expires key) 1%Z in
  Table (clock next) (replace_at (entries next) key (Lease 1%Z v expires)) w.
Definition expire_at_tick style s (keys : words) :=
  let tick := Table (S (clock s)) (entries s) (wheel s) in
  fold_left (fun state key =>
    let '(current,out) := state in
    let old := lease_at current key in
    let idx := wheel_index (clock current) key in
    let due := if Nat.eqb style 0 then Nat.eqb (deadline old) (clock current)
      else Z.eqb (word (wheel current) idx) 1 in
    let next := if Nat.eqb style 0 then current else
      Table (clock current) (entries current) (replace_at (wheel current) idx 0%Z) in
    if due && Z.eqb (live old) 1 then (clear_lease style next key,out++[Z.of_nat key])
    else (next,out)) nodes (tick,keys).
Definition advance_clock style s ticks :=
  fold_left (fun state _ =>
    let '(s,keys) := state in expire_at_tick style s keys) (seq 0 ticks) (s,([] : words)).
Definition lease_step style s op a v ttl : table * words :=
  if Z.eqb op 0 then (set_lease style s a v ttl,[op;0%Z;0%Z;0%Z])
  else if Z.eqb op 3 then
    let '(next,keys) := advance_clock style s a in
    (next,[op;0%Z;0%Z;Z.of_nat (length keys)]++keys)
  else
    let old := lease_at s a in
    let next := if Z.eqb op 2 then clear_lease style s a else s in
    (next,[op;live old;value old;0%Z]).
Definition leases style input :=
  let '(s,out) := fold_left (fun state cmd =>
    let '(s,out) := state in
    let '(op,a,b,c) := cmd in
    let '(next,obs) := lease_step style s op a b c in
    (next,out++obs)) (commands input) (Table 0 (repeat no_lease 8) (zeroes 72),([] : words)) in
  finish (out++[Z.of_nat (clock s)]++flat_map (fun key =>
    let item := lease_at s key in [live item;value item]) nodes).

Definition infinity : Z := 100000%Z.
Definition cost_add base penalty := if Z.eqb base infinity then infinity else (base+penalty)%Z.
Definition cell costs i j := word costs (13*i+j).
Definition gap_minimum open_cost extension len (prior : nat -> Z) :=
  fold_left (fun best k =>
    Z.min best (cost_add (prior k) (open_cost+extension*Z.of_nat (len-k-1))%Z))
    (seq 0 len) infinity.
Definition extend_minimum open_cost extension previous gap :=
  Z.min (cost_add previous open_cost) (cost_add gap extension).
Definition offer style (best : Z*Z) cost move :=
  if Z.ltb cost (fst best) then (cost,move)
  else if negb (Nat.eqb style 2) && Z.eqb cost (fst best) && negb (Z.eqb cost infinity)
    then (cost,(snd best+move)%Z)
    else best.
Definition diagonal_cost input costs n i j :=
  let a := word input (5+i) in
  let b := word input (5+n+j) in
  let penalty := if Z.eqb a b || Z.eqb a 4 || Z.eqb b 4 then 0%Z
    else (word input 5 + if Z.ltb a b then 1 else 0)%Z in
  cost_add (cell costs (i-1) (j-1)) penalty.
Definition align_state := (words * words * Z * Z)%type.
Definition align_cell input style n band i j (state : align_state) : align_state :=
  let '(costs,vertical,horizontal,_) := state in
  let save := fun cost moves v h =>
    (replace_at costs (13*i+j) cost,replace_at vertical j v,h,moves) in
  if Nat.ltb (j+band) i || Nat.ltb (i+band) j then save infinity 0%Z infinity infinity
  else if Nat.eqb i 0 && Nat.eqb j 0 then save 0%Z 0%Z infinity infinity
  else
    let open_cost := word input 3 in
    let extension := word input 4 in
    let v := if Nat.eqb style 0 then gap_minimum open_cost extension i (fun k => cell costs k j)
      else if Nat.eqb i 0 then infinity
      else extend_minimum open_cost extension (cell costs (i-1) j) (word vertical j) in
    let h := if Nat.eqb style 0 then gap_minimum open_cost extension j (fun k => cell costs i k)
      else if Nat.eqb j 0 then infinity
      else extend_minimum open_cost extension (cell costs i (j-1)) horizontal in
    let d := if Nat.eqb i 0 || Nat.eqb j 0 then infinity else diagonal_cost input costs n i j in
    let best := offer style (offer style (offer style (infinity,0%Z) d 1%Z) v 2%Z) h 4%Z in
    save (fst best) (snd best) v h.
Definition alignment style input :=
  let n := Z.to_nat (word input 0) in
  let m := Z.to_nat (word input 1) in
  let band := Z.to_nat (word input 2) in
  let '(costs,_,_,moves) := fold_left (fun (state : align_state) i =>
    let '(costs,vertical,_,moves) := state in
    fold_left (fun acc j => align_cell input style n band i j acc)
      (seq 0 (S m)) (costs,vertical,infinity,moves))
    (seq 0 (S n)) (repeat infinity 169,repeat infinity 13,infinity,0%Z) in
  let cost := cell costs n m in
  finish [if Z.eqb cost infinity then (-1)%Z else cost;moves].

Definition phase := (Z*Z)%type.
Definition split_phase x denominator : phase :=
  let q := (if Z.ltb x 0 then - ((-x+denominator-1)/denominator) else x/denominator)%Z in
  (q,(x-q*denominator)%Z).
Definition adjust_phase denominator (p : phase) : phase :=
  let '(idx,rem) := p in
  if Z.ltb rem 0 then ((idx-1)%Z,(rem+denominator)%Z)
  else if Z.geb rem denominator then ((idx+1)%Z,(rem-denominator)%Z)
  else p.
Definition next_phase denominator step (p : phase) :=
  fold_left (fun acc _ => adjust_phase denominator acc) (seq 0 24) (fst p,(snd p+step)%Z).
Definition round_signed style numerator denominator : Z :=
  let magnitude := Z.abs numerator in
  let twice := (2*(magnitude mod denominator))%Z in
  let inc := if (if Nat.eqb style 2 then Z.gtb twice denominator else Z.geb twice denominator)
    then 1%Z else 0%Z in
  let result := (magnitude/denominator+inc)%Z in
  (if Z.ltb numerator 0 then -result else result)%Z.
Definition interpolate style input idx rem denominator :=
  round_signed style ((denominator-rem)*word input (7+idx)+rem*word input (8+idx))%Z denominator.
Definition sample style input (p : phase) : words :=
  let last := (word input 0-1)%Z in
  let '(idx,rem) := p in
  let '(value,edge) := if Z.ltb idx 0 then (word input 7,(-1)%Z)
    else if Z.geb idx last then
      (word input (7+Z.to_nat last),if Z.gtb idx last || negb (Z.eqb rem 0) then 1%Z else 0%Z)
    else (interpolate style input (Z.to_nat idx) rem (word input 3),0%Z) in
  let lo := word input 5 in
  let hi := word input 6 in
  if Z.ltb value lo then [lo;edge;(-1)%Z]
  else if Z.gtb value hi then [hi;edge;1%Z]
  else [value;edge;0%Z].
Definition resample style input :=
  let denominator := word input 3 in
  let start := word input 4 in
  let step := word input 2 in
  let '(_,out) := fold_left (fun state i =>
    let '(p,out) := state in
    let here := if Nat.eqb style 0 then split_phase (start+Z.of_nat i*step)%Z denominator else p in
    let next := if Nat.eqb style 0 then p else next_phase denominator step p in
    (next,out++sample style input here))
    (seq 0 (Z.to_nat (word input 1))) (split_phase start denominator,([] : words)) in
  finish out.

Definition entry family style input :=
  match family with
  | O => graph style input
  | S O => scopes style input
  | S (S O) => leases style input
  | S (S (S O)) => alignment style input
  | _ => resample style input
  end.
Definition Equivalent (valid : words -> Prop) (a b : words -> option words) :=
  forall x, valid x -> exists o, a x = Some o /\ b x = Some o.
Definition RefutationAt (valid : words -> Prop) (a b : words -> option words) x oa ob :=
  valid x /\ a x = Some oa /\ b x = Some ob /\ oa <> ob.
