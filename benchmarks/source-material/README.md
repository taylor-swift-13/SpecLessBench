# Curator source material

This directory contains exact source snapshots selected for SpecLessBench task design. It is **not an agent-facing task package**. QCIP snapshots contain source-system annotations and contracts. Those and reference proof material must not be supplied as independent function-level specifications in an SpecLessBench task.

The import manifest records the upstream/local source path, revision where applicable, raw-byte SHA-256, and license lineage. Source bytes are kept unchanged. The broader QCIP audit includes modified/untracked files; each selected snapshot's HEAD-match status is recorded individually. Local-source content hashes remain the precise identity of the imported material.

These files are not standalone build targets: headers, helper implementations, layout normalization, linking, input/observation boundaries, and reference certificates remain to be finalized. A callee declaration is not a closed implementation. The source bank imports no QCP generated proof artifacts and claims no new proof or Clight translation.

Licenses and copyright notices are in `licenses/` and `NOTICE.md`. QCIP's root license does not override embedded upstream licenses. See [the source review](../research/qcip-candidate-review.md) for what was inspected and [the tasks](../tasks/) for the implementations retained in the benchmark.

Run `python3 scripts/curation/check_inventory.py` from the repository root to check snapshot hashes, family-index references, and basic paper citation/environment consistency. It does not compile or prove programs.
