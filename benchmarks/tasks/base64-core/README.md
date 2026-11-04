# Base64 encoding equivalence tasks

The input is `[n] ++ bytes`, with 0 ≤ n ≤ 64 and bytes in 0–255. The observation is the complete encoded byte sequence, including padding. V0 encodes three-byte blocks. V1 accumulates bits and emits six-bit groups. V2 emits at most one padding character.

The reference returns `AA==` for the single byte 0. V2 returns `AA=`. That input is an observed distinguishing case. The seven RFC 4648 section 10 vectors are recorded in [fixtures.json](fixtures.json), and the construction test compares the reference output with each recorded expected output.

The two contexts are `A-BASE64-STREAM` and `A-BASE64-PADDING`. Their Lean definitions are `A_BASE64_STREAM_equivalence`, `A_BASE64_STREAM_refutationAt`, `A_BASE64_PADDING_equivalence` and `A_BASE64_PADDING_refutationAt`. Rocq and CompCert expose the corresponding definitions in `rocq/Base64Goals.v` and `compcert/BASE64Goals.v`. The Lean template files live under `lean/pending`. A solve requires either the universal equivalence proof or a proof specialized to concrete valid input and different observations.

The corpus contains 15,285 unique inputs, including seven source vectors, 5,458 new exhaustive short byte strings and 9,815 new seeded random inputs. Nine behavior evaluations per input cover three variants on C, Lean and extracted Rocq. No unintended difference was observed. The mutant differs on 3,573 tested inputs. C was executed with ASan/UBSan. The three Clight ASTs and their target types were checked.

The implementation is newly authored and uses the RFC vectors as curator-side test data. The recorded input domain and observation define the comparison. The final targets have no proofs.
