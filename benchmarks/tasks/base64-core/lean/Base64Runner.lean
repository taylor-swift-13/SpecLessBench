import Base64Domain
def main : IO Unit := do
  let stdin ← IO.getStdin; let stdout ← IO.getStdout
  repeat
    let line ← stdin.getLine
    if line.isEmpty then break
    let fields := ((line.trimAscii.toString.splitOn " ").filter (· != "")).map (fun s => s.toInt?.getD 0)
    let family := (SpecLessBenchBase64.get fields 0).toNat
    let style := (SpecLessBenchBase64.get fields 1).toNat
    let xs := fields.drop 2
    if style == 99 then
      stdout.putStrLn (if SpecLessBenchBase64.validFamilyB family xs then "1" else "0")
    else
      match SpecLessBenchBase64.entry family style xs with
      | none => stdout.putStrLn "FAIL"
      | some result => stdout.putStrLn (String.intercalate " " (result.map toString))
