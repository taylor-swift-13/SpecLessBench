import Lean
namespace EqualBenchClassics
abbrev Words := List Int
abbrev Edge := Nat × Nat × Int × Nat
abbrev Record := Int × Int
def getOr (xs : List α) (i : Nat) (fallback : α) := (xs[i]?).getD fallback
def word (xs : Words) (i : Nat) := getOr xs i 0
def put (xs : List α) (i : Nat) (value : α) := xs.take i ++ [value] ++ xs.drop (i+1)
def finish (xs : Words) : Option Words := some (Int.ofNat xs.length::xs)
def edgeWeight (e : Edge) : Int := let (_,_,w,_) := e; w
def insertEdge (reverse : Bool) (item : Edge) : List Edge → List Edge
  | [] => [item]
  | e::es => if (if reverse then edgeWeight item > edgeWeight e else edgeWeight item < edgeWeight e)
    then item::e::es else e::insertEdge reverse item es
def sortEdges (reverse : Bool) (edges : List Edge) : List Edge :=
  edges.foldl (fun sorted e => insertEdge reverse e sorted) []
def root : Nat → List Nat → Nat → Option Nat
  | 0,_,_ => none
  | fuel+1,parent,x =>
    let next := getOr parent x x
    if next == x then some x else root fuel parent next
def kruskal (reverse : Bool) (n : Nat) (edges : List Edge) : Option (Int × Nat × Nat) := do
  let (_,total,components,mask) ← (sortEdges reverse edges).foldlM (fun (parent,total,components,mask) (u,v,w,id) => do
    let a ← root 9 parent u
    let b ← root 9 parent v
    if a == b then pure (parent,total,components,mask)
    else pure (put parent a b,total+w,components-1,mask+2^id))
    (List.range n,(0 : Int),n,0)
  pure (total,components,mask)
def crossing (seen : List Bool) (e : Edge) : Bool :=
  let (u,v,_,_) := e
  getOr seen u false != getOr seen v false
def bestCrossing (edges : List Edge) (seen : List Bool) : Option Edge :=
  edges.foldl (fun best e =>
    if !crossing seen e then best else
    match best with
    | none => some e
    | some old => if edgeWeight e < edgeWeight old then some e else best) none
def grow (edges : List Edge) : Nat → List Bool → Int → Nat → Option (List Bool × Int × Nat)
  | fuel,seen,total,mask =>
    match bestCrossing edges seen with
    | none => some (seen,total,mask)
    | some (u,v,w,id) =>
      match fuel with
      | 0 => none
      | fuel+1 => grow edges fuel (put (put seen u true) v true) (total+w) (mask+2^id)
def prim (n : Nat) (edges : List Edge) : Option (Int × Nat × Nat) := do
  let (_,total,components,mask) ← (List.range n).foldlM (fun (seen,total,components,mask) start => do
    if getOr seen start false then pure (seen,total,components,mask)
    else
      let (next,total,mask) ← grow edges 8 (put seen start true) total mask
      pure (next,total,components+1,mask)) (List.replicate n false,(0 : Int),0,0)
  pure (total,components,mask)
def forest (style : Nat) (xs : Words) : Option Words := do
  let mode := word xs 0
  let n := (word xs 1).toNat
  let edges := (List.range (word xs 2).toNat).map (fun i =>
    ((word xs (3+3*i)).toNat,(word xs (4+3*i)).toNat,word xs (5+3*i),i))
  let (weight,components,mask) ← if style == 1 then prim n edges else kruskal (style == 2) n edges
  finish ([weight,Int.ofNat components]++if mode == 1 then [Int.ofNat mask] else [])

def insertRecord (item : Record) : List Record → List Record
  | [] => [item]
  | x::xs => if item.1 < x.1 then item::x::xs else x::insertRecord item xs
def merge : Nat → List Record → List Record → Option (List Record)
  | _,[],ys => some ys
  | _,xs,[] => some xs
  | 0,_::_,_::_ => none
  | fuel+1,x::xs,y::ys => do
    if x.1 ≤ y.1 then pure (x::(← merge fuel xs (y::ys)))
    else pure (y::(← merge fuel (x::xs) ys))
def mergeSort : Nat → List Record → Option (List Record)
  | _,[] => some []
  | _,[x] => some [x]
  | 0,_::_::_ => none
  | fuel+1,x::y::rest => do
    let input := x::y::rest
    let half := input.length/2
    let left ← mergeSort fuel (input.take half)
    let right ← mergeSort fuel (input.drop half)
    merge 128 left right
def selectionSort : Nat → List Record → Option (List Record)
  | _,[] => some []
  | 0,_::_ => none
  | fuel+1,items => do
    let best := (List.range items.length).foldl (fun best i =>
      if (getOr items i (0,0)).1 < (getOr items best (0,0)).1 then i else best) 0
    let picked := getOr items best (0,0)
    let swapped := put items best (getOr items 0 (0,0))
    let rest ← selectionSort fuel (swapped.drop 1)
    pure (picked::rest)
def sorting (style : Nat) (xs : Words) : Option Words := do
  let items := (List.range (word xs 0).toNat).map (fun i => (word xs (1+2*i),word xs (2+2*i)))
  let sorted ← if style == 0 then some (items.foldl (fun acc item => insertRecord item acc) [])
    else if style == 1 then mergeSort 8 items else selectionSort 64 items
  finish (sorted.flatMap (fun (key,payload) => [key,payload]))
def entry (family style : Nat) (xs : Words) : Option Words :=
  if family == 0 then forest style xs else sorting style xs
def Equivalent (valid : Words → Prop) (a b : Words → Option Words) : Prop :=
  ∀ x, valid x → ∃ o, a x=some o ∧ b x=some o
def RefutationAt (valid : Words → Prop) (a b : Words → Option Words) (x oa ob : Words) : Prop :=
  valid x ∧ a x=some oa ∧ b x=some ob ∧ oa≠ob
end EqualBenchClassics
