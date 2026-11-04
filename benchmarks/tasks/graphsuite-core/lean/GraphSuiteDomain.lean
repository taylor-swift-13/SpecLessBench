import GraphSuiteNative
namespace SpecLessBenchGraphSuite
def between (x lo hi : Int) : Bool := lo ≤ x && x ≤ hi
def validB (domain : Nat) (xs : Words) : Bool :=
  if domain == 0 || domain == 1 then
    let n := word xs 0
    between n 1 8 && xs.length == 1+n.toNat*n.toNat &&
      (List.range (n.toNat*n.toNat)).all (fun p =>
        let v := word xs (1+p)
        if domain == 1 then between v 0 1
        else if p/n.toNat == p%n.toNat then v == -1 else between v (-1) 100)
  else if domain == 2 then
    let n := word xs 0; let m := word xs 1
    between n 0 48 && between m 0 16 && xs.length == 2+n.toNat+m.toNat &&
      (List.range (n.toNat+m.toNat)).all (fun i => between (word xs (2+i)) 0 3)
  else false
def validFamilyB (family : Nat) (xs : Words) : Bool := validB family xs
def valid (domain : Nat) (xs : Words) : Prop := validB domain xs = true
end SpecLessBenchGraphSuite
