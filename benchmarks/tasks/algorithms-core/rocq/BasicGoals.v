From SpecLessBenchBasic Require Import BasicNative BasicDomain.

Theorem R_FAC_EQ : BasicNative.Equivalent (BasicDomain.valid 0) (BasicNative.entry 0 0) (BasicNative.entry 0 1).
Abort.

Theorem R_FAC_EQ_certificate : BasicNative.Certificate (BasicDomain.valid 0) (BasicNative.entry 0 0) (BasicNative.entry 0 1).
Abort.

Theorem R_FAC_CEX : BasicNative.Counterexample (BasicDomain.valid 0) (BasicNative.entry 0 0) (BasicNative.entry 0 2).
Abort.

Theorem R_FAC_CEX_certificate : BasicNative.Certificate (BasicDomain.valid 0) (BasicNative.entry 0 0) (BasicNative.entry 0 2).
Abort.

Theorem R_REV_EQ : BasicNative.Equivalent (BasicDomain.valid 1) (BasicNative.entry 1 0) (BasicNative.entry 1 1).
Abort.

Theorem R_REV_EQ_certificate : BasicNative.Certificate (BasicDomain.valid 1) (BasicNative.entry 1 0) (BasicNative.entry 1 1).
Abort.

Theorem R_REV_CEX : BasicNative.Counterexample (BasicDomain.valid 1) (BasicNative.entry 1 0) (BasicNative.entry 1 2).
Abort.

Theorem R_REV_CEX_certificate : BasicNative.Certificate (BasicDomain.valid 1) (BasicNative.entry 1 0) (BasicNative.entry 1 2).
Abort.

Theorem R_SUM_EQ : BasicNative.Equivalent (BasicDomain.valid 2) (BasicNative.entry 2 0) (BasicNative.entry 2 1).
Abort.

Theorem R_SUM_EQ_certificate : BasicNative.Certificate (BasicDomain.valid 2) (BasicNative.entry 2 0) (BasicNative.entry 2 1).
Abort.

Theorem R_SUM_CEX : BasicNative.Counterexample (BasicDomain.valid 2) (BasicNative.entry 2 0) (BasicNative.entry 2 2).
Abort.

Theorem R_SUM_CEX_certificate : BasicNative.Certificate (BasicDomain.valid 2) (BasicNative.entry 2 0) (BasicNative.entry 2 2).
Abort.

Theorem R_MAT_EQ : BasicNative.Equivalent (BasicDomain.valid 3) (BasicNative.entry 3 0) (BasicNative.entry 3 1).
Abort.

Theorem R_MAT_EQ_certificate : BasicNative.Certificate (BasicDomain.valid 3) (BasicNative.entry 3 0) (BasicNative.entry 3 1).
Abort.

Theorem R_MAT_CEX : BasicNative.Counterexample (BasicDomain.valid 3) (BasicNative.entry 3 0) (BasicNative.entry 3 2).
Abort.

Theorem R_MAT_CEX_certificate : BasicNative.Certificate (BasicDomain.valid 3) (BasicNative.entry 3 0) (BasicNative.entry 3 2).
Abort.

Theorem R_STR_EQ : BasicNative.Equivalent (BasicDomain.valid 4) (BasicNative.entry 4 0) (BasicNative.entry 4 1).
Abort.

Theorem R_STR_EQ_certificate : BasicNative.Certificate (BasicDomain.valid 4) (BasicNative.entry 4 0) (BasicNative.entry 4 1).
Abort.

Theorem R_STR_CEX : BasicNative.Counterexample (BasicDomain.valid 4) (BasicNative.entry 4 0) (BasicNative.entry 4 2).
Abort.

Theorem R_STR_CEX_certificate : BasicNative.Certificate (BasicDomain.valid 4) (BasicNative.entry 4 0) (BasicNative.entry 4 2).
Abort.

Theorem R_QUE_EQ : BasicNative.Equivalent (BasicDomain.valid 5) (BasicNative.entry 5 0) (BasicNative.entry 5 1).
Abort.

Theorem R_QUE_EQ_certificate : BasicNative.Certificate (BasicDomain.valid 5) (BasicNative.entry 5 0) (BasicNative.entry 5 1).
Abort.

Theorem R_QUE_CEX : BasicNative.Counterexample (BasicDomain.valid 5) (BasicNative.entry 5 0) (BasicNative.entry 5 2).
Abort.

Theorem R_QUE_CEX_certificate : BasicNative.Certificate (BasicDomain.valid 5) (BasicNative.entry 5 0) (BasicNative.entry 5 2).
Abort.
