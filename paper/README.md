# EqualBench paper draft

**Target:** ICML 2027  
**Status:** research-design draft; not submission-ready.

The manuscript records 27 groups, 58 contexts, 174 platform instances and 85 Clight ASTs. The latest tranche adds graph closure, layered scope, lease expiration, banded affine alignment and fixed-point resampling. It distinguishes scenarios adapted from project documentation or tests from numerical samples preserved from a public time series. The evidence appendix and [construction summary](../benchmarks/construction/summary.json) record differential coverage. Target types and literal witness obligations are checked. Final certificates, portable dependency locks and isolated solver packages remain pending. See [construction method](../docs/construction-method.md), [proof interface](../benchmarks/proof-interface/v1/README.md) and [cost protocol](../benchmarks/construction/PROTOCOL.md).

## Files

- `main.tex` — anonymous ICML-style manuscript draft.
- `references.bib` — cited primary literature.
- `styles/icml2026/` — unmodified style and bibliography files from the official ICML 2026 author kit, used provisionally because an ICML 2027 author kit was not available when this draft was prepared.

The official [ICML future-meetings page](https://icml.cc/Conferences/FutureMeetings) currently lists ICML 2027 in South America; its 2027 call, deadlines, and style package should be checked and this draft updated when they are published. The ICML 2026 style archive was downloaded from `https://media.icml.cc/Conferences/ICML2026/Styles/icml2026.zip` (SHA-256: `8b29290f5828e176debb57ea9cc00252502973d55ea561a2f18a7f0a326bfc6c`). The available 2026 submission instructions are [here](https://icml.cc/Conferences/2026/AuthorInstructions).

A Windows MiKTeX executable is visible, but the 2026-11-03 compile attempt stopped before parsing LaTeX: MiKTeX reported an unfinished first-time setup and could not create its user configuration directory in this sandbox. No PDF was produced or visually inspected. The earlier WSL check found no compiler there. Before submission, the task set, reference proofs, agent evaluation, related-work coverage, anonymity, and official 2027 formatting all need to be completed or rechecked.
