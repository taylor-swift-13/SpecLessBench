import Lean

/- Executable native implementations; no task proof or admitted theorem.
   Fuel exhaustion is explicit failure and never an equal successful result. -/
namespace SpecLessBench
abbrev Words := List Int
def getOr (xs : List α) (i : Nat) (fallback : α) : α := (xs[i]?).getD fallback
def iz (xs : Words) (i : Nat) : Int := getOr xs i 0
def put (xs : List α) (i : Nat) (v : α) : List α := xs.take i ++ [v] ++ xs.drop (i+1)
def finish (xs : Words) : Words := (Int.ofNat xs.length) :: xs
def keyBound (x : Int) : Prop := -1024 ≤ x ∧ x ≤ 1024
def valueBound (x : Int) : Prop := -1000000 ≤ x ∧ x ≤ 1000000
def pad (n : Nat) (xs : Words) := xs ++ List.replicate (n-xs.length) 0

inductive Tree where
  | empty
  | node (left : Tree) (key value height : Int) (right : Tree)
deriving Repr
open Tree
def ht : Tree → Int | empty => 0 | node _ _ _ h _ => h
def mk (l : Tree) (k v : Int) (r : Tree) := node l k v (max (ht l) (ht r) + 1) r
def bf : Tree → Int | empty => 0 | node l _ _ _ r => ht l - ht r
def lookup (k : Int) : Tree → Words
  | empty => [0,0]
  | node l x v _ r => if k < x then lookup k l else if x < k then lookup k r else [1,v]
def project : Tree → Words
  | empty => []
  | node l k v _ r => project l ++ [k,v] ++ project r
def insertBST (k v : Int) : Tree → Tree
  | empty => mk empty k v empty
  | node l x y _ r => if k < x then mk (insertBST k v l) x y r else mk l x y (insertBST k v r)
def takeMax : Nat → Tree → Option ((Int × Int) × Tree)
  | 0, _ => none
  | _+1, empty => none
  | _+1, node l k v _ empty => some ((k,v),l)
  | n+1, node l k v _ r => do
      let (kv,r') ← takeMax n r
      pure (kv,mk l k v r')
def takeMin : Nat → Tree → Option ((Int × Int) × Tree)
  | 0, _ => none
  | _+1, empty => none
  | _+1, node empty k v _ r => some ((k,v),r)
  | n+1, node l k v _ r => do
      let (kv,l') ← takeMin n l
      pure (kv,mk l' k v r)
def pushdown : Nat → Tree → Option Tree
  | 0, _ => none
  | _+1, empty => some empty
  | _+1, node l _ _ _ empty => some l
  | n+1, node l k v _ (node rl rk rv _ rr) => do
      let l' ← pushdown n (mk l k v rl)
      pure (mk l' rk rv rr)
def eraseBST (style : Nat) : Nat → Tree → Int → Option Tree
  | _, empty, _ => some empty
  | 0, _, _ => none
  | n+1, node l k v h r, x =>
    if x < k then do
      let l' ← eraseBST style n l x
      pure (node l' k v h r)
    else if k < x then do
      let r' ← eraseBST style n r x
      pure (node l k v h r')
    else if style == 2 then pushdown 64 (node l k v h r)
    else if style == 1 then
      match r, l with
      | empty, _ => some l
      | _, empty => some r
      | _, _ => do
          let ((rk,rv),r') ← takeMin 64 r
          pure (mk l rk rv r')
    else
      match l with
      | empty => some r
      | _ => do
          let ((lk,lv),l') ← takeMax 64 l
          pure (mk l' lk (if style == 3 then v else lv) r)
def bstLoop (style : Nat) : Nat → Tree → Words → Words → Option Words
  | 0, t, _, out => some (finish (out ++ [-2] ++ project t))
  | q+1, t, xs, out =>
      let op := iz xs 0; let k := iz xs 1
      if op == 0 then do
        let t' ← eraseBST style 64 t k
        bstLoop style q t' (xs.drop 2) (out ++ [0,0])
      else bstLoop style q t (xs.drop 2) (out ++ [1] ++ lookup k t)
def bst (style : Nat) (xs : Words) : Option Words :=
  let n := (iz xs 0).toNat
  let initial := (List.range n).foldl (fun t i => insertBST (iz xs (2+2*i)) (iz xs (3+2*i)) t) empty
  bstLoop style (iz xs 1).toNat initial (xs.drop (2+2*n)) []

def rotL (mutant : Bool) : Tree → Option Tree
  | node l k v _ (node mid rk rv _ rr) => some (mk (mk l k v (if mutant then empty else mid)) rk rv rr)
  | _ => none
def rotR : Tree → Option Tree
  | node (node ll lk lv _ mid) k v _ r => some (mk ll lk lv (mk mid k v r))
  | _ => none
def rotLR (mutant : Bool) : Tree → Option Tree
  | node l k v _ r => do let l' ← rotL mutant l; rotR (mk l' k v r)
  | _ => none
def rotRL (mutant : Bool) : Tree → Option Tree
  | node l k v _ r => do let r' ← rotR r; rotL mutant (mk l k v r')
  | _ => none
def balance (style : Nat) (t : Tree) : Option Tree :=
  match t with
  | empty => some empty
  | node l k v _ r =>
    if bf t > 1 then
      if bf l > 0 then rotR t
      else if bf l < 0 then
        if style == 2 then do let l' ← rotL false l; rotR (mk l' k v r)
        else rotLR (style == 3) t
      else some t
    else if bf t < -1 then
      if bf r < 0 then rotL (style == 3) t
      else if bf r > 0 then
        if style == 2 then do let r' ← rotR r; rotL false (mk l k v r')
        else rotRL (style == 3) t
      else some t
    else some t
def insertAVL (style : Nat) : Nat → Tree → Int → Int → Option Tree
  | _, empty, k, v => some (mk empty k v empty)
  | 0, _, _, _ => none
  | n+1, node l k v h r, x, y =>
    if x < k then do let l' ← insertAVL style n l x y; balance style (mk l' k v r)
    else if x > k then do let r' ← insertAVL style n r x y; balance style (mk l k v r')
    else some (node l k v h r)
abbrev Crumb := Bool × Int × Int × Tree
def rebuild (style : Nat) : List Crumb → Tree → Option Tree
  | [], t => some t
  | (left,k,v,sibling)::path, t => do
      let p ← balance style (if left then mk t k v sibling else mk sibling k v t)
      rebuild style path p
def insertStack : Nat → Tree → Int → Int → List Crumb → Option Tree
  | _, empty, k, v, path => rebuild 1 path (mk empty k v empty)
  | 0, _, _, _, _ => none
  | n+1, node l k v h r, x, y, path =>
    if x < k then insertStack n l x y ((true,k,v,r)::path)
    else if x > k then insertStack n r x y ((false,k,v,l)::path)
    else rebuild 1 path (node l k v h r)
def avlLoop (style : Nat) : Nat → Tree → Words → Words → Option Words
  | 0, t, _, out => some (finish (out ++ [-2] ++ project t))
  | q+1, t, xs, out =>
      let op := iz xs 0; let k := iz xs 1; let v := iz xs 2
      if op == 0 then do
        let t' ← if style == 1 then insertStack 64 t k v [] else insertAVL style 64 t k v
        avlLoop style q t' (xs.drop 3) (out ++ [0,0])
      else avlLoop style q t (xs.drop 3) (out ++ [1] ++ lookup k t)
def avl (style : Nat) (xs : Words) := avlLoop style (iz xs 0).toNat empty (xs.drop 1) []

structure RingState where
  data : Words := List.replicate 64 0
  capacity : Nat
  rd : Nat := 0
  wr : Nat := 0
  full : Bool := false
  count : Nat := 0
def ringLength (style : Nat) (s : RingState) : Nat :=
  if style == 2 then s.count
  else if style != 3 && s.rd == s.wr && s.full then s.capacity
  else (s.wr+s.capacity-s.rd)%s.capacity
def writeAt (data bytes : Words) (start : Nat) : Words :=
  (bytes.zipIdx).foldl (fun a (b,i) => put a (start+i) b) data
def putRing (style : Nat) (s : RingState) (bytes : Words) : RingState :=
  let n := bytes.length
  let data := if style == 0 || style == 3 then
      let first := min n (s.capacity-s.wr)
      writeAt (writeAt s.data (bytes.take first) s.wr) (bytes.drop first) 0
    else (bytes.zipIdx).foldl (fun a (b,i) => put a ((s.wr+i)%s.capacity) b) s.data
  let wr := (s.wr+n)%s.capacity
  {s with data := data, wr := wr, full := wr == s.rd, count := s.count+n}
def readRing (style : Nat) (s : RingState) (n : Nat) : Words × RingState :=
  let bytes := if style == 0 || style == 3 then
      let first := min n (s.capacity-s.rd)
      (s.data.drop s.rd).take first ++ s.data.take (n-first)
    else (List.range n).map (fun i => iz s.data ((s.rd+i)%s.capacity))
  (bytes,{s with rd := (s.rd+n)%s.capacity, full := false, count := s.count-n})
def ringLoop (style : Nat) : Nat → RingState → Words → Words → Option Words
  | 0, s, _, out =>
      let n := ringLength style s
      some (finish (out ++ [-2,Int.ofNat n] ++ (List.range n).map (fun i => iz s.data ((s.rd+i)%s.capacity))))
  | q+1, s, xs, out =>
    let op := iz xs 0; let n := (iz xs 1).toNat
    let occupied := ringLength style s
    if op == 1 then
      let actual := min n occupied
      let (bytes,s') := readRing style s actual
      ringLoop style q s' (xs.drop 66) (out ++ [op,if actual == 0 then 1 else 0,Int.ofNat actual] ++ bytes)
    else
      let free := s.capacity-occupied
      let discard := if op == 2 then n-free else 0
      let s' := if discard > 0 then {s with rd := (s.rd+discard)%s.capacity, count := s.count-discard, full := false} else s
      let actual := if op == 2 then n else min n free
      let s'' := if actual == 0 then s' else putRing style s' ((xs.drop 2).take actual)
      ringLoop style q s'' (xs.drop 66) (out ++ [op,if actual == 0 then 1 else 0,Int.ofNat actual])
def ring (style : Nat) (xs : Words) :=
  ringLoop style (iz xs 1).toNat {capacity := (iz xs 0).toNat} (xs.drop 2) []

abbrev Item := Int × Int
abbrev Edge := Int × Int × Int
def item (q : List Item) (i : Nat) : Item := getOr q i (0,0)
def sortedPush (x : Item) : List Item → List Item
  | [] => [x]
  | y::ys => if x.2 < y.2 then x::y::ys else y::sortedPush x ys
def siftUp : Nat → Nat → List Item → List Item
  | 0, _, q => q
  | n+1, i, q =>
      if i == 0 then q else
      let p := (i-1)/2
      if (item q p).2 ≤ (item q i).2 then q
      else siftUp n p (put (put q p (item q i)) i (item q p))
def siftDown : Nat → Nat → List Item → List Item
  | 0, _, q => q
  | n+1, i, q =>
      let l := 2*i+1
      if l ≥ q.length then q else
      let c := if l+1 < q.length && (item q (l+1)).2 < (item q l).2 then l+1 else l
      if (item q i).2 ≤ (item q c).2 then q
      else siftDown n c (put (put q i (item q c)) c (item q i))
def queuePush (style : Nat) (x : Item) (q : List Item) :=
  if style == 2 then siftUp 64 q.length (q++[x]) else sortedPush x q
def queuePop (style : Nat) (q : List Item) : Item × List Item :=
  if style == 2 then
    let rest := if q.length ≤ 1 then [] else siftDown 64 0 (put (q.take (q.length-1)) 0 (item q (q.length-1)))
    (item q 0,rest)
  else (item q 0,q.drop 1)
def relax (style : Nat) (edges : List Edge) (u d : Int) (dist : Words) (queue : List Item) : Words × List Item :=
  edges.foldl (fun (ds,qu) (a,v,w) =>
    let candidate := d+w
    if a == u && w ≥ 0 && d ≤ 1000000000-w && candidate < iz ds v.toNat && (style != 3 || iz ds v.toNat == 1000000000)
    then (put ds v.toNat candidate,queuePush style (v,candidate) qu)
    else (ds,qu)) (dist,queue)
def queueSolve (style : Nat) (edges : List Edge) : Nat → Words → List Item → Option Words
  | 0, _, _ => none
  | fuel+1, dist, q =>
      if q.isEmpty then some dist else
      let ((u,d),rest) := queuePop style q
      let (ds,qs) := if d == iz dist u.toNat then relax style edges u d dist rest else (dist,rest)
      queueSolve style edges fuel ds qs
def scanSolve (edges : List Edge) (n : Nat) : Nat → Words → List Nat → Words
  | 0, dist, _ => dist
  | fuel+1, dist, settled =>
    let u := (List.range n).foldl (fun best i =>
      if settled.contains i || iz dist i ≥ 1000000000 then best
      else match best with | none => some i | some j => if iz dist i < iz dist j then some i else best) none
    match u with
    | none => dist
    | some i =>
      let ds := edges.foldl (fun ds (a,v,w) =>
        if a == Int.ofNat i && iz dist i+w < iz ds v.toNat then put ds v.toNat (iz dist i+w) else ds) dist
      scanSolve edges n fuel ds (i::settled)
def dijkstra (style : Nat) (xs : Words) : Option Words :=
  let n := (iz xs 0).toNat; let m := (iz xs 1).toNat; let s := iz xs 2
  let edges : List Edge := ((List.range m).map (fun i => (iz xs (3+3*i),iz xs (4+3*i),iz xs (5+3*i)))).reverse
  let initial := put (List.replicate 10 1000000000) s.toNat 0
  let result := if style == 1 then some (scanSolve edges n n initial [])
    else queueSolve style edges 2048 initial [(s,0)]
  result.map (fun dist => finish (dist.take n))

def entry (family style : Nat) (xs : Words) : Option Words :=
  match family with | 0 => bst style xs | 1 => avl style xs | 2 => ring style xs | _ => dijkstra style xs
def Equivalent (valid : α → Prop) (a b : α → Option Words) : Prop :=
  ∀ x, valid x → ∃ o, a x = some o ∧ b x = some o
def Counterexample (valid : α → Prop) (a b : α → Option Words) : Prop :=
  ∃ x oa ob, valid x ∧ a x = some oa ∧ b x = some ob ∧ oa ≠ ob
def Certificate (valid : α → Prop) (a b : α → Option Words) : Prop := Equivalent valid a b ∨ Counterexample valid a b
end SpecLessBench

def main : IO Unit := do
  let stdin ← IO.getStdin; let stdout ← IO.getStdout
  repeat
    let line ← stdin.getLine
    if line.isEmpty then break
    let fields := ((line.trimAscii.toString.splitOn " ").filter (· != "")).map (fun s => s.toInt?.getD 0)
    let family := (SpecLessBench.iz fields 0).toNat
    let style := (SpecLessBench.iz fields 1).toNat
    match SpecLessBench.entry family style (fields.drop 2) with
    | none => stdout.putStrLn "FAIL"
    | some xs => stdout.putStrLn (String.intercalate " " (xs.map toString))
