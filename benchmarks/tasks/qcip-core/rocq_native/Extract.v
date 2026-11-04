From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlNatInt ExtrOcamlZInt.
From EqualBenchNative Require Import Native.
Extraction Language OCaml.
Extraction "NativeExtract.ml" entry.
