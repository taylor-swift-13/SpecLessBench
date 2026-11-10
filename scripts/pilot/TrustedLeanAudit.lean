import Lean
open Lean

/-- Policy revision: ordinary native_decide facts are independently replayed by
the kernel. Candidate code generation and imported environment extensions are
never executed by this auditor. This is not a native-name whitelist. -/
def nativeAuditPolicy : String := "lean-native-kernel-replay-v1"

private def standardAxioms : List Name :=
  [`propext, `Classical.choice, `Quot.sound]

/-- Walk actual checked declaration bodies instead of trusting serialized
collectAxioms environment-extension metadata from candidate modules. -/
private partial def checkedAxioms (env : Environment) (todo : List Name)
    (seen : NameSet := {}) (axs : NameSet := {}) : Except String (Array Name) := do
  match todo with
  | [] => return axs.toArray.qsort Name.lt
  | name :: rest =>
    if seen.contains name then
      return ← checkedAxioms env rest seen axs
    let seen := seen.insert name
    let some info := env.checked.get.find? name
      | throw s!"missing checked dependency: {name}"
    let enqueue (e : Expr) (tail : List Name) := e.getUsedConstants.toList ++ tail
    match info with
    | .axiomInfo v =>
      checkedAxioms env (enqueue v.type rest) seen (axs.insert name)
    | .defnInfo v =>
      checkedAxioms env (enqueue v.type (enqueue v.value rest)) seen axs
    | .thmInfo v =>
      checkedAxioms env (enqueue v.type (enqueue v.value rest)) seen axs
    | .opaqueInfo v =>
      checkedAxioms env (enqueue v.type (enqueue v.value rest)) seen axs
    | .quotInfo _ => checkedAxioms env rest seen axs
    | .ctorInfo v => checkedAxioms env (enqueue v.type rest) seen axs
    | .recInfo v => checkedAxioms env (enqueue v.type rest) seen axs
    | .inductInfo v =>
      checkedAxioms env (enqueue v.type (v.ctors ++ rest)) seen axs

private def nativeNameShape (name : Name) : Bool :=
  match name.toString.splitOn "." |>.reverse with
  | last :: "native_decide" :: "_native" :: _ =>
    last == "ax" || last.startsWith "ax_"
  | _ => false

private def fromSubmissionModule (env : Environment) (name : Name) : Bool :=
  match env.getModuleIdxFor? name with
  | none => false
  | some idx => env.header.moduleNames[idx.toNat]? == some `Submission

/-- Official Lean 4.34 native_decide emits an axiom of this exact shape:
Eq Bool (decide proposition instance) true. Check the checked declaration and
its owner, then replay the fact with the kernel, which ignores extern and
implemented_by code-generation substitutions. Merely forging the name never
suffices. A forged but kernel-provable fact has no additional logical trust. -/
private def nativeComputation (env : Environment) (name : Name) : Option Expr := do
  if !nativeNameShape name || !fromSubmissionModule env name then none else do
    let .axiomInfo info ← env.checked.get.find? name | none
    let args := info.type.getAppArgs
    if info.type.getAppFn.constName? != some ``Eq || args.size != 3 then none else do
      if args[0]! != mkConst ``Bool || args[2]! != mkConst ``Bool.true then none else do
        let e := args[1]!
        if !e.isAppOfArity ``Decidable.decide 2 || e.hasFVar || e.hasMVar || e.hasLooseBVars then
          none
        else some e

private inductive ReplayFailure where
  | rejected (detail : String)
  | incomplete (detail : String)

private partial def freshReplayName (env : Environment) (idx : Nat := 0) : Name :=
  let name := Name.num `_speclessNativeKernelReplay idx
  if (env.checked.get.find? name).isSome then freshReplayName env (idx + 1) else name

private def replayNative (env : Environment) (name : Name) (_e : Expr) : Except ReplayFailure Unit := do
  let some (.axiomInfo info) := env.checked.get.find? name
    | throw (.rejected s!"native_decide kernel replay failed: {name}: missing axiom")
  -- Check a new theorem with the exact fact's type and the proof `Eq.refl true`.
  -- The kernel must reduce the original decision expression to true to accept
  -- this proof. Unlike the debugging Kernel.check/isDefEq APIs, addDeclCore
  -- exposes explicit resource parameters. Heartbeats are unlimited inside the
  -- auditor's external wall-time/cgroup boundary; depth is generous but finite.
  -- `doCheck := true` bypasses no kernel checking and evaluates no candidate
  -- native code, environment extension, or Meta-level reduction override.
  let replayDecl := Declaration.thmDecl {
    name := freshReplayName env
    levelParams := info.levelParams
    type := info.type
    value := mkApp2 (mkConst ``Eq.refl [1]) (mkConst ``Bool) (mkConst ``Bool.true)
  }
  match env.addDeclCore 0 100000 replayDecl none (doCheck := true) with
  | .ok _ => pure ()
  | .error .deterministicTimeout =>
    throw (.incomplete s!"native_decide kernel replay incomplete: {name}: deterministic-timeout")
  | .error .excessiveMemory =>
    throw (.incomplete s!"native_decide kernel replay incomplete: {name}: excessive-memory")
  | .error .deepRecursion =>
    throw (.incomplete s!"native_decide kernel replay incomplete: {name}: deep-recursion")
  | .error .interrupted =>
    throw (.incomplete s!"native_decide kernel replay incomplete: {name}: interrupted")
  | .error _ =>
    throw (.rejected s!"native_decide kernel replay failed: {name}: fact not proved by kernel reduction")

def main : IO UInt32 := do
  initSearchPath "/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0"
  let env ← importModules #[{ module := `Gate }] {} 0 (loadExts := false)
  if env.header.trustLevel != 0 then
    IO.eprintln "trusted auditor did not import at trust level zero"; return 2
  match env.checked.get.find? `pilot_checked with
  | some (.thmInfo info) =>
    if info.type != mkConst `Obligation.goal then
      IO.eprintln "checked theorem does not have the fixed goal type"; return 2
  | _ =>
    IO.eprintln "missing checked theorem"; return 2
  let axiomResult := checkedAxioms env [`pilot_checked]
  match axiomResult with
  | .error msg => IO.eprintln msg; return 2
  | .ok _ => pure ()
  let axioms := axiomResult.toOption.getD #[]
  let mut computations : Array (Name × Expr) := #[]
  let mut forbidden : Array Name := #[]
  for name in axioms do
    if !standardAxioms.contains name then
      match nativeComputation env name with
      | some e => computations := computations.push (name, e)
      | none => forbidden := forbidden.push name
  -- Reject every other dependency before evaluating any permitted native fact.
  -- This includes axioms used inside the decision procedure or proposition.
  if !forbidden.isEmpty then
    IO.eprintln s!"forbidden axioms: {forbidden}"; return 1
  let mut verified : Array Name := #[]
  for (name, e) in computations do
    match replayNative env name e with
    | .ok () => verified := verified.push name
    | .error (.rejected msg) => IO.eprintln msg; return 1
    | .error (.incomplete msg) => IO.eprintln msg; return 3
  let standard := axioms.filter (standardAxioms.contains ·)
  IO.println s!"accepted axiom dependencies: {axioms}"
  IO.println s!"verified native_decide dependencies: {verified}"
  let evidence := Json.mkObj [
    ("policy", toJson nativeAuditPolicy),
    ("verification", toJson ("independent-kernel-reduction" : String)),
    ("trust_level", toJson (0 : Nat)),
    ("standard_axioms", toJson (standard.map Name.toString)),
    ("verified_native_decide_axioms", toJson (verified.map Name.toString))]
  IO.println s!"native_audit: {evidence.compress}"
  return 0
