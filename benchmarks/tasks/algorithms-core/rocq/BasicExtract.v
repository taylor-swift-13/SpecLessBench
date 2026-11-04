From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlNatInt ExtrOcamlZInt.
From SpecLessBenchBasic Require Import BasicNative BasicDomain.
Extraction Language OCaml.
Extraction "BasicExtract.ml" BasicNative.entry BasicDomain.validb.
