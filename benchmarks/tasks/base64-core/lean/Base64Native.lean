import Lean
namespace EqualBenchBase64
abbrev Words := List Int
def get (xs : Words) (i : Nat) : Int := (xs[i]?).getD 0
def alphabet (x : Nat) : Int :=
  if x < 26 then Int.ofNat (65+x) else if x < 52 then Int.ofNat (97+x-26)
  else if x < 62 then Int.ofNat (48+x-52) else if x == 62 then 43 else 47
def blocks : Nat → List Nat → Option Words
  | _,[] => some []
  | 0,_::_ => none
  | fuel+1,a::tail => do
    let b := tail.headD 0
    let c := (tail.drop 1).headD 0
    let rest ← blocks fuel (tail.drop 2)
    pure ([alphabet (a/4),alphabet ((a%4)*16+b/16),
      if tail.isEmpty then 61 else alphabet ((b%16)*4+c/64),
      if tail.length < 2 then 61 else alphabet (c%64)] ++ rest)
def emitSextets : Nat → Nat → Nat → Words → Nat × Nat × Words
  | 0,buffer,bits,out => (buffer,bits,out)
  | fuel+1,buffer,bits,out =>
    if bits < 6 then (buffer,bits,out) else
    let remaining := bits-6
    let divisor := 2^remaining
    emitSextets fuel (buffer%divisor) remaining (out++[alphabet (buffer/divisor)])
def stream (style : Nat) (bytes : List Nat) : Words :=
  let (buffer,bits,out) := bytes.foldl (fun (buffer,bits,out) b =>
    emitSextets 3 (buffer*256+b) (bits+8) out) (0,0,([] : Words))
  let out := if bits == 0 then out else out++[alphabet (buffer*2^(6-bits))]
  let padding := (4-out.length%4)%4
  out ++ List.replicate (if style == 2 then min padding 1 else padding) 61
def entry (_family style : Nat) (xs : Words) : Option Words := do
  let bytes := ((xs.drop 1).take (get xs 0).toNat).map Int.toNat
  let out ← if style == 0 then blocks 64 bytes else some (stream style bytes)
  pure (Int.ofNat out.length::out)
def Equivalent (valid : Words → Prop) (a b : Words → Option Words) : Prop :=
  ∀ x, valid x → ∃ o, a x=some o ∧ b x=some o
def RefutationAt (valid : Words → Prop) (a b : Words → Option Words) (x oa ob : Words) : Prop :=
  valid x ∧ a x=some oa ∧ b x=some ob ∧ oa≠ob
end EqualBenchBase64
