"""Measured builds/type-checks only; no proof of a final target is attempted."""
from pathlib import Path
from accounting import ROOT
from measure import measured

CORE = ROOT / "benchmarks/tasks/qcip-core"
BUILD = ROOT / "_build/three-platform"
LEAN = "/home/yangfp/.elan/toolchains/leanprover--lean4---v4.34.0/bin/lean"
COQC = "/home/yangfp/.opam/qcp-8.20/bin/coqc"


def main():
    lean_dir = BUILD / "lean"; lean_dir.mkdir(parents=True, exist_ok=True)
    for name in ("Native", "Domain", "Goals"):
        measured([LEAN, "-o", str(lean_dir / (name+".olean")), str(CORE / "lean" / (name+".lean"))],
            "shared-lean", "typecheck-"+name, timeout=300)
        print("Lean checked definitions/goal types:", name, flush=True)
    paths = ["-Q", str(CORE / "rocq"), "SpecLessBench.QCIP", "-Q", str(CORE / "rocq_native"), "SpecLessBenchNative"]
    for folder, name in (("rocq", "Domain"), ("rocq_native", "Native"), ("rocq_native", "Goals")):
        measured([COQC, *paths, str(CORE / folder / (name+".v"))], "shared-rocq", "typecheck-"+name)
        print("Rocq checked definitions/goal types:", name, flush=True)
    rocq_dir = BUILD / "rocq"; rocq_dir.mkdir(parents=True, exist_ok=True)
    measured([COQC, *paths, str(CORE / "rocq_native/Extract.v")], "shared-rocq", "extract-native", cwd=rocq_dir)
    for name in ("NativeExtract.mli", "NativeExtract.ml"):
        measured(["ocamlopt", "-I", str(rocq_dir), "-c", str(rocq_dir / name)], "shared-rocq", "compile-"+name, cwd=rocq_dir)
    measured(["ocamlopt", "-I", str(rocq_dir), str(rocq_dir / "NativeExtract.cmx"),
        str(ROOT / "scripts/construction/rocq_driver.ml"), "-o", str(rocq_dir / "runner")],
        "shared-rocq", "link-native-runner", cwd=rocq_dir)
    print("Native Lean/Rocq runners ready; CompCert C sources unchanged; no final target proof.", flush=True)


if __name__ == "__main__":
    main()
