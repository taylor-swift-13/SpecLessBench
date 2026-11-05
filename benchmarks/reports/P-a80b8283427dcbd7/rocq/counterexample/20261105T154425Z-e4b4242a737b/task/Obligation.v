From Trusted Require Import BasicNative BasicDomain.
Definition goal : Prop := BasicNative.Counterexample (BasicDomain.valid 0) (BasicNative.entry 0 0) (BasicNative.entry 0 2).
