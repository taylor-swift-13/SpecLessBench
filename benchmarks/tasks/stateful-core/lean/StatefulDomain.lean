import StatefulNative
namespace EqualBenchStateful
def inRange (v lo hi : Int) : Bool := lo ≤ v && v ≤ hi
def validB (family : Nat) (xs : Words) : Bool :=
  let a := iz xs 0; let b := iz xs 1
  let n := a.toNat; let q := b.toNat
  match family with
  | 0 => inRange a 0 64 && xs.length == 1+10*n && (List.range n).all (fun i =>
      let p := 1+10*i; let op := iz xs p; let len := iz xs (p+1)
      inRange op 0 2 && inRange len 0 8 && (op == 0 || len == 0) && (List.range 8).all (fun j =>
        if j < len.toNat then inRange (iz xs (p+2+j)) 0 255 else iz xs (p+2+j) == 0))
  | 1 => inRange a 0 64 && xs.length == 1+3*n && (List.range n).all (fun i =>
      let op := iz xs (1+3*i); let key := iz xs (2+3*i); let v := iz xs (3+3*i)
      inRange op 0 5 && (if op < 3 then inRange key 0 7 && (if op == 0 then inRange v (-1000) 1000 else v == 0) else key == 0 && v == 0))
  | _ => inRange a 0 8 && inRange b 0 64 && xs.length == 2+3*q && (List.range q).all (fun i =>
      let op := iz xs (2+3*i); let key := iz xs (3+3*i); let v := iz xs (4+3*i)
      inRange op 0 4 && inRange key 0 (if op == 4 then 8 else 15) && (if op == 0 then inRange v (-1000) 1000 else v == 0))
def validFamilyB := validB
def valid (family : Nat) (xs : Words) : Prop := validB family xs = true
end EqualBenchStateful
