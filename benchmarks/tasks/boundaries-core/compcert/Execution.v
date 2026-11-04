(* CompCert 3.17 interface; checked with Rocq 9.2. This file contains definitions, no proofs.
 * Definitions only; final target proofs are intentionally deferred.
 * Standard Clight initialization, followed by harness writes to eb_input,
 * models calling main with the fixed input. Function bodies are unchanged. *)
From Stdlib Require Import ZArith List.
From compcert Require Import lib.Integers common.AST common.Values common.Memory
  common.Events common.Globalenvs common.Smallstep cfrontend.Ctypes cfrontend.Clight.
Definition OutputWords : nat := 8192%nat.
Import ListNotations.
Open Scope Z_scope.

Fixpoint store_words (m : mem) (b : block) (ofs : Z) (xs : list Z) : option mem :=
  match xs with
  | [] => Some m
  | x :: tail =>
      match Mem.store Mint32 m b ofs (Vint (Int.repr x)) with
      | Some m' => store_words m' b (ofs + 4) tail
      | None => None
      end
  end.

Fixpoint load_words (n : nat) (m : mem) (b : block) (ofs : Z) : option (list Z) :=
  match n with
  | O => Some []
  | S n' =>
      match Mem.load Mint32 m b ofs, load_words n' m b (ofs + 4) with
      | Some (Vint x), Some xs => Some (Int.signed x :: xs)
      | _, _ => None
      end
  end.

Definition output_words (p : Clight.program) (out_id : ident) (m : mem) : option (list Z) :=
  match Genv.find_symbol (Clight.globalenv p) out_id with
  | Some b => load_words OutputWords m b 0
  | None => None
  end.

Inductive boot (p : Clight.program) (input_id : ident) (xs : list Z) : Clight.state -> Prop :=
| boot_intro : forall f m0 b m1,
    Clight.initial_state p (Clight.Callstate f [] Clight.Kstop m0) ->
    Genv.find_symbol (Clight.globalenv p) input_id = Some b ->
    store_words m0 b 0 xs = Some m1 ->
    boot p input_id xs (Clight.Callstate f [] Clight.Kstop m1).

Definition safe_from (p : Clight.program) (s0 : Clight.state) : Prop :=
  forall s t,
    Smallstep.star Clight.step2 (Clight.globalenv p) s0 t s ->
    (exists r, Clight.final_state s r) \/
    (exists t' s', Clight.step2 (Clight.globalenv p) s t' s').

(* Canonical output is (main return, full initialized output buffer).
 * Unused output slots are reset to zero by begin_output, so padding does not
 * expose hidden heap state. The meaningful length lives in slot zero. *)
Definition observation := (Z * list Z)%type.
Definition executes (p : Clight.program) (input_id out_id : ident)
                    (xs : list Z) (o : observation) : Prop :=
  exists s0 r m ys,
    boot p input_id xs s0 /\ safe_from p s0 /\
    Smallstep.star Clight.step2 (Clight.globalenv p) s0 E0
      (Clight.Returnstate (Vint r) Clight.Kstop m) /\
    output_words p out_id m = Some ys /\ o = (Int.signed r, ys).

Record implementation := {
  program : Clight.program;
  input_symbol : ident;
  output_symbol : ident
}.
Definition run (p : implementation) (xs : list Z) (o : observation) : Prop :=
  executes p.(program) p.(input_symbol) p.(output_symbol) xs o.

Definition Equivalent {I : Type} (valid : I -> Prop) (encode : I -> list Z)
                      (a b : implementation) : Prop :=
  forall x, valid x -> exists o, run a (encode x) o /\ run b (encode x) o.
Definition Counterexample {I : Type} (valid : I -> Prop) (encode : I -> list Z)
                          (a b : implementation) : Prop :=
  exists x oa ob, valid x /\ run a (encode x) oa /\ run b (encode x) ob /\ oa <> ob.
Definition RefutationAt {I : Type} (valid : I -> Prop) (encode : I -> list Z) (a b : implementation) (x : I) (oa ob : observation) : Prop :=
  valid x /\ run a (encode x) oa /\ run b (encode x) ob /\ oa <> ob.
