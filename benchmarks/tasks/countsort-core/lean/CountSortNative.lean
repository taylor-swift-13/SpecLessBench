import Lean
namespace SpecLessBenchCountSort
abbrev Words := List Int
abbrev Record := Int × Int
def getOr (xs : List α) (i : Nat) (fallback : α) := (xs[i]?).getD fallback
def word (xs : Words) (i : Nat) := getOr xs i 0
def put (xs : List α) (i : Nat) (value : α) := xs.take i ++ [value] ++ xs.drop (i+1)
def finish (xs : Words) : Option Words := some (Int.ofNat xs.length::xs)
def insertRecord (item : Record) : List Record → List Record
  | [] => [item]
  | x::xs => if item.1 < x.1 then item::x::xs else x::insertRecord item xs
def index (x : Record) : Nat := (x.1+3).toNat
def counting (xs : List Record) (reverse : Bool) : List Record :=
  let counts := xs.foldl (fun counts x => let k := index x; put counts k (getOr counts k 0+1)) (List.replicate 7 0)
  let positions := (List.range 7).map (fun k => (counts.take k).foldl (· + ·) 0)
  let (out,_) := (if reverse then xs.reverse else xs).foldl (fun (out,pos) x =>
    let k := index x; let slot := getOr pos k 0
    (put out slot x,put pos k (slot+1))) (List.replicate xs.length ((0,0) : Record),positions)
  out
def entry (_family style : Nat) (xs : Words) : Option Words :=
  let n := (word xs 0).toNat
  let items : List Record := (List.range n).map (fun i => (word xs (1+2*i),word xs (2+2*i)))
  let result := if style == 0 then items.foldl (fun acc x => insertRecord x acc) [] else counting items (style == 2)
  finish (result.flatMap (fun (k,v) => [k,v]))
def Equivalent (valid : Words → Prop) (a b : Words → Option Words) : Prop := ∀ x, valid x → ∃ o, a x=some o ∧ b x=some o
def RefutationAt (valid : Words → Prop) (a b : Words → Option Words) (x oa ob : Words) : Prop := valid x ∧ a x=some oa ∧ b x=some ob ∧ oa≠ob
end SpecLessBenchCountSort
