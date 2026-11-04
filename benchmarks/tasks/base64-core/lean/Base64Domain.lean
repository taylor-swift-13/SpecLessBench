import Base64Native
namespace EqualBenchBase64
def validFamilyB (_family : Nat) (xs : Words) : Bool :=
  let n := get xs 0
  0 ≤ n && n ≤ 64 && xs.length == 1+n.toNat &&
  (xs.drop 1).all (fun b => 0 ≤ b && b ≤ 255)
def valid (family : Nat) (xs : Words) : Prop := validFamilyB family xs = true
end EqualBenchBase64
