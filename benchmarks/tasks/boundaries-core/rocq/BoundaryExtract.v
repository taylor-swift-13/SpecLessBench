From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlNatInt ExtrOcamlZInt.
From EqualBenchBoundaryNative Require Import BoundaryNative BoundaryDomain.
Extraction Language OCaml.
Extraction "BoundaryExtract.ml" BoundaryNative.entry BoundaryDomain.valid_familyb.
