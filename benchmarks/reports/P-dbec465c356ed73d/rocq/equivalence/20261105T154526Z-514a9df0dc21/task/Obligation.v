From Trusted Require Import BasicNative BasicDomain.
Definition goal : Prop := BasicNative.Equivalent (BasicDomain.valid 0) (BasicNative.entry 0 0) (BasicNative.entry 0 1).
