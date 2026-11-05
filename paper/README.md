# SpecLessBench paper draft

**Target:** ICML 2027  
**Status:** research-design draft; not submission-ready.

The frozen pilot comprises 71 contexts, 30 split families and 213 platform instances; 103 regenerated Clight ASTs matched the frozen sources. The factorial family is public reference material and is excluded from evaluation, leaving 69 candidate contexts. Its Lean and Rocq equivalence and counterexample goals have checked reference proofs; the CompCert counterexample is checked under documented trusted-library assumptions, while its equivalence goal remains pending. The evidence appendix and [construction summary](../benchmarks/construction/summary.json) record differential coverage. The anonymous index and a synthetic isolation prototype are available, but per-task solver packaging, adversarial grading review, remaining certificates and portable dependency locks remain open. See the [pilot status](../benchmarks/pilot-v1/README.md), [construction method](../docs/construction-method.md), [proof interface](../benchmarks/proof-interface/v1/README.md) and [cost protocol](../benchmarks/construction/PROTOCOL.md).

## Files

- `main.tex` — anonymous ICML-style manuscript draft.
- `references.bib` — cited primary literature.
- `styles/icml2026/` — unmodified style and bibliography files from the official ICML 2026 author kit, used provisionally because an ICML 2027 author kit was not available when this draft was prepared.

The official [ICML future-meetings page](https://icml.cc/Conferences/FutureMeetings) currently lists ICML 2027 in South America; its 2027 call, deadlines, and style package should be checked and this draft updated when they are published. The ICML 2026 style archive was downloaded from `https://media.icml.cc/Conferences/ICML2026/Styles/icml2026.zip` (SHA-256: `8b29290f5828e176debb57ea9cc00252502973d55ea561a2f18a7f0a326bfc6c`). The available 2026 submission instructions are [here](https://icml.cc/Conferences/2026/AuthorInstructions).

The 2026-11-03 Windows MiKTeX attempt stopped before parsing LaTeX because its first-time setup was unfinished. A subsequent WSL pdfLaTeX and BibTeX build succeeded on 2026-11-04, producing an 18-page draft under `_build/paper-pilot/`; it has not been visually inspected. Before submission, the task set, reference proofs, agent evaluation, related-work coverage, anonymity, and official 2027 formatting all need to be completed or rechecked.
