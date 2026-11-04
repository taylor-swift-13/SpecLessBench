import SystemsNative

namespace EqualBenchSystems

def between (x lo hi : Int) : Bool := lo ≤ x && x ≤ hi

def validCommand (family : Nat) (op a b c : Int) : Bool :=
  if family == 0 then
    between op 0 4 && between a 0 7 && c == 0 &&
      (if op ≤ 1 then between b 0 7 else b == 0)
  else if family == 1 then
    between op 0 4 && c == 0 &&
      (if op ≤ 2 then between a 0 7 else a == 0) &&
      (if op == 0 then between b (-1000) 1000 else b == 0)
  else
    between op 0 3 && between a 0 (if op == 3 then 4 else 7) &&
      (if op == 0 then between b (-1000) 1000 && between c 1 8 else b == 0 && c == 0)

def validFamilyB (family : Nat) (xs : Words) : Bool :=
  let q := word xs 0
  if family == 3 then
    let m := word xs 1
    between q 0 12 && between m 0 12 && between (word xs 2) 0 12 &&
      between (word xs 3) 1 10 && between (word xs 4) 0 (word xs 3) &&
      between (word xs 5) 0 10 && xs.length == 6+q.toNat+m.toNat &&
      (xs.drop 6).all (fun x => between x 0 4)
  else if family == 4 then
    between q 1 16 && between (word xs 1) 0 32 && between (word xs 2) (-24) 24 &&
      between (word xs 3) 1 16 && between (word xs 4) (-64) 128 &&
      between (word xs 5) (-512) (word xs 6) && between (word xs 6) (word xs 5) 512 &&
      xs.length == 7+q.toNat && (xs.drop 7).all (fun x => between x (-512) 512)
  else
    between q 0 64 && xs.length == 1+4*q.toNat && (List.range q.toNat).all (fun i =>
      let p := 1+4*i
      validCommand family (word xs p) (word xs (p+1)) (word xs (p+2)) (word xs (p+3)))

def valid (family : Nat) (xs : Words) : Prop := validFamilyB family xs = true

end EqualBenchSystems
