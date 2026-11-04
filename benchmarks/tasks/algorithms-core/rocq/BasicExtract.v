From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlNatInt ExtrOcamlZInt.
From EqualBenchBasic Require Import BasicNative BasicDomain.
Extraction Language OCaml.
Extraction "BasicExtract.ml" BasicNative.entry BasicDomain.validb.
