import Lean
namespace EqualBenchBasic
abbrev Words := List Int
def iz (xs : Words) (i : Nat) : Int := (xs[i]?).getD 0
def put (xs : Words) (i : Nat) (v : Int) := xs.take i ++ [v] ++ xs.drop (i+1)
def finish (xs : Words) : Words := Int.ofNat xs.length :: xs
def factorialRec : Nat → Int | 0 => 1 | n+1 => Int.ofNat (n+1) * factorialRec n
def factorialAcc (mutant : Bool) : Nat → Int → Int
  | 0,a => a
  | n+1,a => factorialAcc mutant n (a*Int.ofNat (if mutant then n else n+1))
def reverseRec : Words → Words | [] => [] | x::xs => reverseRec xs ++ [x]
def reverseAcc : Words → Words → Words | [],a => a | x::xs,a => reverseAcc xs (x::a)
def sumRec : Words → Int | [] => 0 | x::xs => x+sumRec xs
def sumAcc : Words → Int → Int | [],a => a | x::xs,a => sumAcc xs (a+x)
def matrix (style : Nat) (xs : Words) : Words :=
  let r := (iz xs 0).toNat; let k := (iz xs 1).toNat; let c := (iz xs 2).toNat
  if style == 1 then
    (List.range r).foldl (fun out i =>
      (List.range k).foldl (fun out t => (List.range c).foldl (fun out j =>
        put out (i*c+j) (iz out (i*c+j)+iz xs (3+i*k+t)*iz xs (3+r*k+t*c+j))) out) out)
      (List.replicate (r*c) 0)
  else (List.range (r*c)).map (fun pos =>
    let i := pos/c; let j := pos%c
    (List.range k).foldl (fun a t => a+iz xs (3+i*k+t)*iz xs (3+r*k+(if style == 2 then j*k+t else t*c+j))) 0)
def matchAt (text pat : Words) (pos : Nat) : Bool :=
  (List.range pat.length).all (fun j => iz text (pos+j) == iz pat j)
def naiveSearch (text pat : Words) : Int :=
  if pat.length > text.length then -1
  else match ((List.range (text.length-pat.length+1)).find? (matchAt text pat)) with
    | none => -1 | some i => Int.ofNat i
def fallback (mutant : Bool) (pat : Words) (table : List Nat) (b : Int) : Nat → Nat → Option Nat
  | 0,_ => none
  | fuel+1,j =>
    if j > 0 && b != iz pat j then
      fallback mutant pat table b fuel (if mutant then 0 else (table[j-1]?).getD 0)
    else some j
def prefixTable (pat : Words) : Option (List Nat) :=
  (List.range (pat.length-1)).foldlM (fun tab z => do
    let i := z+1
    let j ← fallback false pat tab (iz pat i) 34 ((tab[i-1]?).getD 0)
    pure (tab ++ [if iz pat i == iz pat j then j+1 else j])) [0]
def kmpLoop (mutant : Bool) (text pat : Words) (tab : List Nat) : Nat → Nat → Nat → Option Int
  | 0,_,_ => some (-1)
  | n+1,i,j => do
    let j' ← fallback mutant pat tab (iz text i) 34 j
    let next := if iz text i == iz pat j' then j'+1 else j'
    if next == pat.length then pure (Int.ofNat (i+1)-Int.ofNat pat.length)
    else kmpLoop mutant text pat tab n (i+1) next
def kmp (mutant : Bool) (text pat : Words) : Option Int := do
  if pat.isEmpty then pure 0 else
    let tab ← prefixTable pat
    kmpLoop mutant text pat tab text.length 0 0
def queue (style : Nat) (xs : Words) : Words :=
  let (_,_,out) := (List.range (iz xs 0).toNat).foldl (fun (front,rear,out) i =>
    let op := iz xs (1+2*i); let v := iz xs (2+2*i)
    if op == 0 then
      if style == 0 then (front++[v],rear,out++[0,0]) else (front,v::rear,out++[0,0])
    else
      let (f,r) := if style != 0 && front.isEmpty then
        (reverseRec rear,if style == 2 then rear else []) else (front,rear)
      match f with
      | [] => (f,r,out++[op,0,0])
      | a::rest => (if op == 1 then rest else f,r,out++[op,1,a]))
    (([] : Words),([] : Words),([] : Words))
  out
def entry (family style : Nat) (xs : Words) : Option Words :=
  match family with
  | 0 => some (finish [if style == 0 then factorialRec (iz xs 0).toNat else factorialAcc (style == 2) (iz xs 0).toNat 1])
  | 1 => let data := (xs.drop 1).take (iz xs 0).toNat
         some (finish (if style == 0 then reverseRec data else reverseAcc data (if style == 2 then [0] else [])))
  | 2 => let data := (xs.drop 1).take (iz xs 0).toNat
         some (finish [if style == 0 then sumRec data else sumAcc (if style == 2 then data.take (data.length-1) else data) 0])
  | 3 => some (finish (matrix style xs))
  | 4 => do
      let n := (iz xs 0).toNat; let m := (iz xs 1).toNat
      let text := (xs.drop 2).take n; let pat := (xs.drop (2+n)).take m
      let result ← if style == 0 then some (naiveSearch text pat) else kmp (style == 2) text pat
      pure (finish [result])
  | _ => some (finish (queue style xs))
def Equivalent (valid : Words → Prop) (a b : Words → Option Words) : Prop :=
  ∀ x, valid x → ∃ o, a x = some o ∧ b x = some o
def Counterexample (valid : Words → Prop) (a b : Words → Option Words) : Prop :=
  ∃ x oa ob, valid x ∧ a x = some oa ∧ b x = some ob ∧ oa ≠ ob
def Certificate (valid : Words → Prop) (a b : Words → Option Words) : Prop := Equivalent valid a b ∨ Counterexample valid a b
end EqualBenchBasic
def basicRunnerMain : IO Unit := do
  let stdin ← IO.getStdin; let stdout ← IO.getStdout
  repeat
    let line ← stdin.getLine
    if line.isEmpty then break
    let fields := ((line.trimAscii.toString.splitOn " ").filter (· != "")).map (fun s => s.toInt?.getD 0)
    match EqualBenchBasic.entry (EqualBenchBasic.iz fields 0).toNat (EqualBenchBasic.iz fields 1).toNat (fields.drop 2) with
    | none => stdout.putStrLn "FAIL"
    | some xs => stdout.putStrLn (String.intercalate " " (xs.map toString))
