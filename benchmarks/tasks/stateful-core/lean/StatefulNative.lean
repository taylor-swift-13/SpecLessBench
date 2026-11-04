import Lean
namespace SpecLessBenchStateful
abbrev Words := List Int
abbrev Item := Int × Int
def getOr (xs : List α) (i : Nat) (fallback : α) := (xs[i]?).getD fallback
def iz (xs : Words) (i : Nat) : Int := getOr xs i 0
def put (xs : List α) (i : Nat) (v : α) := xs.take i ++ [v] ++ xs.drop (i+1)
def finish (xs : Words) : Words := Int.ofNat xs.length :: xs

structure StreamState where
  data : Words
  head : Nat := 0
  count : Nat := 0
  base : Nat := 0
  code : Int := 0
  pos : Int := -1
def streamInit (style : Nat) : StreamState := ⟨if style == 0 then [] else List.replicate 32 0,0,0,0,0,-1⟩
def peekByte (style : Nat) (s : StreamState) (i : Nat) : Int := iz s.data (if style == 0 then i else (s.head+i)%32)
def pushByte (style : Nat) (s : StreamState) (c : Int) : StreamState :=
  {s with data := if style == 0 then s.data++[c] else put s.data ((s.head+s.count)%32) c, count := s.count+1}
def dropBytes (style : Nat) (s : StreamState) (n : Nat) : StreamState :=
  {s with data := (if style == 0 then s.data.drop n else s.data), head := (if style == 0 then 0 else (s.head+n)%32), count := s.count-n, base := s.base+n}
def streamError (s : StreamState) (code : Int) (p : Nat) : StreamState := {s with code:=code, pos:=Int.ofNat p}
def checksumFrame (style : Nat) (s : StreamState) (size : Nat) : Int :=
  Int.ofNat ((List.range (size-1)).foldl (fun x i => Nat.xor x (peekByte style s i).toNat) 0)
def drainFrames (style : Nat) : Nat → StreamState → Nat → Words → Option (StreamState × Nat × Words)
  | fuel,s,n,out =>
    if s.count == 0 || s.code != 0 then some (s,n,out) else
    match fuel with
    | 0 => none
    | f+1 =>
      let tag := peekByte style s 0
      if tag < 1 || tag > 3 then some (streamError s 1 s.base,n,out)
      else if s.count < 2 then some (s,n,out)
      else
        let len := (peekByte style s 1).toNat; let size := len+3
        if len > 8 then some (streamError s 2 (s.base+1),n,out)
        else if s.count < size then some (s,n,out)
        else if checksumFrame style s size != peekByte style s (size-1) then some (streamError s 3 (s.base+size-1),n,out)
        else drainFrames style f (dropBytes style s size) (n+1)
          (out++[tag,Int.ofNat len]++(List.range len).map (fun i => peekByte style s (2+i)))
def feedChunk (style : Nat) (s : StreamState) (data : Words) : Option (StreamState × Nat × Words) :=
  if s.code != 0 then some (s,0,[]) else
    let first := if style == 2 && data.isEmpty then {s with count:=0} else s
    drainFrames style 32 (data.foldl (pushByte style) first) 0 []
def finishStream (s : StreamState) : StreamState := if s.code == 0 && s.count > 0 then streamError s 4 s.base else s
def streamObserve (style : Nat) (op : Int) (s : StreamState) (n : Nat) (out : Words) : Words :=
  [op,s.code,s.pos,Int.ofNat s.base,Int.ofNat n]++out++[Int.ofNat s.count]++(List.range s.count).map (peekByte style s)
def frames (style : Nat) (xs : Words) : Option Words := do
  let (_,out) ← (List.range (iz xs 0).toNat).foldlM (fun (s,out) i => do
    let p := 1+10*i; let op := iz xs p; let len := (iz xs (p+1)).toNat
    let (next,n,data) ← if op == 0 then feedChunk style s ((xs.drop (p+2)).take len)
      else some (if op == 1 then finishStream s else streamInit style,0,[])
    pure (next,out++streamObserve style op next n data)) (streamInit style,([] : Words))
  pure (finish out)

structure TxState where
  slots : Words := List.replicate 16 0
  snaps : List Words := []
  undo : List (Int × Int × Int) := []
  marks : List Nat := []
def txDepth (style : Nat) (s : TxState) : Nat := if style == 0 then s.snaps.length else s.marks.length
def readSlot (s : TxState) (key : Nat) : Item := (iz s.slots (2*key),iz s.slots (2*key+1))
def writeSlot (s : TxState) (key : Nat) (f v : Int) : TxState := {s with slots:=put (put s.slots (2*key) f) (2*key+1) v}
def appendUndo (style : Nat) (s : TxState) (key : Nat) : TxState :=
  if style != 0 && txDepth style s > 0 then
    let (f,v) := readSlot s key
    {s with undo:=s.undo++[(Int.ofNat key,f,v)]}
  else s
def txWrite (style : Nat) (s : TxState) (key : Nat) (f v : Int) : TxState := writeSlot (appendUndo style s key) key f v
def txBegin (style : Nat) (s : TxState) : TxState × Int :=
  if txDepth style s == 8 then (s,2) else
  (if style == 0 then {s with snaps:=s.slots::s.snaps} else {s with marks:=s.undo.length::s.marks},0)
def txCommit (style : Nat) (s : TxState) : TxState × Int :=
  if txDepth style s == 0 then (s,1) else
  if style == 0 then ({s with snaps:=s.snaps.drop 1},0)
  else
    let mark := getOr s.marks 0 0; let rest := s.marks.drop 1
    ({s with marks:=rest, undo:=if style == 2 then s.undo.take mark else if rest.isEmpty then [] else s.undo},0)
def restoreUndo (s : TxState) (u : Int × Int × Int) : TxState :=
  let (key,f,v) := u
  writeSlot s key.toNat f v
def undoTo (s : TxState) (mark : Nat) : TxState :=
  let restored := (s.undo.drop mark).reverse.foldl restoreUndo s
  {restored with undo:=s.undo.take mark}
def txRollback (style : Nat) (s : TxState) : TxState × Int :=
  if txDepth style s == 0 then (s,1) else
  if style == 0 then ({s with slots:=getOr s.snaps 0 (List.replicate 16 0),snaps:=s.snaps.drop 1},0)
  else ({(undoTo s (getOr s.marks 0 0)) with marks:=s.marks.drop 1},0)
def executeTx (style : Nat) (s : TxState) (op key value : Int) : TxState × Words :=
  let (next,code) := if op == 0 then (txWrite style s key.toNat 1 value,0)
    else if op == 1 then (txWrite style s key.toNat 0 0,0)
    else if op == 3 then txBegin style s else if op == 4 then txCommit style s
    else if op == 5 then txRollback style s else (s,0)
  let (f,v) := if op == 2 then readSlot s key.toNat else (0,0)
  (next,[op,code,f,v,Int.ofNat (txDepth style next)])
def transactions (style : Nat) (xs : Words) : Option Words :=
  let (s,out) := (List.range (iz xs 0).toNat).foldl (fun (s,out) i =>
    let (next,data) := executeTx style s (iz xs (1+3*i)) (iz xs (2+3*i)) (iz xs (3+3*i))
    (next,out++data)) (({} : TxState),([] : Words))
  some (finish (out++[Int.ofNat (txDepth style s)]++s.slots))

structure CacheNode where
  key : Int := 0
  value : Int := 0
  prev : Int := -1
  next : Int := -1
  live : Bool := false
structure CacheState where
  cap : Nat
  order : List Item := []
  nodes : List CacheNode := List.replicate 8 {}
  head : Int := -1
  tail : Int := -1
def nodeAt (s : CacheState) (id : Int) : CacheNode := getOr s.nodes id.toNat {}
def setNode (s : CacheState) (id : Int) (v : CacheNode) : CacheState := {s with nodes:=put s.nodes id.toNat v}
def cacheSize (style : Nat) (s : CacheState) : Nat := if style == 0 then s.order.length else (s.nodes.filter (·.live)).length
def lookupKey (style : Nat) (s : CacheState) (key : Int) : Int :=
  let ids := if style == 0 then List.range s.order.length else List.range 8
  match ids.find? (fun i => if style == 0 then (getOr s.order i (0,0)).1 == key else
    let node := getOr s.nodes i ({} : CacheNode)
    node.live && node.key == key) with
  | none => -1 | some i => Int.ofNat i
def itemAt (style : Nat) (s : CacheState) (id : Int) : Item :=
  if style == 0 then getOr s.order id.toNat (0,0) else let node := nodeAt s id; (node.key,node.value)
def detach (s : CacheState) (id : Int) : CacheState :=
  let node := nodeAt s id
  let first := if node.prev < 0 then {s with head:=node.next} else
    setNode s node.prev {(nodeAt s node.prev) with next:=node.next}
  if node.next < 0 then {first with tail:=node.prev} else
    setNode first node.next {(nodeAt first node.next) with prev:=node.prev}
def linkFront (s : CacheState) (id : Int) : CacheState :=
  let first := setNode s id {(nodeAt s id) with prev := -1,next:=s.head}
  let second := if s.head < 0 then {first with tail:=id} else setNode first s.head {(nodeAt first s.head) with prev:=id}
  {second with head:=id}
def eraseAt (style : Nat) (s : CacheState) (id : Int) : CacheState :=
  if style == 0 then {s with order:=s.order.take id.toNat++s.order.drop (id.toNat+1)}
  else let first := detach s id; setNode first id {(nodeAt first id) with live:=false}
def touch (style : Nat) (s : CacheState) (id : Int) : CacheState :=
  if style == 0 then {s with order:=itemAt style s id::(s.order.take id.toNat++s.order.drop (id.toNat+1))}
  else linkFront (detach s id) id
def setValue (style : Nat) (s : CacheState) (id value : Int) : CacheState :=
  if style == 0 then {s with order:=put s.order id.toNat ((itemAt style s id).1,value)}
  else setNode s id {(nodeAt s id) with value:=value}
def insertFront (style : Nat) (s : CacheState) (key value : Int) : CacheState :=
  if style == 0 then {s with order:=(key,value)::s.order} else
  let id := Int.ofNat (((List.range 8).find? (fun i => !(getOr s.nodes i ({} : CacheNode)).live)).getD 0)
  linkFront (setNode s id {(nodeAt s id) with key:=key,value:=value,live:=true}) id
def evictTail (style : Nat) (s : CacheState) : CacheState × Item :=
  let id := if style == 0 then Int.ofNat (s.order.length-1) else s.tail
  (eraseAt style s id,itemAt style s id)
def cachePut (style : Nat) (s : CacheState) (key value : Int) : CacheState × Int × List Item :=
  let id := lookupKey style s key
  if id ≥ 0 then (touch style (setValue style s id value) id,1,[])
  else if s.cap == 0 then (s,0,[])
  else
    let (first,evicted) := if cacheSize style s == s.cap then let (t,item) := evictTail style s; (t,[item]) else (s,[])
    (insertFront style first key value,1,evicted)
def cacheQuery (style : Nat) (s : CacheState) (key : Int) (update : Bool) : CacheState × Int × Int :=
  let id := lookupKey style s key
  if id < 0 then (s,0,0) else
    (if update && style != 2 then touch style s id else s,1,(itemAt style s id).2)
def shrinkCache (style : Nat) : Nat → CacheState → List Item → Option (CacheState × List Item)
  | fuel,s,out => if cacheSize style s ≤ s.cap then some (s,out) else
    match fuel with
    | 0 => none
    | f+1 => let (next,item) := evictTail style s; shrinkCache style f next (out++[item])
def executeCache (style : Nat) (s : CacheState) (op key value : Int) : Option (CacheState × Words) := do
  let (next,status,v,evicted) ← if op == 0 then
      let (next,status,out) := cachePut style s key value; some (next,status,(0 : Int),out)
    else if op == 1 || op == 2 then
      let (next,status,v) := cacheQuery style s key (op == 1); some (next,status,v,[])
    else if op == 3 then
      let id := lookupKey style s key
      some (if id < 0 then (s,0,0,[]) else (eraseAt style s id,1,(itemAt style s id).2,[]))
    else do
      let (next,out) ← shrinkCache style 8 {s with cap:=key.toNat} []
      some (next,1,key,out)
  pure (next,[op,status,v,Int.ofNat evicted.length]++evicted.flatMap (fun (k,v) => [k,v]))
def linkedView : Nat → CacheState → Int → Option Words
  | fuel,s,id => if id < 0 then some [] else
    match fuel with
    | 0 => none
    | f+1 => do
      let node := nodeAt s id
      let rest ← linkedView f s node.next
      pure ([node.key,node.value]++rest)
def lru (style : Nat) (xs : Words) : Option Words := do
  let (s,out) ← (List.range (iz xs 1).toNat).foldlM (fun (s,out) i => do
    let (next,data) ← executeCache style s (iz xs (2+3*i)) (iz xs (3+3*i)) (iz xs (4+3*i))
    pure (next,out++data)) (({cap:=(iz xs 0).toNat} : CacheState),([] : Words))
  let data ← if style == 0 then some (s.order.flatMap (fun (k,v) => [k,v])) else linkedView 8 s s.head
  pure (finish (out++[Int.ofNat s.cap,Int.ofNat (cacheSize style s)]++data))
def entry (family style : Nat) (xs : Words) : Option Words :=
  match family with | 0 => frames style xs | 1 => transactions style xs | _ => lru style xs
def Equivalent (valid : Words → Prop) (a b : Words → Option Words) : Prop := ∀ x, valid x → ∃ o, a x=some o ∧ b x=some o
def RefutationAt (valid : Words → Prop) (a b : Words → Option Words) (x oa ob : Words) : Prop := valid x ∧ a x=some oa ∧ b x=some ob ∧ oa≠ob
end SpecLessBenchStateful
