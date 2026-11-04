import Lean
namespace SpecLessBenchGraphSuite
abbrev Words := List Int
def getOr (xs : List α) (i : Nat) (fallback : α) := (xs[i]?).getD fallback
def word (xs : Words) (i : Nat) := getOr xs i 0
def put (xs : List α) (i : Nat) (value : α) := xs.take i ++ [value] ++ xs.drop (i+1)
def finish (xs : Words) : Option Words := some (Int.ofNat xs.length::xs)
def lim : Int := 1000000
def initDist (n : Nat) (xs : Words) : Words := (List.range (n*n)).map fun p =>
  let v := word xs (1+p)
  if p/n == p%n then 0 else if v < 0 then lim else v
def floyd (n : Nat) (xs : Words) : Words :=
  (List.range n).foldl (fun d k => (List.range n).foldl (fun d i =>
    (List.range n).foldl (fun d j =>
      let x := word d (i*n+k); let y := word d (k*n+j); let z := word d (i*n+j)
      if x != lim && y != lim && x+y < z then put d (i*n+j) (x+y) else d) d) d) (initDist n xs)
def dijkstra (n : Nat) (xs : Words) (mutant : Bool) : Words :=
  (List.range n).flatMap fun source =>
    let start := put (List.replicate n lim) source 0
    let (d,_) := (List.range n).foldl (fun (d,seen) _ =>
      let best := (List.range n).foldl (fun best j =>
        if getOr seen j false || word d j == lim then best
        else match best with
          | none => some j
          | some b => if word d j < word d b then some j else best) (none : Option Nat)
      match best with
      | none => (d,seen)
      | some u =>
        let d := (List.range n).foldl (fun d j =>
          let w := word xs (1+u*n+j)
          if w >= 0 && !(mutant && w == 0) && word d u+w < word d j
          then put d j (word d u+w) else d) d
        (d,put seen u true)) (start,List.replicate n false)
    d
def apsp (style : Nat) (xs : Words) : Option Words :=
  let n := (word xs 0).toNat
  let d := if style == 0 then floyd n xs else dijkstra n xs (style == 2)
  finish (d.map fun v => if v == lim then -1 else v)

structure TS where
  idx : List Int
  low : List Int
  stack : List Nat
  ons : List Bool
  comp : List Int
  clock : Int
  count : Int
def tarjanPop : Nat → Nat → TS → Option TS
  | 0,_,_ => none
  | fuel+1,v,s => match s.stack with
    | [] => none
    | x::rest =>
      let s := {s with stack := rest, ons := put s.ons x false, comp := put s.comp x s.count}
      if x == v then some {s with count := s.count+1} else tarjanPop fuel v s
def tarjanVisit (n : Nat) (xs : Words) : Nat → Nat → TS → Option TS
  | 0,_,_ => none
  | fuel+1,v,s => do
    let s := {s with idx := put s.idx v s.clock, low := put s.low v s.clock, stack := v::s.stack, ons := put s.ons v true, clock := s.clock+1}
    let s ← (List.range n).foldlM (fun s w => do
      if word xs (1+v*n+w) == 0 then pure s
      else if word s.idx w < 0 then
        let s ← tarjanVisit n xs fuel w s
        pure {s with low := put s.low v (min (word s.low v) (word s.low w))}
      else if getOr s.ons w false then
        pure {s with low := put s.low v (min (word s.low v) (word s.idx w))}
      else pure s) s
    if word s.low v == word s.idx v then tarjanPop 9 v s else pure s
def tarjan (n : Nat) (xs : Words) : Option Words := do
  let start : TS := ⟨List.replicate n (-1),List.replicate n 0,[],List.replicate n false,List.replicate n (-1),0,0⟩
  let s ← (List.range n).foldlM (fun s v =>
    if word s.idx v < 0 then tarjanVisit n xs 9 v s else some s) start
  pure s.comp
def firstVisit (n : Nat) (xs : Words) : Nat → Nat → List Bool → List Nat → Option (List Bool × List Nat)
  | 0,_,_,_ => none
  | fuel+1,v,seen,order => do
    let (seen,order) ← (List.range n).foldlM (fun (seen,order) w =>
      if word xs (1+v*n+w) != 0 && !(getOr seen w false)
      then firstVisit n xs fuel w seen order else some (seen,order)) (put seen v true,order)
    pure (seen,v::order)
def secondVisit (n : Nat) (xs : Words) (mutant : Bool) : Nat → Nat → Int → Words → Option Words
  | 0,_,_,_ => none
  | fuel+1,v,c,comp =>
    (List.range n).foldlM (fun comp w =>
      let p := if mutant then v*n+w else w*n+v
      if word xs (1+p) != 0 && word comp w < 0
      then secondVisit n xs mutant fuel w c comp else some comp) (put comp v c)
def kosaraju (n : Nat) (xs : Words) (mutant : Bool) : Option Words := do
  let (_,order) ← (List.range n).foldlM (fun (seen,order) v =>
    if getOr seen v false then some (seen,order) else firstVisit n xs 9 v seen order)
    (List.replicate n false,[])
  let (comp,_) ← order.foldlM (fun (comp,c) v => do
    if word comp v >= 0 then pure (comp,c)
    else let comp ← secondVisit n xs mutant 9 v c comp; pure (comp,c+1))
    (List.replicate n (-1),(0 : Int))
  pure comp
def scc (style : Nat) (xs : Words) : Option Words := do
  let n := (word xs 0).toNat
  let comp ← if style == 0 then tarjan n xs else kosaraju n xs (style == 2)
  finish ((List.range n).flatMap fun i => (List.range n).map fun j => if word comp i == word comp j then 1 else 0)
def brute (text pattern : Words) : Int :=
  if pattern.length > text.length then -1 else
    ((List.range (text.length-pattern.length+1)).foldl (fun result i =>
      if result == -1 && (text.drop i).take pattern.length == pattern then Int.ofNat i else result) (-1))
def bmLoop (text pattern : Words) (mutant : Bool) : Nat → Nat → Int
  | 0,_ => -1
  | fuel+1,i =>
    if i+pattern.length > text.length then -1 else
      let mismatch := (List.range pattern.length).reverse.find? (fun j => word text (i+j) != word pattern j)
      match mismatch with
      | none => Int.ofNat i
      | some j =>
        let right := (List.range pattern.length).foldl (fun r k => if word pattern k == word text (i+j) then Int.ofNat k else r) (-1)
        let skip := if mutant then pattern.length else (max 1 (Int.ofNat j-right)).toNat
        bmLoop text pattern mutant fuel (i+skip)
def search (style : Nat) (xs : Words) : Option Words :=
  let n := (word xs 0).toNat; let m := (word xs 1).toNat
  let text := (xs.drop 2).take n; let pattern := (xs.drop (2+n)).take m
  finish [if style == 0 then brute text pattern else if m == 0 then 0 else bmLoop text pattern (style == 2) 49 0]
def entry (family style : Nat) (xs : Words) : Option Words :=
  if family == 0 then apsp style xs else if family == 1 then scc style xs else search style xs
def Equivalent (valid : Words → Prop) (a b : Words → Option Words) : Prop := ∀ x, valid x → ∃ o, a x=some o ∧ b x=some o
def RefutationAt (valid : Words → Prop) (a b : Words → Option Words) (x oa ob : Words) : Prop := valid x ∧ a x=some oa ∧ b x=some ob ∧ oa≠ob
end SpecLessBenchGraphSuite
