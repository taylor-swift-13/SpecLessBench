"""Read-only source inventory for EqualBench candidate selection.

Function/call information is lexical and is explicitly not a C semantic analysis.
The report records raw and comment-stripped hashes because local QCIP files can
differ from the repository's HEAD. This script never compiles or proves sources.
"""

import argparse
import hashlib
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path


TOKEN = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*.*?\*/|//[^\n]*', re.S)
FUNCTION = re.compile(
    r"(?m)^[ \t]*(?:[A-Za-z_]\w*[\s*]+)+?([A-Za-z_]\w*)\s*\([^;{}]*\)\s*\{"
)
KEYWORDS = {"if", "for", "while", "switch", "sizeof", "return", "_Alignof"}


def strip_comments(source):
    return TOKEN.sub(
        lambda m: re.sub(r"[^\n]", " ", m.group())
        if m.group().startswith(("/*", "//")) else m.group(), source
    )


def digest(data):
    return hashlib.sha256(data).hexdigest()


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    return result.stdout if result.returncode == 0 else None


def inspect(root, relative):
    path = root / relative
    raw = path.read_bytes()
    code = strip_comments(raw.decode("utf-8", errors="replace"))
    masked = TOKEN.sub(lambda m: re.sub(r"[^\n]", " ", m.group()), code)
    functions = []
    for match in FUNCTION.finditer(masked):
        opening = masked.index("{", match.start(), match.end())
        balance, end = 1, opening + 1
        while end < len(masked) and balance:
            balance += (masked[end] == "{") - (masked[end] == "}")
            end += 1
        calls = sorted(set(re.findall(r"\b([A-Za-z_]\w*)\s*\(", masked[opening + 1:end])) - KEYWORDS)
        functions.append({
            "name": match.group(1),
            "line": masked.count("\n", 0, match.start()) + 1,
            "call_tokens": calls,
            "recursive_call_token": match.group(1) in calls,
        })
    head_blob = git(root, "show", "HEAD:" + relative)
    status = git(root, "status", "--porcelain=v1", "--", relative)
    return {
        "path": relative,
        "sha256": digest(raw),
        "comment_stripped_sha256": digest(code.encode("utf-8")),
        "head_blob_sha256": digest(head_blob) if head_blob is not None else None,
        "matches_head_blob": head_blob == raw if head_blob is not None else False,
        "git_status": status.decode().strip() if status else "",
        "physical_lines": len(code.splitlines()),
        "code_lines_after_comment_removal": sum(bool(line.strip()) for line in code.splitlines()),
        "includes": re.findall(r'(?m)^\s*#\s*include\s+([^\n]+)', code),
        "functions_lexical": functions,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--show", nargs="*", default=[])
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    if args.show:
        for relative in args.show:
            if relative not in manifest["paths"]:
                raise ValueError("Path not selected in manifest: " + relative)
            print("SOURCE:", relative)
            code = strip_comments((args.root / relative).read_text())
            for number, line in enumerate(code.splitlines(), 1):
                if line.strip():
                    print(f"{number}: {line.rstrip()}")
        return
    records = [inspect(args.root, path) for path in manifest["paths"]]
    report = {
        "schema_version": 1,
        "inspection_date": datetime.now(timezone.utc).date().isoformat(),
        "root": str(args.root),
        "repository_head": git(args.root, "rev-parse", "HEAD").decode().strip(),
        "method": "Lexical source inspection; no compilation, symbolic execution, proof replay, or equivalence certification.",
        "call_tokens_warning": "Tokens may name macros, declarations in other translation units, or indirect-call wrappers; not a resolved call graph.",
        "file_count": len(records),
        "files": records,
    }
    if not args.output:
        parser.error("--output is required unless --show is used")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    for record in records:
        names = ", ".join(f["name"] for f in record["functions_lexical"])
        print(f'{record["path"]}: {record["code_lines_after_comment_removal"]} code lines; {names}')


if __name__ == "__main__":
    main()
