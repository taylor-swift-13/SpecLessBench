import Native
namespace EqualBench
namespace BST
inductive Command where | delete (key : Int) | lookup (key : Int)
structure Input where
  initial : List (Int × Int)
  commands : List Command
def validCommand : Command → Prop
  | .delete k | .lookup k => keyBound k
def valid (x : Input) : Prop := x.initial.length ≤ 32 ∧ x.commands.length ≤ 64 ∧
  (x.initial.map Prod.fst).Nodup ∧ (∀ kv ∈ x.initial, keyBound kv.1 ∧ valueBound kv.2) ∧
  (∀ c ∈ x.commands, validCommand c)
def encodeCommand : Command → Words | .delete k => [0,k] | .lookup k => [1,k]
def encode (x : Input) : Words := pad 8192
  ([Int.ofNat x.initial.length,Int.ofNat x.commands.length] ++
   x.initial.flatMap (fun (k,v) => [k,v]) ++ x.commands.flatMap encodeCommand)
end BST
namespace AVL
inductive Command where | insert (key value : Int) | lookup (key : Int)
structure Input where
  commands : List Command
def validCommand : Command → Prop
  | .insert k v => keyBound k ∧ valueBound v
  | .lookup k => keyBound k
def valid (x : Input) : Prop := x.commands.length ≤ 64 ∧ ∀ c ∈ x.commands, validCommand c
def encodeCommand : Command → Words | .insert k v => [0,k,v] | .lookup k => [1,k,0]
def encode (x : Input) : Words := pad 8192 ([Int.ofNat x.commands.length] ++ x.commands.flatMap encodeCommand)
end AVL
namespace Ring
inductive Command where | write (bytes : Words) | read (count : Int) | force (bytes : Words)
structure Input where
  capacity : Int
  commands : List Command
def validBytes (cap : Int) (xs : Words) : Prop :=
  1 ≤ Int.ofNat xs.length ∧ Int.ofNat xs.length ≤ cap ∧ ∀ b ∈ xs, 0 ≤ b ∧ b ≤ 255
def validCommand (cap : Int) : Command → Prop
  | .write xs | .force xs => validBytes cap xs
  | .read n => 1 ≤ n ∧ n ≤ cap
def valid (x : Input) : Prop := 1 ≤ x.capacity ∧ x.capacity ≤ 64 ∧ x.commands.length ≤ 64 ∧
  ∀ c ∈ x.commands, validCommand x.capacity c
def encodeCommand : Command → Words
  | .write xs => [0,Int.ofNat xs.length] ++ pad 64 xs
  | .read n => [1,n] ++ List.replicate 64 0
  | .force xs => [2,Int.ofNat xs.length] ++ pad 64 xs
def encode (x : Input) : Words := pad 8192
  ([x.capacity,Int.ofNat x.commands.length] ++ x.commands.flatMap encodeCommand)
end Ring
namespace Dijkstra
structure Edge where
  source : Int
  destination : Int
  weight : Int
structure Input where
  vertices : Int
  start : Int
  edges : List Edge
def validEdge (n : Int) (e : Edge) : Prop :=
  0 ≤ e.source ∧ e.source < n ∧ 0 ≤ e.destination ∧ e.destination < n ∧ 0 ≤ e.weight ∧ e.weight ≤ 1000
def valid (x : Input) : Prop := 1 ≤ x.vertices ∧ x.vertices ≤ 10 ∧ 0 ≤ x.start ∧ x.start < x.vertices ∧
  x.edges.length ≤ 64 ∧ ∀ e ∈ x.edges, validEdge x.vertices e
def encode (x : Input) : Words := pad 8192
  ([x.vertices,Int.ofNat x.edges.length,x.start] ++ x.edges.flatMap (fun e => [e.source,e.destination,e.weight]))
end Dijkstra
end EqualBench
