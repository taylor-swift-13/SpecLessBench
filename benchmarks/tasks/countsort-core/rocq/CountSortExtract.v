From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlNatInt ExtrOcamlZInt.
From SpecLessBenchCountSortNative Require Import CountSortNative CountSortDomain.
Extraction Language OCaml.
Extraction "CountSortExtract.ml" CountSortNative.entry CountSortDomain.valid_familyb.
