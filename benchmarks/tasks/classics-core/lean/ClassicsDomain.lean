import ClassicsNative
namespace EqualBenchClassics
def between (x lo hi : Int) : Bool := lo ≤ x && x ≤ hi
def validB (domain : Nat) (xs : Words) : Bool :=
  if domain == 2 then
    let n := word xs 0
    between n 0 64 && xs.length == 1+2*n.toNat && (List.range n.toNat).all (fun i =>
      between (word xs (1+2*i)) (-1000) 1000 && between (word xs (2+2*i)) (-1000) 1000)
  else
    let mode := word xs 0; let n := word xs 1; let m := word xs 2
    mode == Int.ofNat domain && between n 1 8 && between m 0 28 && xs.length == 3+3*m.toNat &&
    (List.range m.toNat).all (fun i =>
      let u := word xs (3+3*i); let v := word xs (4+3*i); let w := word xs (5+3*i)
      0 ≤ u && u < v && v < n && between w (-1000) 1000 &&
      (List.range i).all (fun j =>
        (u != word xs (3+3*j) || v != word xs (4+3*j)) &&
        (domain != 1 || w != word xs (5+3*j))))
def validFamilyB (family : Nat) (xs : Words) : Bool :=
  if family == 0 then validB (word xs 0).toNat xs else validB 2 xs
def valid (domain : Nat) (xs : Words) : Prop := validB domain xs = true
end EqualBenchClassics
