import Lean
namespace EqualBenchBoundary
abbrev Words := List Int
def getOr (xs : List α) (i : Nat) (fallback : α) := (xs[i]?).getD fallback
def iz (xs : Words) (i : Nat) : Int := getOr xs i 0
def put (xs : List α) (i : Nat) (v : α) := xs.take i ++ [v] ++ xs.drop (i+1)
def finish (xs : Words) : Words := Int.ofNat xs.length :: xs
abbrev Node := Int × Int × Int
def nodeAt (xs : List Node) (i : Nat) := getOr xs i (0,-1,-1)
def mirrorRec (mutant : Bool) : Nat → List Node → Int → Option (List Node)
  | 0,ns,id => if id < 0 then some ns else none
  | fuel+1,ns,id =>
    if id < 0 then some ns else do
      let (v,l,r) := nodeAt ns id.toNat
      let first ← mirrorRec mutant fuel (put ns id.toNat (v,r,l)) r
      if mutant then pure first else mirrorRec mutant fuel first l
def mirrorStack : Nat → List Node → List Int → Option (List Node)
  | _,ns,[] => some ns
  | 0,_,_ => none
  | fuel+1,ns,id::todo =>
    if id < 0 then mirrorStack fuel ns todo else
    let (v,l,r) := nodeAt ns id.toNat
    mirrorStack fuel (put ns id.toNat (v,r,l)) (l::r::todo)
def projectTree : Nat → List Node → Int → Option (Nat × Words)
  | 0,_,id => if id < 0 then some (0,[-1]) else none
  | fuel+1,ns,id =>
    if id < 0 then some (0,[-1]) else do
      let (v,l,r) := nodeAt ns id.toNat
      let (lh,lv) ← projectTree fuel ns l
      let (rh,rv) ← projectTree fuel ns r
      pure (max lh rh+1,[id,v]++lv++rv)
def tree (style : Nat) (xs : Words) : Option Words := do
  let n := (iz xs 0).toNat
  let ns := (List.range n).map (fun i => (iz xs (1+3*i),iz xs (2+3*i),iz xs (3+3*i)))
  let root := Int.ofNat n-1
  let result ← if style == 1 then mirrorStack 256 ns [root] else mirrorRec (style == 2) 64 ns root
  let (height,projection) ← projectTree 64 result root
  pure (finish (Int.ofNat height::projection))

def findUF (style : Nat) : Nat → Words → Nat → Option (Nat × Words)
  | 0,_,_ => none
  | fuel+1,p,x =>
    let parent := (iz p x).toNat
    if style == 2 then some (parent,p)
    else if parent == x then some (x,p)
    else if style == 1 then
      let grand := (iz p parent).toNat
      findUF style fuel (put p x (Int.ofNat grand)) grand
    else do
      let (r,changed) ← findUF style fuel p parent
      pure (r,put changed x (Int.ofNat r))
def unionfind (style : Nat) (xs : Words) : Option Words := do
  let n := (iz xs 0).toNat; let q := (iz xs 1).toNat
  let (_,_,out) ← (List.range q).foldlM (fun (p,r,out) i => do
    let op := iz xs (2+3*i); let a := (iz xs (3+3*i)).toNat; let b := (iz xs (4+3*i)).toNat
    let (x,p') ← findUF style 128 p a
    let (y,p'') ← findUF style 128 p' b
    if op == 1 then pure (p'',r,out++[1,if x == y then 1 else 0])
    else if x == y then pure (p'',r,out++[0,0])
    else if iz r x > iz r y then pure (put p'' y (Int.ofNat x),r,out++[0,0])
    else pure (put p'' x (Int.ofNat y),if iz r x == iz r y then put r y (iz r y+1) else r,out++[0,0]))
    ((List.range n).map Int.ofNat,List.replicate n 0,([] : Words))
  pure (finish out)

def sortedPush (v : Int) : Words → Words
  | [] => [v]
  | x::xs => if v > x then v::x::xs else x::sortedPush v xs
def siftUp : Nat → Words → Nat → Option Words
  | 0,_,_ => none
  | fuel+1,q,i =>
    if i == 0 then some q else
    let p := (i-1)/2
    if iz q p ≥ iz q i then some q else siftUp fuel (put (put q p (iz q i)) i (iz q p)) p
def siftDown (mutant : Bool) : Nat → Words → Nat → Option Words
  | 0,_,_ => none
  | fuel+1,q,i =>
    let l := 2*i+1
    if l ≥ q.length then some q else
    let child := if !mutant && l+1 < q.length && iz q (l+1) > iz q l then l+1 else l
    if iz q i ≥ iz q child then some q else siftDown mutant fuel (put (put q i (iz q child)) child (iz q i)) child
def pqPush (style : Nat) (q : Words) (v : Int) : Option Words :=
  if style == 1 then some (sortedPush v q) else siftUp 64 (q++[v]) q.length
def pqPop (style : Nat) (q : Words) : Option (Int × Words) := do
  if q.length ≤ 1 then pure (iz q 0,[])
  else if style == 1 then pure (iz q 0,q.drop 1)
  else
    let result ← siftDown (style == 2) 64 (put (q.take (q.length-1)) 0 (iz q (q.length-1))) 0
    pure (iz q 0,result)
def pqDrain (style : Nat) : Nat → Words → Words → Option Words
  | 0,q,out => if q.isEmpty then some out else none
  | fuel+1,q,out => if q.isEmpty then some out else do
      let (v,rest) ← pqPop style q
      pqDrain style fuel rest (out++[v])
def priority (style : Nat) (xs : Words) : Option Words := do
  let n := (iz xs 1).toNat
  if iz xs 0 == 1 then
    let q ← (List.range n).foldlM (fun q i => pqPush style q (iz xs (2+i))) []
    let out ← pqDrain style 65 q []
    pure (finish out)
  else
    let (_,out) ← (List.range n).foldlM (fun (q,out) i => do
      let op := iz xs (2+2*i); let v := iz xs (3+2*i)
      if op == 0 then
        let next ← pqPush style q v
        pure (next,out++[0,0])
      else if op == 3 then pure (q,out++[3,if q.isEmpty then 1 else 0])
      else if q.isEmpty then pure (q,out++[op,0,0])
      else if op == 2 then pure (q,out++[2,1,iz q 0])
      else
        let (value,next) ← pqPop style q
        pure (next,out++[1,1,value])) (([] : Words),([] : Words))
    pure (finish out)

structure Result where
  code : Int
  error : Int
  value : Int
def missing : Result := ⟨-1,-1,0⟩
def ok (v : Int) : Result := ⟨0,-1,v⟩
def failure (c : Int) (i : Nat) : Result := ⟨c,Int.ofNat i,0⟩
def expr (xs : Words) (i : Nat) : Node :=
  let p := 2+(iz xs 1).toNat+3*i
  (iz xs p,iz xs (p+1),iz xs (p+2))
def leaf (xs : Words) (i : Nat) : Option Result :=
  let (tag,a,_) := expr xs i
  if tag == 0 then some (ok a)
  else if tag == 1 then some (if a ≥ iz xs 1 then failure 1 i else ok (iz xs (2+a.toNat)))
  else if tag > 10 then some (failure 4 i) else none
def quotient (a b : Int) : Int :=
  let mag := Int.ofNat (a.natAbs/b.natAbs)
  if a < 0 then (if b < 0 then mag else -mag) else (if b < 0 then -mag else mag)
def combine (mutant : Bool) (xs : Words) (i : Nat) (cache : List Result) : Result :=
  let (tag,a,b) := expr xs i
  let l := getOr cache a.toNat missing; let r := getOr cache b.toNat missing
  if l.code != 0 then l
  else if mutant && (tag == 6 || tag == 7) && r.code != 0 then r
  else if tag == 6 && l.value == 0 then ok 0
  else if tag == 7 && l.value != 0 then ok 1
  else if tag != 8 && tag != 9 && r.code != 0 then r
  else if tag == 10 && r.value == 0 then failure 3 i
  else
    let v := if tag == 2 then l.value+r.value else if tag == 3 then l.value-r.value
      else if tag == 4 then (if l.value < r.value then 1 else 0)
      else if tag == 5 then (if l.value == r.value then 1 else 0)
      else if tag == 6 then (if l.value != 0 && r.value != 0 then 1 else 0)
      else if tag == 7 then (if l.value != 0 || r.value != 0 then 1 else 0)
      else if tag == 8 then -l.value else if tag == 9 then (if l.value == 0 then 1 else 0)
      else quotient l.value r.value
    if v < -32768 || v > 32767 then failure 2 i else ok v
def evalRec (xs : Words) : Nat → Nat → List Result → Option (List Result)
  | 0,i,cache => if (getOr cache i missing).code ≥ 0 then some cache else none
  | fuel+1,i,cache =>
    if (getOr cache i missing).code ≥ 0 then some cache
    else match leaf xs i with
    | some value => some (put cache i value)
    | none => do
      let (tag,a,b) := expr xs i
      let first ← evalRec xs fuel a.toNat cache
      let l := getOr first a.toNat missing
      let skip := l.code != 0 || tag == 8 || tag == 9 || (tag == 6 && l.value == 0) || (tag == 7 && l.value != 0)
      let second ← if skip then some first else evalRec xs fuel b.toNat first
      pure (put second i (combine false xs i second))
def evaluator (style : Nat) (xs : Words) : Option Words := do
  let n := (iz xs 0).toNat
  let initial := List.replicate n missing
  let cache ← if style == 0 then evalRec xs 64 (n-1) initial
    else some ((List.range n).foldl (fun cache i =>
      put cache i ((leaf xs i).getD (combine (style == 2) xs i cache))) initial)
  let result := getOr cache (n-1) missing
  pure (finish [result.code,result.error,result.value])

abbrev ParseError := Int × Nat
def xorBytes (xs : Words) : Int := Int.ofNat (xs.foldl (fun acc b => Nat.xor acc b.toNat) 0)
def tlvRecord (mutant : Bool) (src : Words) (start : Nat) : Except ParseError (Nat × Words) := do
  if src.length < 3 then throw (1,start)
  let tag := iz src 0; let len := ((iz src 1)+256*(iz src 2)).toNat
  if tag < 1 || tag > 3 then throw (2,start)
  if len > 32 then throw (3,start)
  if src.length < len+4 then throw (4,start)
  if (tag == 1 && len != 2) || (tag == 3 && len != 1) then throw (5,start)
  if xorBytes (src.take (3+len)) != iz src (3+len) then throw (7,start+3+len)
  if tag == 3 && iz src 3 > 1 then throw (6,start+3)
  let out := if tag == 1 then [tag,if mutant then 256*iz src 3+iz src 4 else iz src 3+256*iz src 4]
    else if tag == 3 then [tag,iz src 3] else [tag,Int.ofNat len]++(src.drop 3).take len
  pure (len+4,out)
def tlvSuffix (mutant : Bool) : Nat → Words → Nat → Nat → Words → Option Words
  | 0,src,p,count,out => if src.isEmpty then some (finish ([0,Int.ofNat p,Int.ofNat count]++out)) else none
  | fuel+1,src,p,count,out =>
    if src.isEmpty then some (finish ([0,Int.ofNat p,Int.ofNat count]++out)) else
    match tlvRecord mutant src p with
    | .error (code,offset) => some (finish ([code,Int.ofNat offset,Int.ofNat count]++out))
    | .ok (used,bytes) => tlvSuffix mutant fuel (src.drop used) (p+used) (count+1) (out++bytes)
def tlvIndexed (mutant : Bool) (data : Words) : Nat → Nat → Nat → Words → Option Words
  | 0,p,count,out => if p == data.length then some (finish ([0,Int.ofNat p,Int.ofNat count]++out)) else none
  | fuel+1,p,count,out =>
    if p == data.length then some (finish ([0,Int.ofNat p,Int.ofNat count]++out)) else
    match tlvRecord mutant (data.drop p) p with
    | .error (code,offset) => some (finish ([code,Int.ofNat offset,Int.ofNat count]++out))
    | .ok (used,bytes) => tlvIndexed mutant data fuel (p+used) (count+1) (out++bytes)
def tlv (style : Nat) (xs : Words) :=
  let data := (xs.drop 1).take (iz xs 0).toNat
  if style == 1 then tlvSuffix false 128 data 0 0 [] else tlvIndexed (style == 2) data 128 0 0 []

structure QuoteState where
  mode : Nat := 0
  opening : Nat := 0
  escaping : Bool := false
  slash : Nat := 0
  active : Bool := false
  current : Words := []
  tokens : List Words := []
  code : Int := 0
  offset : Nat := 0
def appendChar (s : QuoteState) (c : Int) := {s with current := s.current++[c], active := true}
def commitToken (s : QuoteState) := {s with tokens := if s.active then s.tokens++[s.current] else s.tokens, current := [], active := false}
def quoteStep (mutant : Bool) (s : QuoteState) (c : Int) (p : Nat) : QuoteState :=
  if s.code != 0 then s else if c == 0 then {s with code := 3, offset := p}
  else if s.escaping then {(appendChar s c) with escaping := false}
  else if s.mode == 1 then if c == 39 then {s with mode := 0} else appendChar s c
  else if c == 92 then {s with escaping := true, slash := p}
  else if s.mode == 2 then if c == 34 then {s with mode := 0} else appendChar s c
  else if c == 9 || c == 32 then commitToken s
  else if c == 39 || c == 34 then {s with mode := if c == 39 then 1 else 2, opening := p, active := if mutant then s.active else true}
  else appendChar s c
def ordinary (c : Int) : Bool := c != 0 && c != 9 && c != 32 && c != 34 && c != 39 && c != 92
def quoteSpans : Nat → Words → Nat → QuoteState → Option QuoteState
  | _,[],_,s => some s
  | 0,_,_,_ => none
  | fuel+1,src,p,s =>
    if s.code != 0 then some s else
    if s.mode == 0 && !s.escaping && ordinary (iz src 0) then
      let span := src.takeWhile ordinary
      quoteSpans fuel (src.drop span.length) (p+span.length) {s with current := s.current++span,active := true}
    else quoteSpans fuel (src.drop 1) (p+1) (quoteStep false s (iz src 0) p)
def quotes (style : Nat) (xs : Words) : Option Words := do
  let data := (xs.drop 1).take (iz xs 0).toNat
  let s ← if style == 1 then quoteSpans 128 data 0 {} else some ((data.zipIdx).foldl (fun s (c,p) => quoteStep (style == 2) s c p) {})
  let final := if s.code != 0 then s else if s.escaping then {s with code := 1,offset := s.slash}
    else if s.mode != 0 then {s with code := 2,offset := s.opening} else {(commitToken s) with offset := data.length}
  pure (finish ([final.code,Int.ofNat final.offset,Int.ofNat final.tokens.length]++
    final.tokens.flatMap (fun token => Int.ofNat token.length::token)))

def packBlock (mutant : Bool) (src : Words) (start cap produced : Nat) : Except ParseError (Nat × Words) := do
  let control := (iz src 0).toNat
  if control == 128 then pure (1,[]) else
    let count := if control < 128 then control+1 else 257-control-(if mutant then 1 else 0)
    let used := if control < 128 then count+1 else 2
    if src.length < used then throw (1,start)
    if produced+count > cap then throw (2,start)
    pure (used,if control < 128 then (src.drop 1).take count else List.replicate count (iz src 1))
def packSuffix (mutant : Bool) (cap : Nat) : Nat → Words → Nat → Words → Option Words
  | _,[],p,out => some (finish ([0,Int.ofNat p,Int.ofNat out.length]++out))
  | 0,_,_,_ => none
  | fuel+1,src,p,out => match packBlock mutant src p cap out.length with
    | .error (code,offset) => some (finish ([code,Int.ofNat offset,Int.ofNat out.length]++out))
    | .ok (used,bytes) => packSuffix mutant cap fuel (src.drop used) (p+used) (out++bytes)
def packIndexed (mutant : Bool) (cap : Nat) (data : Words) : Nat → Nat → Words → Option Words
  | 0,p,out => if p == data.length then some (finish ([0,Int.ofNat p,Int.ofNat out.length]++out)) else none
  | fuel+1,p,out => if p == data.length then some (finish ([0,Int.ofNat p,Int.ofNat out.length]++out)) else
    match packBlock mutant (data.drop p) p cap out.length with
    | .error (code,offset) => some (finish ([code,Int.ofNat offset,Int.ofNat out.length]++out))
    | .ok (used,bytes) => packIndexed mutant cap data fuel (p+used) (out++bytes)
def packbits (style : Nat) (xs : Words) :=
  let data := (xs.drop 2).take (iz xs 0).toNat; let cap := (iz xs 1).toNat
  if style == 1 then packSuffix false cap 128 data 0 [] else packIndexed (style == 2) cap data 128 0 []

def splitPath (data : Words) : List Words :=
  let (parts,current) := data.foldl (fun (parts,current) c =>
    if c == 47 then (if current.isEmpty then parts else parts++[current],[]) else (parts,current++[c])) (([] : List Words),([] : Words))
  if current.isEmpty then parts else parts++[current]
def joinPath : List Words → Words
  | [] => []
  | x::xs => x++xs.flatMap (fun s => 47::s)
def path (style : Nat) (xs : Words) : Option Words :=
  let data := (xs.drop 1).take (iz xs 0).toNat
  match (List.range data.length).find? (fun i => iz data i == 0) with
  | some p => some (finish [1,Int.ofNat p,0])
  | none =>
    let absolute := iz data 0 == 47
    let parts := splitPath data
    let kept := if style == 1 then
        let (pending,result) := parts.foldr (fun part (pending,result) =>
          if part == [46] then (pending,result) else if part == [46,46] then (pending+1,result)
          else if pending > 0 then (pending-1,result) else (pending,part::result)) (0,([] : List Words))
        (if absolute then [] else List.replicate pending [46,46])++result
      else
        let stack := parts.foldl (fun stack part =>
          if part == [46] then stack else if part == [46,46] then
            if !stack.isEmpty && (style == 2 || getOr stack 0 [] != [46,46]) then stack.drop 1
            else if absolute then stack else part::stack
          else part::stack) ([] : List Words)
        stack.reverse
    let result := if absolute then 47::joinPath kept else if kept.isEmpty then [46] else joinPath kept
    some (finish ([0,Int.ofNat data.length,Int.ofNat result.length]++result))

def entry (family style : Nat) (xs : Words) : Option Words :=
  match family with
  | 0 => tree style xs | 1 => unionfind style xs | 2 => priority style xs | 3 => evaluator style xs
  | 4 => tlv style xs | 5 => quotes style xs | 6 => packbits style xs | _ => path style xs
def Equivalent (valid : Words → Prop) (a b : Words → Option Words) : Prop := ∀ x, valid x → ∃ o, a x=some o ∧ b x=some o
def RefutationAt (valid : Words → Prop) (a b : Words → Option Words) (x oa ob : Words) : Prop := valid x ∧ a x=some oa ∧ b x=some ob ∧ oa≠ob
end EqualBenchBoundary
