"""Hash, declaration, and native C design checks. Never runs a proof assistant.

Native cases detect construction errors; they do NOT certify any task label.
The native harness has stdio for batching; it is not in any Clight program.
"""
import argparse
import hashlib
import json
import os
import random
import re
import struct
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "benchmarks/tasks/qcip-core"
WORDS = 8192


def pack(family, x):
    if family == "bst":
        xs = [len(x["initial"]), len(x["commands"])]
        xs += [z for pair in x["initial"] for z in pair]
        xs += [z for cmd in x["commands"] for z in cmd]
    elif family == "avl":
        xs = [len(x["commands"])] + [z for cmd in x["commands"] for z in cmd]
    elif family == "ring":
        xs = [x["capacity"], len(x["commands"])]
        for op, arg in x["commands"]:
            payload = [] if op == 1 else arg
            n = arg if op == 1 else len(arg)
            xs += [op, n] + payload + [0] * (64 - len(payload))
    else:
        xs = [x["vertices"], len(x["edges"]), x["start"]]
        xs += [z for edge in x["edges"] for z in edge]
    assert len(xs) <= WORDS
    return xs + [0] * (WORDS - len(xs))


def valid(family, x):
    key = lambda k: -1024 <= k <= 1024
    value = lambda v: -1000000 <= v <= 1000000
    if family == "bst":
        pairs = x["initial"]; cmds = x["commands"]
        return (len(pairs) <= 32 and len(cmds) <= 64 and len({k for k, v in pairs}) == len(pairs)
            and all(key(k) and value(v) for k, v in pairs)
            and all(op in (0, 1) and key(k) for op, k in cmds))
    if family == "avl":
        return len(x["commands"]) <= 64 and all(op in (0, 1) and key(k) and
            (value(v) if op == 0 else v == 0) for op, k, v in x["commands"])
    if family == "ring":
        cap = x["capacity"]
        return 1 <= cap <= 64 and len(x["commands"]) <= 64 and all(
            op in (0, 1, 2) and (1 <= arg <= cap if op == 1 else
            1 <= len(arg) <= cap and all(0 <= b <= 255 for b in arg)) for op, arg in x["commands"])
    n = x["vertices"]
    return (1 <= n <= 10 and 0 <= x["start"] < n and len(x["edges"]) <= 64
        and all(0 <= u < n and 0 <= v < n and 0 <= w <= 1000 for u, v, w in x["edges"]))


def cases(family, rng, count, seed):
    result = [seed]
    if family == "bst":
        result += [{"initial": [], "commands": []},
            {"initial": [[k, -k] for k in range(32)], "commands": [[0, k] for k in range(32)] * 2}]
    elif family == "avl":
        result += [{"commands": []}, {"commands": [[0, k, -k] for k in range(64)]},
            {"commands": [[0, k, k] for k in reversed(range(64))]},
            {"commands": [[0, 1, 7], [0, 1, 9], [1, 1, 0]]}]
    elif family == "ring":
        result += [{"capacity": cap, "commands": [[0, list(range(cap))], [1, cap],
            [2, [255] * cap], [1, cap]]} for cap in (1, 2, 63, 64)]
        result += [{"capacity": 64, "commands": []},
            {"capacity": 64, "commands": [[0, list(range(64))], [1, 64]] * 32}]
    else:
        result += [{"vertices": 1, "start": 0, "edges": []},
            {"vertices": 10, "start": 9, "edges": []},
            {"vertices": 10, "start": 0, "edges": [[i, (i + 1) % 10, 0] for i in range(10)]},
            {"vertices": 10, "start": 0, "edges": [[0, 1, 1000 - i] for i in range(64)]}]
    for _ in range(count):
        if family == "bst":
            keys = rng.sample(range(-40, 41), rng.randrange(33))
            x = {"initial": [[k, rng.randint(-1000000, 1000000)] for k in keys],
                "commands": [[rng.randrange(2), rng.randint(-42, 42)] for _ in range(rng.randrange(65))]}
        elif family == "avl":
            x = {"commands": [[op, rng.randint(-32, 32), rng.randint(-1000000, 1000000) if op == 0 else 0]
                for op in [rng.randrange(2) for _ in range(rng.randrange(65))]]}
        elif family == "ring":
            cap = rng.randint(1, 64); commands = []
            for _ in range(rng.randrange(65)):
                op = rng.randrange(3); n = rng.randint(1, cap)
                commands.append([op, n if op == 1 else [rng.randrange(256) for _ in range(n)]])
            x = {"capacity": cap, "commands": commands}
        else:
            n = rng.randint(1, 10)
            x = {"vertices": n, "start": rng.randrange(n), "edges":
                [[rng.randrange(n), rng.randrange(n), rng.randint(0, 1000)] for _ in range(rng.randrange(65))]}
        result.append(x)
    assert all(valid(family, x) for x in result), family
    return result


def run(cmd, **kwargs):
    result = subprocess.run(cmd, capture_output=True, **kwargs)
    if result.returncode:
        raise RuntimeError(f"Command failed ({result.returncode}): {cmd}\n{result.stderr.decode(errors='replace')}")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--native", action="store_true")
    parser.add_argument("--random-cases", type=int, default=160)
    parser.add_argument("--export-clight", action="store_true")
    args = parser.parse_args()
    manifest = json.loads((CORE / "tasks.json").read_text())
    seeds = json.loads((CORE / "curator-witnesses.json").read_text())
    for record in manifest["protected_files"]:
        path = CORE / record["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record["sha256"], path
    assert len(manifest["families"]) == 4
    assert sum(len(f["tasks"]) for f in manifest["families"]) == 12
    for f in manifest["families"]:
        expected = (CORE / f["tasks"][0]["expected_goal_file"]).read_text()
        public = (CORE / f["tasks"][0]["public_goal_file"]).read_text()
        assert len(re.findall(r"^Theorem ", expected, re.M)) == 3
        assert len(re.findall(r"^Theorem ", public, re.M)) == 3
        for task in f["tasks"]:
            assert task["expected_statement"] in expected
        assert valid(f["id"], seeds[f["id"]]["input"])
    for p in (CORE / "rocq").glob("*.v"):
        text = re.sub(r"\(\*.*?\*\)", "", p.read_text(), flags=re.S)
        assert not re.search(r"\b(Admitted|Axiom|Parameter|Proof|Qed)\b", text), p
    print("Frozen inputs/implementations/targets: hashes and 12 task bindings passed; no proofs.")
    if not (args.native or args.export_clight):
        return
    build = ROOT / "_build/qcip-core"
    build.mkdir(parents=True, exist_ok=True)
    c_dir = build / "c"; c_dir.mkdir(exist_ok=True)
    report = {"schema_version": 1, "kind": "native construction checks, not formal certificates",
        "tasks_manifest_sha256": hashlib.sha256((CORE / "tasks.json").read_bytes()).hexdigest(),
        "compiler": run(["gcc", "--version"]).stdout.decode().splitlines()[0],
        "random_seed": 20261103, "cases_per_family": {}, "variants": [], "witnesses": {}}
    rng = random.Random(report["random_seed"])
    harness = build / "native_harness.c"
    harness.write_text('#define main eb_entry\n#include EB_PROGRAM\n#undef main\n'
        '#include <stdio.h>\nint main(void) {\n'
        'while (fread(eb_input, sizeof(int), 8192, stdin) == 8192) {\n'
        'if (eb_entry() != 0) return 2;\n'
        'if (fwrite(eb_output, sizeof(int), 8192, stdout) != 8192) return 3;\n'
        '} return ferror(stdin) ? 4 : 0; }\n')
    clight = None
    if args.export_clight:
        version = run(["clightgen", "-version"]).stdout.decode()
        assert "3.16" in version, version
        ast_dir = build / "ast"; ast_dir.mkdir(exist_ok=True)
        clight = {"version": version, "exports": []}
    for family in manifest["families"]:
        fid = family["id"]
        inputs = cases(fid, rng, args.random_cases, seeds[fid]["input"]) if args.native else []
        payload = b"".join(struct.pack("<8192i", *pack(fid, x)) for x in inputs)
        report["cases_per_family"][fid] = len(inputs)
        outputs = []
        for variant in family["variants"]:
            src = CORE / variant["source"]; name = variant["id"]
            preprocessed = run(["gcc", "-E", "-P", "-std=c99", str(src)]).stdout
            frozen = c_dir / f"{name}.c"; frozen.write_bytes(preprocessed)
            item = {"id": name, "preprocessed_sha256": hashlib.sha256(preprocessed).hexdigest()}
            if args.native:
                exe = build / name
                compile_cmd = ["gcc", "-std=c99", "-pedantic-errors", "-Werror=implicit-function-declaration",
                    "-O1", "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-no-pie",
                    '-DEB_PROGRAM="' + str(frozen) + '"', str(harness), "-o", str(exe)]
                run(compile_cmd)
                env = dict(os.environ, ASAN_OPTIONS="detect_leaks=0:halt_on_error=1", UBSAN_OPTIONS="halt_on_error=1")
                result = run([str(exe)], input=payload, env=env, timeout=90)
                assert len(result.stdout) == len(inputs) * WORDS * 4
                raw = list(struct.iter_unpack("<8192i", result.stdout))
                observations = [list(o[:o[0] + 1]) for o in raw]
                assert all(0 <= o[0] < WORDS and all(z == 0 for z in o[o[0] + 1:]) for o in raw)
                outputs.append(observations)
                item["asan_ubsan_batch_passed"] = True
                item["native_cases"] = len(inputs)
            if clight is not None:
                ast = ast_dir / f"{name}.v"
                run(["clightgen", "-normalize", "-o", str(ast), str(frozen)])
                clight["exports"].append({"id": name, "ast_sha256": hashlib.sha256(ast.read_bytes()).hexdigest(),
                    "preprocessed_sha256": item["preprocessed_sha256"]})
            report["variants"].append(item)
        if args.native:
            assert outputs[0] == outputs[1] == outputs[2], f"candidate positive disagreement: {fid}"
            assert outputs[0][0] != outputs[3][0], f"witness seed did not distinguish: {fid}"
            report["witnesses"][fid] = {"reference_output": outputs[0][0], "mutant_output": outputs[3][0],
                "status": "native observation only; no Rocq counterexample certificate"}
            print(f"{fid}: 4 implementations x {len(inputs)} cases; candidate positives agree, seed differs; ASan/UBSan passed.")
    if args.native:
        (build / "native-report.json").write_text(json.dumps(report, indent=2) + "\n")
    if clight is not None:
        (build / "ast-manifest.json").write_text(json.dumps(clight, indent=2) + "\n")
    print("No coqc/coqchk, equivalence proof, or formal counterexample was run.")


if __name__ == "__main__":
    main()
