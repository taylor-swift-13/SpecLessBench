From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlNatInt ExtrOcamlZInt.
From EqualBenchStatefulNative Require Import StatefulNative StatefulDomain.
Extraction Language OCaml.
Extraction "StatefulExtract.ml" StatefulNative.entry StatefulDomain.valid_familyb.
