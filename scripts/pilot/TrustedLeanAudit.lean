import Lean
import Lean.Util.CollectAxioms
open Lean

/-- Toy infrastructure checker: importing untrusted compiled gates with
    `loadExts := false` avoids running their environment extensions here. -/
def main : IO UInt32 := do
  initSearchPath "/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0"
  let env ← importModules #[{ module := `Gate }] {} 0 (loadExts := false)
  match env.find? `pilot_checked with
  | some (.thmInfo info) =>
    if info.type != mkConst `Obligation.goal then
      IO.eprintln "checked theorem does not have the fixed goal type"; return 2
  | _ =>
    IO.eprintln "missing checked theorem"; return 2
  let ctx : Core.Context := { fileName := "<pilot-audit>", fileMap := FileMap.ofString "" }
  let state : Core.State := { env := env }
  let axioms ← (collectAxioms `pilot_checked : CoreM (Array Name)).toIO' ctx state
  let allowed : List Name := [`propext, `Classical.choice, `Quot.sound]
  let forbidden := axioms.filter (fun n => !allowed.contains n)
  if !forbidden.isEmpty then
    IO.eprintln s!"forbidden axioms: {forbidden}"; return 1
  IO.println s!"accepted axiom dependencies: {axioms}"
  return 0
