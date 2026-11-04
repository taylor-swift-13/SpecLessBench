import BasicNative
namespace SpecLessBenchBasic
def inRange (v lo hi : Int) : Bool := lo ≤ v && v ≤ hi
def validB (family : Nat) (xs : Words) : Bool :=
  let a := iz xs 0; let b := iz xs 1; let c := iz xs 2
  let n := a.toNat; let m := b.toNat; let z := c.toNat
  match family with
  | 0 => xs.length == 1 && inRange a 0 12
  | 1 | 2 => inRange a 0 64 && xs.length == 1+n && (xs.drop 1).all (fun v => inRange v (-1000000) 1000000)
  | 3 => inRange a 0 6 && inRange b 0 6 && inRange c 0 6 && xs.length == 3+n*m+m*z &&
      (xs.drop 3).all (fun v => inRange v (-1000) 1000)
  | 4 => inRange a 0 64 && inRange b 0 32 && xs.length == 2+n+m && (xs.drop 2).all (fun v => inRange v 0 255)
  | _ => inRange a 0 64 && xs.length == 1+2*n && (List.range n).all (fun i =>
      let op := iz xs (1+2*i); let v := iz xs (2+2*i)
      inRange op 0 2 && (if op == 0 then inRange v (-1000000) 1000000 else v == 0))
def valid (family : Nat) (xs : Words) : Prop := validB family xs = true
end SpecLessBenchBasic
