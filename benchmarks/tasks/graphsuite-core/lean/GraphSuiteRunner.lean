import GraphSuiteDomain
def main : IO Unit := do
  let stdin ← IO.getStdin; let stdout ← IO.getStdout
  repeat
    let line ← stdin.getLine
    if line.isEmpty then break
    let fields := ((line.trimAscii.toString.splitOn " ").filter (· != "")).map (fun s => s.toInt?.getD 0)
    let family := (SpecLessBenchGraphSuite.word fields 0).toNat
    let style := (SpecLessBenchGraphSuite.word fields 1).toNat
    let xs := fields.drop 2
    if style == 99 then
      stdout.putStrLn (if SpecLessBenchGraphSuite.validFamilyB family xs then "1" else "0")
    else
      match SpecLessBenchGraphSuite.entry family style xs with
      | none => stdout.putStrLn "FAIL"
      | some result => stdout.putStrLn (String.intercalate " " (result.map toString))
