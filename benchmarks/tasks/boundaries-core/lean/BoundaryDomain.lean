import BoundaryNative
namespace SpecLessBenchBoundary
def inRange (v lo hi : Int) : Bool := lo ≤ v && v ≤ hi
def validB (domain : Nat) (xs : Words) : Bool :=
  let a := iz xs 0; let b := iz xs 1
  let n := a.toNat; let q := b.toNat
  match domain with
  | 0 => inRange a 0 64 && xs.length == 1+3*n && (List.range n).all (fun i =>
      inRange (iz xs (1+3*i)) (-1000) 1000 &&
      [iz xs (2+3*i),iz xs (3+3*i)].all (fun c => c == -1 || (0 ≤ c && c < Int.ofNat i))) &&
      (List.range n).all (fun j => ((List.range (2*n)).filter (fun k =>
        iz xs (2+3*(k/2)+k%2) == Int.ofNat j)).length ≤ 1)
  | 1 => inRange a 1 64 && inRange b 0 64 && xs.length == 2+3*q && (List.range q).all (fun i =>
      inRange (iz xs (2+3*i)) 0 1 && inRange (iz xs (3+3*i)) 0 (a-1) && inRange (iz xs (4+3*i)) 0 (a-1))
  | 2 => a == 0 && inRange b 0 64 && xs.length == 2+2*q && (List.range q).all (fun i =>
      let op := iz xs (2+2*i); let v := iz xs (3+2*i)
      inRange op 0 3 && (if op == 0 then inRange v (-1000000) 1000000 else v == 0))
  | 3 => a == 1 && inRange b 0 64 && xs.length == 2+q && (xs.drop 2).all (fun v => inRange v (-1000000) 1000000)
  | 4 => inRange a 1 64 && inRange b 0 8 && xs.length == 2+q+3*n &&
      ((xs.drop 2).take q).all (fun v => inRange v (-1000) 1000) && (List.range n).all (fun i =>
        let p := 2+q+3*i; let tag := iz xs p; let l := iz xs (p+1); let r := iz xs (p+2)
        inRange tag 0 255 && (if tag == 0 then inRange l (-1000) 1000 && r == 0
        else if tag == 1 then inRange l 0 15 && r == 0
        else if tag > 10 then inRange l (-1000) 1000 && inRange r (-1000) 1000
        else 0 ≤ l && l < Int.ofNat i && (if tag == 8 || tag == 9 then r == 0 else 0 ≤ r && r < Int.ofNat i)))
  | 5 => inRange a 0 96 && xs.length == 1+n && (xs.drop 1).all (fun v => inRange v 0 255)
  | 7 => inRange a 0 64 && inRange b 0 96 && xs.length == 2+n && (xs.drop 2).all (fun v => inRange v 0 255)
  | _ => inRange a 0 64 && xs.length == 1+n && (xs.drop 1).all (fun v => inRange v 0 255)
def familyDomain (family : Nat) (xs : Words) : Nat :=
  if family < 2 then family else if family == 2 then (if iz xs 0 == 0 then 2 else 3) else family+1
def validFamilyB (family : Nat) (xs : Words) : Bool := validB (familyDomain family xs) xs
def valid (domain : Nat) (xs : Words) : Prop := validB domain xs = true
end SpecLessBenchBoundary
