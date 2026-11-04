import Lean

namespace EqualBenchSystems

abbrev Words := List Int

def getOr (xs : List α) (i : Nat) (fallback : α) := (xs[i]?).getD fallback
def word (xs : Words) (i : Nat) : Int := getOr xs i 0
def replaceAt (xs : List α) (i : Nat) (value : α) :=
  xs.take i ++ [value] ++ xs.drop (i+1)
def finish (out : Words) : Option Words := some (Int.ofNat out.length :: out)
def commands (input : Words) : List (Int × Nat × Int × Nat) :=
  (List.range (word input 0).toNat).map fun i =>
    let p := 1+4*i
    (word input p,(word input (p+1)).toNat,word input (p+2),(word input (p+3)).toNat)
def nodes := List.range 8
def zeroes (n : Nat) : Words := List.replicate n 0

def eligibleEdge (edges dirty seen : Words) (skipDirty : Bool) (src dst : Nat) : Bool :=
  word edges (8*src+dst) == 1 && word seen dst == 0 && (!skipDirty || word dirty dst == 0)

def scanNeighbors (edges seen : Words) (src : Nat) : Words :=
  nodes.foldl (fun acc dst =>
    if eligibleEdge edges [] acc false src dst then replaceAt acc dst 1 else acc) seen

def scanPass (edges seen : Words) : Words :=
  nodes.foldl (fun acc src =>
    if word acc src == 1 then scanNeighbors edges acc src else acc) seen

def enqueueNeighbors (edges dirty : Words) (skipDirty : Bool) (src : Nat)
    (seen : Words) (todo : List Nat) : Words × List Nat :=
  nodes.foldl (fun (acc,queue) dst =>
    if eligibleEdge edges dirty acc skipDirty src dst then
      (replaceAt acc dst 1,queue++[dst])
    else (acc,queue)) (seen,todo)

def flood (edges dirty : Words) (skipDirty : Bool) : Nat → Words → List Nat → Option Words
  | _,seen,[] => some seen
  | 0,_,_::_ => none
  | fuel+1,seen,src::rest =>
    let (next,todo) := enqueueNeighbors edges dirty skipDirty src seen rest
    flood edges dirty skipDirty fuel next todo

def invalidate (style : Nat) (edges dirty : Words) (root : Nat) : Option Words := do
  let seed := replaceAt (zeroes 8) root 1
  let reached ← if style == 0 then
      some (nodes.foldl (fun acc _ => scanPass edges acc) seed)
    else flood edges dirty (style == 2) 8 seed [root]
  pure (nodes.map fun i => max (word dirty i) (word reached i))

def dirtyMask (dirty : Words) : Int :=
  nodes.foldl (fun mask i => mask + word dirty i * Int.ofNat (2^i)) 0

def graph (style : Nat) (input : Words) : Option Words := do
  let (_,_,out) ← (commands input).foldlM (fun (edges,dirty,out) (op,a,b,_) => do
    let nextEdges := if op ≤ 1 then replaceAt edges (8*a+b.toNat) (if op == 0 then 1 else 0) else edges
    let nextDirty ← if op == 2 then invalidate style edges dirty a
      else some (if op == 3 then replaceAt dirty a 0 else dirty)
    let value := if op == 4 then word dirty a else 0
    pure (nextEdges,nextDirty,out++[op,value,dirtyMask nextDirty])) (zeroes 64,zeroes 8,([] : Words))
  finish out

abbrev Binding := Int × Int
abbrev Layers := List (List Binding)
def absent : Binding := (0,0)
def inherit : Binding := (-1,0)
def topLayer (layers : Layers) := getOr layers 0 (List.replicate 8 absent)
def resolveBinding (key : Nat) : Layers → Binding
  | [] => absent
  | layer::rest =>
    let cell := getOr layer key absent
    if cell.1 < 0 then resolveBinding key rest else cell
def writeBinding (layers : Layers) (key : Nat) (cell : Binding) : Layers :=
  replaceAt (topLayer layers) key cell :: layers.drop 1
def scopeStep (style : Nat) (layers : Layers) (op : Int) (key : Nat) (value : Int) :
    Layers × Int × Binding :=
  if op == 0 then (writeBinding layers key (1,value),0,absent)
  else if op == 1 then
    let cell := if style == 2 && layers.length > 1 then inherit else absent
    (writeBinding layers key cell,0,absent)
  else if op == 2 then (layers,0,resolveBinding key layers)
  else if op == 3 then
    if layers.length == 5 then (layers,2,absent)
    else
      let layer := if style == 0 then topLayer layers else List.replicate 8 inherit
      (layer::layers,0,absent)
  else if layers.length ≤ 1 then (layers,1,absent)
  else (layers.drop 1,0,absent)

def scopes (style : Nat) (input : Words) : Option Words :=
  let (layers,out) := (commands input).foldl (fun (layers,out) (op,key,value,_) =>
    let (next,status,(found,result)) := scopeStep style layers op key value
    (next,out++[op,status,found,result,Int.ofNat (next.length-1)]))
    ([List.replicate 8 absent],([] : Words))
  finish (out++nodes.flatMap (fun key =>
    let (found,value) := resolveBinding key layers
    [found,value]))

structure Lease where
  live : Int := 0
  value : Int := 0
  deadline : Nat := 0
structure LeaseTable where
  clock : Nat := 0
  entries : List Lease := List.replicate 8 {}
  wheel : Words := zeroes 72

def leaseAt (s : LeaseTable) (key : Nat) : Lease := getOr s.entries key {}
def wheelIndex (time key : Nat) := (time%9)*8+key
def clearLease (style : Nat) (s : LeaseTable) (key : Nat) : LeaseTable :=
  let old := leaseAt s key
  let wheel := if style != 0 && old.live == 1 then replaceAt s.wheel (wheelIndex old.deadline key) 0 else s.wheel
  {s with entries := replaceAt s.entries key {}, wheel := wheel}
def setLease (style : Nat) (s : LeaseTable) (key : Nat) (value : Int) (ttl : Nat) : LeaseTable :=
  let next := if style == 1 then clearLease style s key else s
  let deadline := s.clock+ttl
  let wheel := if style == 0 then next.wheel else replaceAt next.wheel (wheelIndex deadline key) 1
  {next with entries := replaceAt next.entries key ⟨1,value,deadline⟩, wheel := wheel}

def expireAtTick (style : Nat) (s : LeaseTable) (keys : Words) : LeaseTable × Words :=
  let tick := {s with clock := s.clock+1}
  nodes.foldl (fun (table,out) key =>
    let old := leaseAt table key
    let idx := wheelIndex table.clock key
    let due := if style == 0 then old.deadline == table.clock else word table.wheel idx == 1
    let next := if style == 0 then table else {table with wheel := replaceAt table.wheel idx 0}
    if due && old.live == 1 then (clearLease style next key,out++[Int.ofNat key])
    else (next,out)) (tick,keys)

def advanceClock (style : Nat) (s : LeaseTable) (ticks : Nat) : LeaseTable × Words :=
  (List.range ticks).foldl (fun (table,keys) _ => expireAtTick style table keys) (s,[])

def leaseStep (style : Nat) (s : LeaseTable) (op : Int) (a : Nat) (value : Int) (ttl : Nat) :
    LeaseTable × Words :=
  if op == 0 then (setLease style s a value ttl,[op,0,0,0])
  else if op == 3 then
    let (next,keys) := advanceClock style s a
    (next,[op,0,0,Int.ofNat keys.length]++keys)
  else
    let old := leaseAt s a
    let next := if op == 2 then clearLease style s a else s
    (next,[op,old.live,old.value,0])

def leases (style : Nat) (input : Words) : Option Words :=
  let (s,out) := (commands input).foldl (fun (s,out) (op,a,b,c) =>
    let (next,obs) := leaseStep style s op a b c
    (next,out++obs)) (({} : LeaseTable),([] : Words))
  finish (out++[Int.ofNat s.clock]++nodes.flatMap (fun key =>
    let item := leaseAt s key
    [item.live,item.value]))

def infinity : Int := 100000
def costAdd (base penalty : Int) := if base == infinity then infinity else base+penalty
def cell (costs : Words) (i j : Nat) := word costs (13*i+j)
def gapMinimum (openCost extension : Int) (length : Nat) (prior : Nat → Int) : Int :=
  (List.range length).foldl (fun best k =>
    min best (costAdd (prior k) (openCost+extension*Int.ofNat (length-k-1)))) infinity
def extendMinimum (openCost extension previous gap : Int) : Int :=
  min (costAdd previous openCost) (costAdd gap extension)
def offer (style : Nat) (best : Int × Int) (cost move : Int) : Int × Int :=
  if cost < best.1 then (cost,move)
  else if style != 2 && cost == best.1 && cost != infinity then (cost,best.2+move)
  else best
def diagonalCost (input costs : Words) (n i j : Nat) : Int :=
  let a := word input (5+i)
  let b := word input (5+n+j)
  let penalty := if a == b || a == 4 || b == 4 then 0 else word input 5 + (if a < b then 1 else 0)
  costAdd (cell costs (i-1) (j-1)) penalty
def alignCell (input : Words) (style n band i j : Nat)
    (state : Words × Words × Int × Int) : Words × Words × Int × Int :=
  let (costs,vertical,horizontal,_) := state
  let save := fun cost moves v h => (replaceAt costs (13*i+j) cost,replaceAt vertical j v,h,moves)
  if i > j+band || j > i+band then save infinity 0 infinity infinity
  else if i == 0 && j == 0 then save 0 0 infinity infinity
  else
    let openCost := word input 3
    let extension := word input 4
    let v := if style == 0 then gapMinimum openCost extension i (fun k => cell costs k j)
      else if i == 0 then infinity
      else extendMinimum openCost extension (cell costs (i-1) j) (word vertical j)
    let h := if style == 0 then gapMinimum openCost extension j (fun k => cell costs i k)
      else if j == 0 then infinity
      else extendMinimum openCost extension (cell costs i (j-1)) horizontal
    let d := if i == 0 || j == 0 then infinity else diagonalCost input costs n i j
    let best := offer style (offer style (offer style (infinity,0) d 1) v 2) h 4
    save best.1 best.2 v h
def alignment (style : Nat) (input : Words) : Option Words :=
  let n := (word input 0).toNat
  let m := (word input 1).toNat
  let band := (word input 2).toNat
  let (costs,_,_,moves) := (List.range (n+1)).foldl (fun (costs,vertical,_,moves) i =>
    (List.range (m+1)).foldl (fun state j => alignCell input style n band i j state)
      (costs,vertical,infinity,moves))
    (List.replicate 169 infinity,List.replicate 13 infinity,infinity,0)
  let cost := cell costs n m
  finish [if cost == infinity then -1 else cost,moves]

abbrev Phase := Int × Int
def splitPhase (x denominator : Int) : Phase := (x/denominator,x%denominator)
def adjustPhase (denominator : Int) (p : Phase) : Phase :=
  if p.2 < 0 then (p.1-1,p.2+denominator)
  else if p.2 ≥ denominator then (p.1+1,p.2-denominator)
  else p
def nextPhase (denominator step : Int) (p : Phase) : Phase :=
  (List.range 24).foldl (fun acc _ => adjustPhase denominator acc) (p.1,p.2+step)
def roundSigned (style : Nat) (numerator denominator : Int) : Int :=
  let magnitude := if numerator < 0 then -numerator else numerator
  let twice := 2*(magnitude%denominator)
  let increment := if (if style == 2 then twice > denominator else twice ≥ denominator) then 1 else 0
  let result := magnitude/denominator+increment
  if numerator < 0 then -result else result
def interpolate (style : Nat) (input : Words) (index : Nat) (rem denominator : Int) : Int :=
  roundSigned style ((denominator-rem)*word input (7+index)+rem*word input (8+index)) denominator
def sample (style : Nat) (input : Words) (p : Phase) : Words :=
  let last := word input 0-1
  let (value,edge) := if p.1 < 0 then (word input 7,(-1 : Int))
    else if p.1 ≥ last then (word input (7+last.toNat),if p.1 > last || p.2 != 0 then 1 else 0)
    else (interpolate style input p.1.toNat p.2 (word input 3),0)
  let lo := word input 5
  let hi := word input 6
  if value < lo then [lo,edge,-1] else if value > hi then [hi,edge,1] else [value,edge,0]
def resample (style : Nat) (input : Words) : Option Words :=
  let denominator := word input 3
  let start := word input 4
  let step := word input 2
  let (_,out) := (List.range (word input 1).toNat).foldl (fun (phase,out) i =>
    let here := if style == 0 then splitPhase (start+Int.ofNat i*step) denominator else phase
    let next := if style == 0 then phase else nextPhase denominator step phase
    (next,out++sample style input here)) (splitPhase start denominator,([] : Words))
  finish out

def entry (family style : Nat) (input : Words) : Option Words :=
  match family with
  | 0 => graph style input
  | 1 => scopes style input
  | 2 => leases style input
  | 3 => alignment style input
  | _ => resample style input

def Equivalent (valid : Words → Prop) (a b : Words → Option Words) : Prop :=
  ∀ x, valid x → ∃ o, a x = some o ∧ b x = some o
def RefutationAt (valid : Words → Prop) (a b : Words → Option Words) (x oa ob : Words) : Prop :=
  valid x ∧ a x = some oa ∧ b x = some ob ∧ oa ≠ ob

end EqualBenchSystems
