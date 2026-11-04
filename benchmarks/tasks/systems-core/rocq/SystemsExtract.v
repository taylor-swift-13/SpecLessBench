From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlNatInt ExtrOcamlZInt.
From EqualBenchSystemsNative Require Import SystemsNative SystemsDomain.
Extraction Language OCaml.
Extraction "SystemsExtract.ml" SystemsNative.entry SystemsDomain.valid_familyb.
