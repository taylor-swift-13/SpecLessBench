"""Measured three-language differential construction with reproducible cases.

Group once, all variants/platforms inside it. No proof or equivalence label is
inferred from absence of counterexamples. Every disagreement persists before
the run fails. Small domains are exhaustive; larger domains are seeded samples.
"""
import argparse
import gzip
import hashlib
import itertools
import json
import random
import struct
import sys
from pathlib import Path
from accounting import ROOT, AUDIT, append, now
from measure import measured
from build_three_platform import LEAN, BUILD, CORE
sys.path.insert(0, str(ROOT / "scripts/curation"))
from check_qcip_core import pack, valid, cases

FIDS = {"bst": 0, "avl": 1, "ring": 2, "dijkstra": 3}
GIDS = {"bst": "qcip-bst-delete", "avl": "qcip-avl-insert", "ring": "qcip-xizi-ring", "dijkstra": "qcip-dijkstra"}


def small_cases(fid):
    if fid == "bst":
        cmds = [[op, k] for op in (0, 1) for k in range(3)]
        for n in range(4):
            for initial in itertools.permutations(range(3), n):
                for q in range(4):
                    for trace in itertools.product(cmds, repeat=q):
                        yield {"initial": [[k, [0, 17, -7][k]] for k in initial], "commands": list(trace)}
    elif fid == "avl":
        cmds = [[0, k, v] for k in (-1, 0, 1) for v in (-7, 7)] + [[1, k, 0] for k in (-1, 0, 1)]
        for q in range(4):
            for trace in itertools.product(cmds, repeat=q):
                yield {"commands": list(trace)}
    elif fid == "ring":
        for cap in (1, 2):
            bytesets = [list(xs) for n in range(1, cap+1) for xs in itertools.product((0, 1), repeat=n)]
            cmds = [[op, bs] for op in (0, 2) for bs in bytesets] + [[1, n] for n in range(1, cap+1)]
            for q in range(4):
                for trace in itertools.product(cmds, repeat=q):
                    yield {"capacity": cap, "commands": list(trace)}
    else:
        endpoints = [(u, v) for u in range(3) for v in range(3) if u != v]
        for weights in itertools.product((-1, 0, 1), repeat=6):
            edges = [[u, v, w] for (u, v), w in zip(endpoints, weights) if w >= 0]
            for start in range(3):
                yield {"vertices": 3, "start": start, "edges": edges}


def prefix_length(fid, x):
    if fid == "bst": return 2+2*len(x["initial"])+2*len(x["commands"])
    if fid == "avl": return 1+3*len(x["commands"])
    if fid == "ring": return 2+66*len(x["commands"])
    return 3+3*len(x["edges"])


def c_outputs(path):
    result = []
    with path.open("rb") as stream:
        while head := stream.read(4):
            assert len(head) == 4
            n = struct.unpack("<i", head)[0]
            assert 0 <= n < 8192
            payload = stream.read(n*4)
            assert len(payload) == n*4
            result.append([n, *struct.unpack("<"+str(n)+"i", payload)])
    return result


def native_outputs(path):
    return [None if line.strip() == "FAIL" else list(map(int, line.split())) for line in path.read_text().splitlines()]


def issue(fid, kind, index, x, observations, run_id):
    row = {"schema_version": 1, "id": run_id+"-"+kind+"-"+str(index), "timestamp_utc": now(),
        "group_id": GIDS[fid], "revision": "design-v0.2", "kind": kind, "status": "open",
        "case_index": index, "input": x, "observations": observations,
        "reproducer": f"python3 scripts/construction/differential.py --family {fid}",
        "minimality": "not minimized yet; exact safe-domain input retained"}
    append(AUDIT / "issues.jsonl", row)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--family", choices=FIDS, required=True)
    parser.add_argument("--random-cases", type=int, default=5000)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args(); fid = args.family; gid = GIDS[fid]
    seed = 20261103 + FIDS[fid]
    witnesses = json.loads((CORE / "curator-witnesses.json").read_text())
    xs = cases(fid, random.Random(seed), args.random_cases, witnesses[fid]["input"])
    curated_count = len(xs)-args.random_cases
    exhaustive = list(small_cases(fid)) if not args.smoke else []
    xs += exhaustive
    if args.smoke: xs = xs[:12]
    assert all(valid(fid, x) for x in xs)
    run_id = fid+"-"+now().replace(":", "").replace(".", "")
    folder = BUILD / "differential" / run_id; folder.mkdir(parents=True)
    corpus = folder / "cases.jsonl.gz"
    with gzip.open(corpus, "wt") as out:
        for x in xs: out.write(json.dumps(x, separators=(",", ":"))+"\n")
    binary = folder / "input.bin"; text = folder / "input.txt"
    with binary.open("wb") as b, text.open("w") as t:
        for x in xs:
            data = pack(fid, x); b.write(struct.pack("<8192i", *data))
            prefix = " ".join(map(str, data[:prefix_length(fid, x)]))
            for style in range(4): t.write(f"{FIDS[fid]} {style} {prefix}\n")
    harness = folder / "harness.c"
    harness.write_text('#define main eb_entry\n#include EB_PROGRAM\n#undef main\n#include <stdio.h>\n'
        'int main(void) { int i,n; while(fread(eb_input,sizeof(int),8192,stdin)==8192) {\n'
        'if(eb_entry()!=0) return 2; n=eb_output[0]; if(n<0||n>=8192) return 3;\n'
        'for(i=n+1;i<8192;i++) if(eb_output[i]!=0) return 4;\n'
        'if(fwrite(eb_output,sizeof(int),n+1,stdout)!=(unsigned)(n+1)) return 5;\n'
        '} return ferror(stdin)?6:0; }\n')
    c_results = []
    for style in range(4):
        source = CORE / fid / f"v{style}.c"
        frozen = folder / f"v{style}.c"
        measured(["gcc", "-E", "-P", "-std=c99", str(source)], gid, "preprocess", stdout_path=frozen)
        exe = folder / f"v{style}"
        measured(["gcc", "-std=c99", "-O1", "-g", "-fsanitize=address,undefined", "-fno-omit-frame-pointer", "-no-pie",
            '-DEB_PROGRAM="'+str(frozen)+'"', str(harness), "-o", str(exe)], gid, "compile-c-sanitized")
        output = folder / f"c{style}.out"
        measured([str(exe)], gid, "c-differential", stdin_path=binary, stdout_path=output, timeout=600)
        c_results.append(c_outputs(output))
    native = {}
    for platform, cmd in (("lean", [LEAN, "--run", str(CORE / "lean/Native.lean")]),
                          ("rocq", [str(BUILD / "rocq/runner")])):
        output = folder / (platform+".out")
        measured(cmd, gid, platform+"-differential", stdin_path=text, stdout_path=output, timeout=1200)
        native[platform] = native_outputs(output)
        assert len(native[platform]) == 4*len(xs)
    errors = []; retained = []
    for i, x in enumerate(xs):
        if not (c_results[0][i] == c_results[1][i] == c_results[2][i]):
            issue(fid, "unexpected-positive-difference", i, x, {f"c{j}": c_results[j][i] for j in range(3)}, run_id)
            errors.append(i)
        for style in range(4):
            expected = c_results[style][i]
            obs = {p: native[p][4*i+style] for p in native}
            if any(y != expected for y in obs.values()):
                issue(fid, "cross-platform-mismatch-v"+str(style), i, x, {"c": expected, **obs}, run_id)
                errors.append(i)
        if c_results[0][i] != c_results[3][i]:
            retained.append(i)
    if retained:
        i = min(retained, key=lambda i: len(json.dumps(xs[i])))
        append(AUDIT / "issues.jsonl", {"schema_version": 1, "id": run_id+"-retained-negative",
            "timestamp_utc": now(), "group_id": gid, "kind": "intentional-negative-observed",
            "revision": "design-v0.2", "status": "retained-as-task", "input": xs[i],
            "observations": {"v0": c_results[0][i], "v3": c_results[3][i]},
            "minimality": "smallest JSON among tested witnesses; not globally minimal",
            "witness_case_count": len(retained), "certificate": None})
    report = {"schema_version": 1, "run_id": run_id, "group_id": gid, "revision": "design-v0.2",
        "rng_seed": seed, "random_cases_requested": args.random_cases, "curated_cases": curated_count,
        "exhaustive_small_cases": len(exhaustive), "case_count": len(xs), "program_executions": 12*len(xs),
        "platforms": ["lean", "rocq", "c-native-sanitized"], "compcert_semantic_execution_tested": False,
        "positive_disagreements": len(set(errors)), "negative_distinguishing_inputs": len(retained),
        "corpus": corpus.relative_to(ROOT).as_posix(), "corpus_sha256": hashlib.sha256(corpus.read_bytes()).hexdigest(),
        "source_registry_sha256": hashlib.sha256((CORE / "three-platform.json").read_bytes()).hexdigest(),
        "status": "failed" if errors or not retained else "differential-passed; no formal equivalence inferred",
        "smoke": args.smoke}
    out = CORE / "evidence" / (fid+"-three-platform"+("-smoke" if args.smoke else "")+".json")
    out.write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(report), flush=True)
    if errors or not retained: raise SystemExit("Differential construction failed; retained issues must be resolved and rerun")


if __name__ == "__main__":
    main()
