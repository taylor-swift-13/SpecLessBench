import CountSortNative
namespace SpecLessBenchCountSort
def between (x lo hi : Int) : Bool := lo ≤ x && x ≤ hi
def validB (domain : Nat) (xs : Words) : Bool :=
  let n := word xs 0
  domain == 0 && between n 0 64 && xs.length == 1+2*n.toNat &&
  (List.range n.toNat).all (fun i => between (word xs (1+2*i)) (-3) 3 && between (word xs (2+2*i)) (-1000) 1000)
def validFamilyB (family : Nat) (xs : Words) : Bool := validB family xs
def valid (domain : Nat) (xs : Words) : Prop := validB domain xs = true
end SpecLessBenchCountSort
