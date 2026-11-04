From Coq Require Import Extraction ExtrOcamlBasic ExtrOcamlNatInt ExtrOcamlZInt.
From SpecLessBenchGraphSuiteNative Require Import GraphSuiteNative GraphSuiteDomain.
Extraction Language OCaml.
Extraction "GraphSuiteExtract.ml" GraphSuiteNative.entry GraphSuiteDomain.valid_familyb.
