From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlNatInt ExtrOcamlZInt.
From SpecLessBenchStatefulNative Require Import StatefulNative StatefulDomain.
Extraction Language OCaml.
Extraction "StatefulExtract.ml" StatefulNative.entry StatefulDomain.valid_familyb.
