From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlNatInt ExtrOcamlZInt.
From EqualBenchBase64Native Require Import Base64Native Base64Domain.
Extraction Language OCaml.
Extraction "Base64Extract.ml" Base64Native.entry Base64Domain.valid_familyb.
