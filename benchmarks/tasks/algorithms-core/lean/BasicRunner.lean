import BasicDomain
def main : IO Unit := do
  let stdin ← IO.getStdin; let stdout ← IO.getStdout
  repeat
    let line ← stdin.getLine
    if line.isEmpty then break
    let fields := ((line.trimAscii.toString.splitOn " ").filter (· != "")).map (fun s => s.toInt?.getD 0)
    let family := (SpecLessBenchBasic.iz fields 0).toNat
    let style := (SpecLessBenchBasic.iz fields 1).toNat
    let xs := fields.drop 2
    if style == 99 then
      stdout.putStrLn (if SpecLessBenchBasic.validB family xs then "1" else "0")
    else
      match SpecLessBenchBasic.entry family style xs with
      | none => stdout.putStrLn "FAIL"
      | some result => stdout.putStrLn (String.intercalate " " (result.map toString))
