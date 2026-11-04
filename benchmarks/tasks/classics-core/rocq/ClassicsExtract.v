From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlNatInt ExtrOcamlZInt.
From SpecLessBenchClassicsNative Require Import ClassicsNative ClassicsDomain.
Extraction Language OCaml.
Extraction "ClassicsExtract.ml" ClassicsNative.entry ClassicsDomain.valid_familyb.
