From Coq Require Import String List ZArith.
From compcert Require Import Coqlib Integers Floats AST Ctypes Cop Clight Clightdefs.
Import Clightdefs.ClightNotations.
Local Open Scope Z_scope.
Local Open Scope string_scope.
Local Open Scope clight_scope.

Module Info.
  Definition version := "3.17".
  Definition build_number := "".
  Definition build_tag := "".
  Definition build_branch := "".
  Definition arch := "x86".
  Definition model := "64".
  Definition abi := "standard".
  Definition bitsize := 64.
  Definition big_endian := false.
  Definition source_file := "ALIGNMENT_V1.c".
  Definition normalized := true.
End Info.

Definition _Candidate : ident := $"Candidate".
Definition ___builtin_ais_annot : ident := $"__builtin_ais_annot".
Definition ___builtin_annot : ident := $"__builtin_annot".
Definition ___builtin_annot_intval : ident := $"__builtin_annot_intval".
Definition ___builtin_bswap : ident := $"__builtin_bswap".
Definition ___builtin_bswap16 : ident := $"__builtin_bswap16".
Definition ___builtin_bswap32 : ident := $"__builtin_bswap32".
Definition ___builtin_bswap64 : ident := $"__builtin_bswap64".
Definition ___builtin_clz : ident := $"__builtin_clz".
Definition ___builtin_clzl : ident := $"__builtin_clzl".
Definition ___builtin_clzll : ident := $"__builtin_clzll".
Definition ___builtin_ctz : ident := $"__builtin_ctz".
Definition ___builtin_ctzl : ident := $"__builtin_ctzl".
Definition ___builtin_ctzll : ident := $"__builtin_ctzll".
Definition ___builtin_debug : ident := $"__builtin_debug".
Definition ___builtin_expect : ident := $"__builtin_expect".
Definition ___builtin_fabs : ident := $"__builtin_fabs".
Definition ___builtin_fabsf : ident := $"__builtin_fabsf".
Definition ___builtin_fmadd : ident := $"__builtin_fmadd".
Definition ___builtin_fmax : ident := $"__builtin_fmax".
Definition ___builtin_fmin : ident := $"__builtin_fmin".
Definition ___builtin_fmsub : ident := $"__builtin_fmsub".
Definition ___builtin_fnmadd : ident := $"__builtin_fnmadd".
Definition ___builtin_fnmsub : ident := $"__builtin_fnmsub".
Definition ___builtin_fsqrt : ident := $"__builtin_fsqrt".
Definition ___builtin_membar : ident := $"__builtin_membar".
Definition ___builtin_memcpy_aligned : ident := $"__builtin_memcpy_aligned".
Definition ___builtin_read16_reversed : ident := $"__builtin_read16_reversed".
Definition ___builtin_read32_reversed : ident := $"__builtin_read32_reversed".
Definition ___builtin_sel : ident := $"__builtin_sel".
Definition ___builtin_sqrt : ident := $"__builtin_sqrt".
Definition ___builtin_unreachable : ident := $"__builtin_unreachable".
Definition ___builtin_va_arg : ident := $"__builtin_va_arg".
Definition ___builtin_va_copy : ident := $"__builtin_va_copy".
Definition ___builtin_va_end : ident := $"__builtin_va_end".
Definition ___builtin_va_start : ident := $"__builtin_va_start".
Definition ___builtin_write16_reversed : ident := $"__builtin_write16_reversed".
Definition ___builtin_write32_reversed : ident := $"__builtin_write32_reversed".
Definition ___compcert_i64_dtos : ident := $"__compcert_i64_dtos".
Definition ___compcert_i64_dtou : ident := $"__compcert_i64_dtou".
Definition ___compcert_i64_sar : ident := $"__compcert_i64_sar".
Definition ___compcert_i64_sdiv : ident := $"__compcert_i64_sdiv".
Definition ___compcert_i64_shl : ident := $"__compcert_i64_shl".
Definition ___compcert_i64_shr : ident := $"__compcert_i64_shr".
Definition ___compcert_i64_smod : ident := $"__compcert_i64_smod".
Definition ___compcert_i64_smulh : ident := $"__compcert_i64_smulh".
Definition ___compcert_i64_stod : ident := $"__compcert_i64_stod".
Definition ___compcert_i64_stof : ident := $"__compcert_i64_stof".
Definition ___compcert_i64_udiv : ident := $"__compcert_i64_udiv".
Definition ___compcert_i64_umod : ident := $"__compcert_i64_umod".
Definition ___compcert_i64_umulh : ident := $"__compcert_i64_umulh".
Definition ___compcert_i64_utod : ident := $"__compcert_i64_utod".
Definition ___compcert_i64_utof : ident := $"__compcert_i64_utof".
Definition ___compcert_va_composite : ident := $"__compcert_va_composite".
Definition ___compcert_va_float64 : ident := $"__compcert_va_float64".
Definition ___compcert_va_int32 : ident := $"__compcert_va_int32".
Definition ___compcert_va_int64 : ident := $"__compcert_va_int64".
Definition _a : ident := $"a".
Definition _align : ident := $"align".
Definition _align_cell : ident := $"align_cell".
Definition _b : ident := $"b".
Definition _band : ident := $"band".
Definition _base : ident := $"base".
Definition _begin_output : ident := $"begin_output".
Definition _best : ident := $"best".
Definition _cost : ident := $"cost".
Definition _cost_add : ident := $"cost_add".
Definition _diagonal : ident := $"diagonal".
Definition _dp : ident := $"dp".
Definition _eb_input : ident := $"eb_input".
Definition _eb_out : ident := $"eb_out".
Definition _eb_output : ident := $"eb_output".
Definition _emit : ident := $"emit".
Definition _end_output : ident := $"end_output".
Definition _extend : ident := $"extend".
Definition _extend_minimum : ident := $"extend_minimum".
Definition _extension : ident := $"extension".
Definition _gap : ident := $"gap".
Definition _horizontal : ident := $"horizontal".
Definition _i : ident := $"i".
Definition _j : ident := $"j".
Definition _m : ident := $"m".
Definition _main : ident := $"main".
Definition _mask : ident := $"mask".
Definition _mismatch : ident := $"mismatch".
Definition _move : ident := $"move".
Definition _moves : ident := $"moves".
Definition _n : ident := $"n".
Definition _offer : ident := $"offer".
Definition _offer_gaps : ident := $"offer_gaps".
Definition _open_cost : ident := $"open_cost".
Definition _penalty : ident := $"penalty".
Definition _previous : ident := $"previous".
Definition _start : ident := $"start".
Definition _vertical : ident := $"vertical".
Definition _x : ident := $"x".
Definition _t'1 : ident := 128%positive.
Definition _t'2 : ident := 129%positive.
Definition _t'3 : ident := 130%positive.
Definition _t'4 : ident := 131%positive.
Definition _t'5 : ident := 132%positive.
Definition _t'6 : ident := 133%positive.
Definition _t'7 : ident := 134%positive.
Definition _t'8 : ident := 135%positive.

Definition v_eb_input := {|
  gvar_info := (tarray tint 8192);
  gvar_init := (Init_space 32768 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_eb_output := {|
  gvar_info := (tarray tint 8192);
  gvar_init := (Init_space 32768 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_eb_out := {|
  gvar_info := tint;
  gvar_init := (Init_space 4 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition f_emit := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_x, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_t'2, tint) :: (_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Sset _t'2 (Evar _eb_out tint))
    (Sassign
      (Ederef
        (Ebinop Oadd (Evar _eb_output (tarray tint 8192))
          (Etempvar _t'2 tint) (tptr tint)) tint) (Etempvar _x tint)))
  (Ssequence
    (Sset _t'1 (Evar _eb_out tint))
    (Sassign (Evar _eb_out tint)
      (Ebinop Oadd (Etempvar _t'1 tint) (Econst_int (Int.repr 1) tint) tint))))
|}.

Definition f_begin_output := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := nil;
  fn_vars := nil;
  fn_temps := ((_i, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Sset _i (Econst_int (Int.repr 0) tint))
    (Sloop
      (Ssequence
        (Sifthenelse (Ebinop Olt (Etempvar _i tint)
                       (Econst_int (Int.repr 8192) tint) tint)
          Sskip
          Sbreak)
        (Sassign
          (Ederef
            (Ebinop Oadd (Evar _eb_output (tarray tint 8192))
              (Etempvar _i tint) (tptr tint)) tint)
          (Econst_int (Int.repr 0) tint)))
      (Sset _i
        (Ebinop Oadd (Etempvar _i tint) (Econst_int (Int.repr 1) tint) tint))))
  (Sassign (Evar _eb_out tint) (Econst_int (Int.repr 1) tint)))
|}.

Definition f_end_output := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := nil;
  fn_vars := nil;
  fn_temps := ((_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Sset _t'1 (Evar _eb_out tint))
    (Sassign
      (Ederef
        (Ebinop Oadd (Evar _eb_output (tarray tint 8192))
          (Econst_int (Int.repr 0) tint) (tptr tint)) tint)
      (Ebinop Osub (Etempvar _t'1 tint) (Econst_int (Int.repr 1) tint) tint)))
  (Sreturn (Some (Econst_int (Int.repr 0) tint))))
|}.

Definition v_dp := {|
  gvar_info := (tarray (tarray tint 13) 13);
  gvar_init := (Init_space 676 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_vertical := {|
  gvar_info := (tarray tint 13);
  gvar_init := (Init_space 52 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_horizontal := {|
  gvar_info := tint;
  gvar_init := (Init_space 4 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_open_cost := {|
  gvar_info := tint;
  gvar_init := (Init_space 4 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_extension := {|
  gvar_info := tint;
  gvar_init := (Init_space 4 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_mismatch := {|
  gvar_info := tint;
  gvar_init := (Init_space 4 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_n := {|
  gvar_info := tint;
  gvar_init := (Init_space 4 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition f_cost_add := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := ((_base, tint) :: (_penalty, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Sifthenelse (Ebinop Oeq (Etempvar _base tint)
                 (Econst_int (Int.repr 100000) tint) tint)
    (Sset _t'1 (Ecast (Econst_int (Int.repr 100000) tint) tint))
    (Sset _t'1
      (Ecast
        (Ebinop Oadd (Etempvar _base tint) (Etempvar _penalty tint) tint)
        tint)))
  (Sreturn (Some (Etempvar _t'1 tint))))
|}.

Definition f_offer := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_best, (tptr (Tstruct _Candidate noattr))) ::
                (_cost, tint) :: (_move, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_t'1, tint) :: (_t'4, tint) :: (_t'3, tint) ::
               (_t'2, tint) :: nil);
  fn_body :=
(Ssequence
  (Sset _t'2
    (Efield
      (Ederef (Etempvar _best (tptr (Tstruct _Candidate noattr)))
        (Tstruct _Candidate noattr)) _cost tint))
  (Sifthenelse (Ebinop Olt (Etempvar _cost tint) (Etempvar _t'2 tint) tint)
    (Ssequence
      (Sassign
        (Efield
          (Ederef (Etempvar _best (tptr (Tstruct _Candidate noattr)))
            (Tstruct _Candidate noattr)) _cost tint) (Etempvar _cost tint))
      (Sassign
        (Efield
          (Ederef (Etempvar _best (tptr (Tstruct _Candidate noattr)))
            (Tstruct _Candidate noattr)) _moves tint) (Etempvar _move tint)))
    (Ssequence
      (Sifthenelse (Ebinop One (Etempvar _cost tint)
                     (Econst_int (Int.repr 100000) tint) tint)
        (Ssequence
          (Sset _t'4
            (Efield
              (Ederef (Etempvar _best (tptr (Tstruct _Candidate noattr)))
                (Tstruct _Candidate noattr)) _cost tint))
          (Sset _t'1
            (Ecast
              (Ebinop Oeq (Etempvar _cost tint) (Etempvar _t'4 tint) tint)
              tbool)))
        (Sset _t'1 (Econst_int (Int.repr 0) tint)))
      (Sifthenelse (Etempvar _t'1 tint)
        (Ssequence
          (Sset _t'3
            (Efield
              (Ederef (Etempvar _best (tptr (Tstruct _Candidate noattr)))
                (Tstruct _Candidate noattr)) _moves tint))
          (Sassign
            (Efield
              (Ederef (Etempvar _best (tptr (Tstruct _Candidate noattr)))
                (Tstruct _Candidate noattr)) _moves tint)
            (Ebinop Oor (Etempvar _t'3 tint) (Etempvar _move tint) tint)))
        Sskip))))
|}.

Definition f_diagonal := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := ((_i, tint) :: (_j, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_a, tint) :: (_b, tint) :: (_penalty, tint) ::
               (_t'4, tint) :: (_t'3, tint) :: (_t'2, tint) ::
               (_t'1, tint) :: (_t'7, tint) :: (_t'6, tint) ::
               (_t'5, tint) :: nil);
  fn_body :=
(Ssequence
  (Sset _a
    (Ederef
      (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
        (Ebinop Oadd (Econst_int (Int.repr 5) tint) (Etempvar _i tint) tint)
        (tptr tint)) tint))
  (Ssequence
    (Ssequence
      (Sset _t'7 (Evar _n tint))
      (Sset _b
        (Ederef
          (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
            (Ebinop Oadd
              (Ebinop Oadd (Econst_int (Int.repr 5) tint)
                (Etempvar _t'7 tint) tint) (Etempvar _j tint) tint)
            (tptr tint)) tint)))
    (Ssequence
      (Ssequence
        (Ssequence
          (Ssequence
            (Sifthenelse (Ebinop Oeq (Etempvar _a tint) (Etempvar _b tint)
                           tint)
              (Sset _t'1 (Econst_int (Int.repr 1) tint))
              (Sset _t'1
                (Ecast
                  (Ebinop Oeq (Etempvar _a tint)
                    (Econst_int (Int.repr 4) tint) tint) tbool)))
            (Sifthenelse (Etempvar _t'1 tint)
              (Sset _t'2 (Econst_int (Int.repr 1) tint))
              (Sset _t'2
                (Ecast
                  (Ebinop Oeq (Etempvar _b tint)
                    (Econst_int (Int.repr 4) tint) tint) tbool))))
          (Sifthenelse (Etempvar _t'2 tint)
            (Sset _t'3 (Ecast (Econst_int (Int.repr 0) tint) tint))
            (Ssequence
              (Sset _t'6 (Evar _mismatch tint))
              (Sset _t'3
                (Ecast
                  (Ebinop Oadd (Etempvar _t'6 tint)
                    (Ebinop Olt (Etempvar _a tint) (Etempvar _b tint) tint)
                    tint) tint)))))
        (Sset _penalty (Etempvar _t'3 tint)))
      (Ssequence
        (Ssequence
          (Sset _t'5
            (Ederef
              (Ebinop Oadd
                (Ederef
                  (Ebinop Oadd (Evar _dp (tarray (tarray tint 13) 13))
                    (Ebinop Osub (Etempvar _i tint)
                      (Econst_int (Int.repr 1) tint) tint)
                    (tptr (tarray tint 13))) (tarray tint 13))
                (Ebinop Osub (Etempvar _j tint)
                  (Econst_int (Int.repr 1) tint) tint) (tptr tint)) tint))
          (Scall (Some _t'4)
            (Evar _cost_add (Tfunction (tint :: tint :: nil) tint cc_default))
            ((Etempvar _t'5 tint) :: (Etempvar _penalty tint) :: nil)))
        (Sreturn (Some (Etempvar _t'4 tint)))))))
|}.

Definition f_extend_minimum := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := ((_previous, tint) :: (_gap, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_start, tint) :: (_extend, tint) :: (_t'3, tint) ::
               (_t'2, tint) :: (_t'1, tint) :: (_t'5, tint) ::
               (_t'4, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Ssequence
      (Sset _t'5 (Evar _open_cost tint))
      (Scall (Some _t'1)
        (Evar _cost_add (Tfunction (tint :: tint :: nil) tint cc_default))
        ((Etempvar _previous tint) :: (Etempvar _t'5 tint) :: nil)))
    (Sset _start (Etempvar _t'1 tint)))
  (Ssequence
    (Ssequence
      (Ssequence
        (Sset _t'4 (Evar _extension tint))
        (Scall (Some _t'2)
          (Evar _cost_add (Tfunction (tint :: tint :: nil) tint cc_default))
          ((Etempvar _gap tint) :: (Etempvar _t'4 tint) :: nil)))
      (Sset _extend (Etempvar _t'2 tint)))
    (Ssequence
      (Sifthenelse (Ebinop Olt (Etempvar _start tint) (Etempvar _extend tint)
                     tint)
        (Sset _t'3 (Ecast (Etempvar _start tint) tint))
        (Sset _t'3 (Ecast (Etempvar _extend tint) tint)))
      (Sreturn (Some (Etempvar _t'3 tint))))))
|}.

Definition f_offer_gaps := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_best, (tptr (Tstruct _Candidate noattr))) :: (_i, tint) ::
                (_j, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_t'2, tint) :: (_t'1, tint) :: (_t'8, tint) ::
               (_t'7, tint) :: (_t'6, tint) :: (_t'5, tint) ::
               (_t'4, tint) :: (_t'3, tint) :: nil);
  fn_body :=
(Ssequence
  (Sifthenelse (Ebinop Ogt (Etempvar _i tint) (Econst_int (Int.repr 0) tint)
                 tint)
    (Ssequence
      (Ssequence
        (Sset _t'7
          (Ederef
            (Ebinop Oadd
              (Ederef
                (Ebinop Oadd (Evar _dp (tarray (tarray tint 13) 13))
                  (Ebinop Osub (Etempvar _i tint)
                    (Econst_int (Int.repr 1) tint) tint)
                  (tptr (tarray tint 13))) (tarray tint 13))
              (Etempvar _j tint) (tptr tint)) tint))
        (Ssequence
          (Sset _t'8
            (Ederef
              (Ebinop Oadd (Evar _vertical (tarray tint 13))
                (Etempvar _j tint) (tptr tint)) tint))
          (Scall (Some _t'1)
            (Evar _extend_minimum (Tfunction (tint :: tint :: nil) tint
                                    cc_default))
            ((Etempvar _t'7 tint) :: (Etempvar _t'8 tint) :: nil))))
      (Sassign
        (Ederef
          (Ebinop Oadd (Evar _vertical (tarray tint 13)) (Etempvar _j tint)
            (tptr tint)) tint) (Etempvar _t'1 tint)))
    Sskip)
  (Ssequence
    (Sifthenelse (Ebinop Ogt (Etempvar _j tint)
                   (Econst_int (Int.repr 0) tint) tint)
      (Ssequence
        (Ssequence
          (Sset _t'5
            (Ederef
              (Ebinop Oadd
                (Ederef
                  (Ebinop Oadd (Evar _dp (tarray (tarray tint 13) 13))
                    (Etempvar _i tint) (tptr (tarray tint 13)))
                  (tarray tint 13))
                (Ebinop Osub (Etempvar _j tint)
                  (Econst_int (Int.repr 1) tint) tint) (tptr tint)) tint))
          (Ssequence
            (Sset _t'6 (Evar _horizontal tint))
            (Scall (Some _t'2)
              (Evar _extend_minimum (Tfunction (tint :: tint :: nil) tint
                                      cc_default))
              ((Etempvar _t'5 tint) :: (Etempvar _t'6 tint) :: nil))))
        (Sassign (Evar _horizontal tint) (Etempvar _t'2 tint)))
      Sskip)
    (Ssequence
      (Ssequence
        (Sset _t'4
          (Ederef
            (Ebinop Oadd (Evar _vertical (tarray tint 13)) (Etempvar _j tint)
              (tptr tint)) tint))
        (Scall None
          (Evar _offer (Tfunction
                         ((tptr (Tstruct _Candidate noattr)) :: tint ::
                          tint :: nil) tvoid cc_default))
          ((Etempvar _best (tptr (Tstruct _Candidate noattr))) ::
           (Etempvar _t'4 tint) :: (Econst_int (Int.repr 2) tint) :: nil)))
      (Ssequence
        (Sset _t'3 (Evar _horizontal tint))
        (Scall None
          (Evar _offer (Tfunction
                         ((tptr (Tstruct _Candidate noattr)) :: tint ::
                          tint :: nil) tvoid cc_default))
          ((Etempvar _best (tptr (Tstruct _Candidate noattr))) ::
           (Etempvar _t'3 tint) :: (Econst_int (Int.repr 4) tint) :: nil))))))
|}.

Definition f_align_cell := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := ((_i, tint) :: (_j, tint) :: (_band, tint) :: nil);
  fn_vars := ((_best, (Tstruct _Candidate noattr)) :: nil);
  fn_temps := ((_t'4, tint) :: (_t'3, tint) :: (_t'2, tint) ::
               (_t'1, tint) :: (_t'6, tint) :: (_t'5, tint) :: nil);
  fn_body :=
(Ssequence
  (Sassign (Efield (Evar _best (Tstruct _Candidate noattr)) _cost tint)
    (Econst_int (Int.repr 100000) tint))
  (Ssequence
    (Sassign (Efield (Evar _best (Tstruct _Candidate noattr)) _moves tint)
      (Econst_int (Int.repr 0) tint))
    (Ssequence
      (Ssequence
        (Sifthenelse (Ebinop Ogt
                       (Ebinop Osub (Etempvar _i tint) (Etempvar _j tint)
                         tint) (Etempvar _band tint) tint)
          (Sset _t'4 (Econst_int (Int.repr 1) tint))
          (Sset _t'4
            (Ecast
              (Ebinop Ogt
                (Ebinop Osub (Etempvar _j tint) (Etempvar _i tint) tint)
                (Etempvar _band tint) tint) tbool)))
        (Sifthenelse (Etempvar _t'4 tint)
          (Ssequence
            (Sassign
              (Ederef
                (Ebinop Oadd (Evar _vertical (tarray tint 13))
                  (Etempvar _j tint) (tptr tint)) tint)
              (Econst_int (Int.repr 100000) tint))
            (Sassign (Evar _horizontal tint)
              (Econst_int (Int.repr 100000) tint)))
          (Ssequence
            (Sifthenelse (Ebinop Oeq (Etempvar _i tint)
                           (Econst_int (Int.repr 0) tint) tint)
              (Sset _t'3
                (Ecast
                  (Ebinop Oeq (Etempvar _j tint)
                    (Econst_int (Int.repr 0) tint) tint) tbool))
              (Sset _t'3 (Econst_int (Int.repr 0) tint)))
            (Sifthenelse (Etempvar _t'3 tint)
              (Sassign
                (Efield (Evar _best (Tstruct _Candidate noattr)) _cost tint)
                (Econst_int (Int.repr 0) tint))
              (Ssequence
                (Ssequence
                  (Sifthenelse (Ebinop Ogt (Etempvar _i tint)
                                 (Econst_int (Int.repr 0) tint) tint)
                    (Sset _t'2
                      (Ecast
                        (Ebinop Ogt (Etempvar _j tint)
                          (Econst_int (Int.repr 0) tint) tint) tbool))
                    (Sset _t'2 (Econst_int (Int.repr 0) tint)))
                  (Sifthenelse (Etempvar _t'2 tint)
                    (Ssequence
                      (Scall (Some _t'1)
                        (Evar _diagonal (Tfunction (tint :: tint :: nil) tint
                                          cc_default))
                        ((Etempvar _i tint) :: (Etempvar _j tint) :: nil))
                      (Scall None
                        (Evar _offer (Tfunction
                                       ((tptr (Tstruct _Candidate noattr)) ::
                                        tint :: tint :: nil) tvoid
                                       cc_default))
                        ((Eaddrof (Evar _best (Tstruct _Candidate noattr))
                           (tptr (Tstruct _Candidate noattr))) ::
                         (Etempvar _t'1 tint) ::
                         (Econst_int (Int.repr 1) tint) :: nil)))
                    Sskip))
                (Scall None
                  (Evar _offer_gaps (Tfunction
                                      ((tptr (Tstruct _Candidate noattr)) ::
                                       tint :: tint :: nil) tvoid cc_default))
                  ((Eaddrof (Evar _best (Tstruct _Candidate noattr))
                     (tptr (Tstruct _Candidate noattr))) ::
                   (Etempvar _i tint) :: (Etempvar _j tint) :: nil)))))))
      (Ssequence
        (Ssequence
          (Sset _t'6
            (Efield (Evar _best (Tstruct _Candidate noattr)) _cost tint))
          (Sassign
            (Ederef
              (Ebinop Oadd
                (Ederef
                  (Ebinop Oadd (Evar _dp (tarray (tarray tint 13) 13))
                    (Etempvar _i tint) (tptr (tarray tint 13)))
                  (tarray tint 13)) (Etempvar _j tint) (tptr tint)) tint)
            (Etempvar _t'6 tint)))
        (Ssequence
          (Sset _t'5
            (Efield (Evar _best (Tstruct _Candidate noattr)) _moves tint))
          (Sreturn (Some (Etempvar _t'5 tint))))))))
|}.

Definition f_align := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_m, tint) :: (_band, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_i, tint) :: (_j, tint) :: (_mask, tint) :: (_t'2, tint) ::
               (_t'1, tint) :: (_t'7, tint) :: (_t'6, tint) ::
               (_t'5, tint) :: (_t'4, tint) :: (_t'3, tint) :: nil);
  fn_body :=
(Ssequence
  (Sset _mask (Econst_int (Int.repr 0) tint))
  (Ssequence
    (Ssequence
      (Sset _j (Econst_int (Int.repr 0) tint))
      (Sloop
        (Ssequence
          (Sifthenelse (Ebinop Ole (Etempvar _j tint) (Etempvar _m tint)
                         tint)
            Sskip
            Sbreak)
          (Sassign
            (Ederef
              (Ebinop Oadd (Evar _vertical (tarray tint 13))
                (Etempvar _j tint) (tptr tint)) tint)
            (Econst_int (Int.repr 100000) tint)))
        (Sset _j
          (Ebinop Oadd (Etempvar _j tint) (Econst_int (Int.repr 1) tint)
            tint))))
    (Ssequence
      (Ssequence
        (Sset _i (Econst_int (Int.repr 0) tint))
        (Sloop
          (Ssequence
            (Ssequence
              (Sset _t'7 (Evar _n tint))
              (Sifthenelse (Ebinop Ole (Etempvar _i tint)
                             (Etempvar _t'7 tint) tint)
                Sskip
                Sbreak))
            (Ssequence
              (Sassign (Evar _horizontal tint)
                (Econst_int (Int.repr 100000) tint))
              (Ssequence
                (Sset _j (Econst_int (Int.repr 0) tint))
                (Sloop
                  (Ssequence
                    (Sifthenelse (Ebinop Ole (Etempvar _j tint)
                                   (Etempvar _m tint) tint)
                      Sskip
                      Sbreak)
                    (Ssequence
                      (Scall (Some _t'1)
                        (Evar _align_cell (Tfunction
                                            (tint :: tint :: tint :: nil)
                                            tint cc_default))
                        ((Etempvar _i tint) :: (Etempvar _j tint) ::
                         (Etempvar _band tint) :: nil))
                      (Sset _mask (Etempvar _t'1 tint))))
                  (Sset _j
                    (Ebinop Oadd (Etempvar _j tint)
                      (Econst_int (Int.repr 1) tint) tint))))))
          (Sset _i
            (Ebinop Oadd (Etempvar _i tint) (Econst_int (Int.repr 1) tint)
              tint))))
      (Ssequence
        (Ssequence
          (Ssequence
            (Sset _t'3 (Evar _n tint))
            (Ssequence
              (Sset _t'4
                (Ederef
                  (Ebinop Oadd
                    (Ederef
                      (Ebinop Oadd (Evar _dp (tarray (tarray tint 13) 13))
                        (Etempvar _t'3 tint) (tptr (tarray tint 13)))
                      (tarray tint 13)) (Etempvar _m tint) (tptr tint)) tint))
              (Sifthenelse (Ebinop Oeq (Etempvar _t'4 tint)
                             (Econst_int (Int.repr 100000) tint) tint)
                (Sset _t'2
                  (Ecast (Eunop Oneg (Econst_int (Int.repr 1) tint) tint)
                    tint))
                (Ssequence
                  (Sset _t'5 (Evar _n tint))
                  (Ssequence
                    (Sset _t'6
                      (Ederef
                        (Ebinop Oadd
                          (Ederef
                            (Ebinop Oadd
                              (Evar _dp (tarray (tarray tint 13) 13))
                              (Etempvar _t'5 tint) (tptr (tarray tint 13)))
                            (tarray tint 13)) (Etempvar _m tint) (tptr tint))
                        tint))
                    (Sset _t'2 (Ecast (Etempvar _t'6 tint) tint)))))))
          (Scall None (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
            ((Etempvar _t'2 tint) :: nil)))
        (Scall None (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
          ((Etempvar _mask tint) :: nil))))))
|}.

Definition f_main := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := nil;
  fn_vars := nil;
  fn_temps := ((_t'1, tint) :: (_t'7, tint) :: (_t'6, tint) ::
               (_t'5, tint) :: (_t'4, tint) :: (_t'3, tint) ::
               (_t'2, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Scall None (Evar _begin_output (Tfunction nil tvoid cc_default)) nil)
    (Ssequence
      (Ssequence
        (Sset _t'7
          (Ederef
            (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
              (Econst_int (Int.repr 0) tint) (tptr tint)) tint))
        (Sassign (Evar _n tint) (Etempvar _t'7 tint)))
      (Ssequence
        (Ssequence
          (Sset _t'6
            (Ederef
              (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
                (Econst_int (Int.repr 3) tint) (tptr tint)) tint))
          (Sassign (Evar _open_cost tint) (Etempvar _t'6 tint)))
        (Ssequence
          (Ssequence
            (Sset _t'5
              (Ederef
                (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
                  (Econst_int (Int.repr 4) tint) (tptr tint)) tint))
            (Sassign (Evar _extension tint) (Etempvar _t'5 tint)))
          (Ssequence
            (Ssequence
              (Sset _t'4
                (Ederef
                  (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
                    (Econst_int (Int.repr 5) tint) (tptr tint)) tint))
              (Sassign (Evar _mismatch tint) (Etempvar _t'4 tint)))
            (Ssequence
              (Ssequence
                (Sset _t'2
                  (Ederef
                    (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
                      (Econst_int (Int.repr 1) tint) (tptr tint)) tint))
                (Ssequence
                  (Sset _t'3
                    (Ederef
                      (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
                        (Econst_int (Int.repr 2) tint) (tptr tint)) tint))
                  (Scall None
                    (Evar _align (Tfunction (tint :: tint :: nil) tvoid
                                   cc_default))
                    ((Etempvar _t'2 tint) :: (Etempvar _t'3 tint) :: nil))))
              (Ssequence
                (Scall (Some _t'1)
                  (Evar _end_output (Tfunction nil tint cc_default)) nil)
                (Sreturn (Some (Etempvar _t'1 tint))))))))))
  (Sreturn (Some (Econst_int (Int.repr 0) tint))))
|}.

Definition composites : list composite_definition :=
(Composite _Candidate Struct
   (Member_plain _cost tint :: Member_plain _moves tint :: nil)
   noattr :: nil).

Definition global_definitions : list (ident * globdef fundef type) :=
((___compcert_va_int32,
   Gfun(External (EF_runtime "__compcert_va_int32"
                   (mksignature (AST.Xptr :: nil) AST.Xint cc_default))
     ((tptr tvoid) :: nil) tuint cc_default)) ::
 (___compcert_va_int64,
   Gfun(External (EF_runtime "__compcert_va_int64"
                   (mksignature (AST.Xptr :: nil) AST.Xlong cc_default))
     ((tptr tvoid) :: nil) tulong cc_default)) ::
 (___compcert_va_float64,
   Gfun(External (EF_runtime "__compcert_va_float64"
                   (mksignature (AST.Xptr :: nil) AST.Xfloat cc_default))
     ((tptr tvoid) :: nil) tdouble cc_default)) ::
 (___compcert_va_composite,
   Gfun(External (EF_runtime "__compcert_va_composite"
                   (mksignature (AST.Xptr :: AST.Xlong :: nil) AST.Xptr
                     cc_default)) ((tptr tvoid) :: tulong :: nil)
     (tptr tvoid) cc_default)) ::
 (___compcert_i64_dtos,
   Gfun(External (EF_runtime "__compcert_i64_dtos"
                   (mksignature (AST.Xfloat :: nil) AST.Xlong cc_default))
     (tdouble :: nil) tlong cc_default)) ::
 (___compcert_i64_dtou,
   Gfun(External (EF_runtime "__compcert_i64_dtou"
                   (mksignature (AST.Xfloat :: nil) AST.Xlong cc_default))
     (tdouble :: nil) tulong cc_default)) ::
 (___compcert_i64_stod,
   Gfun(External (EF_runtime "__compcert_i64_stod"
                   (mksignature (AST.Xlong :: nil) AST.Xfloat cc_default))
     (tlong :: nil) tdouble cc_default)) ::
 (___compcert_i64_utod,
   Gfun(External (EF_runtime "__compcert_i64_utod"
                   (mksignature (AST.Xlong :: nil) AST.Xfloat cc_default))
     (tulong :: nil) tdouble cc_default)) ::
 (___compcert_i64_stof,
   Gfun(External (EF_runtime "__compcert_i64_stof"
                   (mksignature (AST.Xlong :: nil) AST.Xsingle cc_default))
     (tlong :: nil) tfloat cc_default)) ::
 (___compcert_i64_utof,
   Gfun(External (EF_runtime "__compcert_i64_utof"
                   (mksignature (AST.Xlong :: nil) AST.Xsingle cc_default))
     (tulong :: nil) tfloat cc_default)) ::
 (___compcert_i64_sdiv,
   Gfun(External (EF_runtime "__compcert_i64_sdiv"
                   (mksignature (AST.Xlong :: AST.Xlong :: nil) AST.Xlong
                     cc_default)) (tlong :: tlong :: nil) tlong cc_default)) ::
 (___compcert_i64_udiv,
   Gfun(External (EF_runtime "__compcert_i64_udiv"
                   (mksignature (AST.Xlong :: AST.Xlong :: nil) AST.Xlong
                     cc_default)) (tulong :: tulong :: nil) tulong
     cc_default)) ::
 (___compcert_i64_smod,
   Gfun(External (EF_runtime "__compcert_i64_smod"
                   (mksignature (AST.Xlong :: AST.Xlong :: nil) AST.Xlong
                     cc_default)) (tlong :: tlong :: nil) tlong cc_default)) ::
 (___compcert_i64_umod,
   Gfun(External (EF_runtime "__compcert_i64_umod"
                   (mksignature (AST.Xlong :: AST.Xlong :: nil) AST.Xlong
                     cc_default)) (tulong :: tulong :: nil) tulong
     cc_default)) ::
 (___compcert_i64_shl,
   Gfun(External (EF_runtime "__compcert_i64_shl"
                   (mksignature (AST.Xlong :: AST.Xint :: nil) AST.Xlong
                     cc_default)) (tlong :: tint :: nil) tlong cc_default)) ::
 (___compcert_i64_shr,
   Gfun(External (EF_runtime "__compcert_i64_shr"
                   (mksignature (AST.Xlong :: AST.Xint :: nil) AST.Xlong
                     cc_default)) (tulong :: tint :: nil) tulong cc_default)) ::
 (___compcert_i64_sar,
   Gfun(External (EF_runtime "__compcert_i64_sar"
                   (mksignature (AST.Xlong :: AST.Xint :: nil) AST.Xlong
                     cc_default)) (tlong :: tint :: nil) tlong cc_default)) ::
 (___compcert_i64_smulh,
   Gfun(External (EF_runtime "__compcert_i64_smulh"
                   (mksignature (AST.Xlong :: AST.Xlong :: nil) AST.Xlong
                     cc_default)) (tlong :: tlong :: nil) tlong cc_default)) ::
 (___compcert_i64_umulh,
   Gfun(External (EF_runtime "__compcert_i64_umulh"
                   (mksignature (AST.Xlong :: AST.Xlong :: nil) AST.Xlong
                     cc_default)) (tulong :: tulong :: nil) tulong
     cc_default)) ::
 (___builtin_ais_annot,
   Gfun(External (EF_builtin "__builtin_ais_annot"
                   (mksignature (AST.Xptr :: nil) AST.Xvoid
                     {|cc_vararg:=(Some 1); cc_unproto:=false; cc_structret:=false|}))
     ((tptr tschar) :: nil) tvoid
     {|cc_vararg:=(Some 1); cc_unproto:=false; cc_structret:=false|})) ::
 (___builtin_bswap64,
   Gfun(External (EF_builtin "__builtin_bswap64"
                   (mksignature (AST.Xlong :: nil) AST.Xlong cc_default))
     (tulong :: nil) tulong cc_default)) ::
 (___builtin_bswap,
   Gfun(External (EF_builtin "__builtin_bswap"
                   (mksignature (AST.Xint :: nil) AST.Xint cc_default))
     (tuint :: nil) tuint cc_default)) ::
 (___builtin_bswap32,
   Gfun(External (EF_builtin "__builtin_bswap32"
                   (mksignature (AST.Xint :: nil) AST.Xint cc_default))
     (tuint :: nil) tuint cc_default)) ::
 (___builtin_bswap16,
   Gfun(External (EF_builtin "__builtin_bswap16"
                   (mksignature (AST.Xint16unsigned :: nil)
                     AST.Xint16unsigned cc_default)) (tushort :: nil) tushort
     cc_default)) ::
 (___builtin_clz,
   Gfun(External (EF_builtin "__builtin_clz"
                   (mksignature (AST.Xint :: nil) AST.Xint cc_default))
     (tuint :: nil) tint cc_default)) ::
 (___builtin_clzl,
   Gfun(External (EF_builtin "__builtin_clzl"
                   (mksignature (AST.Xlong :: nil) AST.Xint cc_default))
     (tulong :: nil) tint cc_default)) ::
 (___builtin_clzll,
   Gfun(External (EF_builtin "__builtin_clzll"
                   (mksignature (AST.Xlong :: nil) AST.Xint cc_default))
     (tulong :: nil) tint cc_default)) ::
 (___builtin_ctz,
   Gfun(External (EF_builtin "__builtin_ctz"
                   (mksignature (AST.Xint :: nil) AST.Xint cc_default))
     (tuint :: nil) tint cc_default)) ::
 (___builtin_ctzl,
   Gfun(External (EF_builtin "__builtin_ctzl"
                   (mksignature (AST.Xlong :: nil) AST.Xint cc_default))
     (tulong :: nil) tint cc_default)) ::
 (___builtin_ctzll,
   Gfun(External (EF_builtin "__builtin_ctzll"
                   (mksignature (AST.Xlong :: nil) AST.Xint cc_default))
     (tulong :: nil) tint cc_default)) ::
 (___builtin_fabs,
   Gfun(External (EF_builtin "__builtin_fabs"
                   (mksignature (AST.Xfloat :: nil) AST.Xfloat cc_default))
     (tdouble :: nil) tdouble cc_default)) ::
 (___builtin_fabsf,
   Gfun(External (EF_builtin "__builtin_fabsf"
                   (mksignature (AST.Xsingle :: nil) AST.Xsingle cc_default))
     (tfloat :: nil) tfloat cc_default)) ::
 (___builtin_fsqrt,
   Gfun(External (EF_builtin "__builtin_fsqrt"
                   (mksignature (AST.Xfloat :: nil) AST.Xfloat cc_default))
     (tdouble :: nil) tdouble cc_default)) ::
 (___builtin_sqrt,
   Gfun(External (EF_builtin "__builtin_sqrt"
                   (mksignature (AST.Xfloat :: nil) AST.Xfloat cc_default))
     (tdouble :: nil) tdouble cc_default)) ::
 (___builtin_memcpy_aligned,
   Gfun(External (EF_builtin "__builtin_memcpy_aligned"
                   (mksignature
                     (AST.Xptr :: AST.Xptr :: AST.Xlong :: AST.Xlong :: nil)
                     AST.Xvoid cc_default))
     ((tptr tvoid) :: (tptr tvoid) :: tulong :: tulong :: nil) tvoid
     cc_default)) ::
 (___builtin_sel,
   Gfun(External (EF_builtin "__builtin_sel"
                   (mksignature (AST.Xbool :: nil) AST.Xvoid
                     {|cc_vararg:=(Some 1); cc_unproto:=false; cc_structret:=false|}))
     (tbool :: nil) tvoid
     {|cc_vararg:=(Some 1); cc_unproto:=false; cc_structret:=false|})) ::
 (___builtin_annot,
   Gfun(External (EF_builtin "__builtin_annot"
                   (mksignature (AST.Xptr :: nil) AST.Xvoid
                     {|cc_vararg:=(Some 1); cc_unproto:=false; cc_structret:=false|}))
     ((tptr tschar) :: nil) tvoid
     {|cc_vararg:=(Some 1); cc_unproto:=false; cc_structret:=false|})) ::
 (___builtin_annot_intval,
   Gfun(External (EF_builtin "__builtin_annot_intval"
                   (mksignature (AST.Xptr :: AST.Xint :: nil) AST.Xint
                     cc_default)) ((tptr tschar) :: tint :: nil) tint
     cc_default)) ::
 (___builtin_membar,
   Gfun(External (EF_builtin "__builtin_membar"
                   (mksignature nil AST.Xvoid cc_default)) nil tvoid
     cc_default)) ::
 (___builtin_va_start,
   Gfun(External (EF_builtin "__builtin_va_start"
                   (mksignature (AST.Xptr :: nil) AST.Xvoid cc_default))
     ((tptr tvoid) :: nil) tvoid cc_default)) ::
 (___builtin_va_arg,
   Gfun(External (EF_builtin "__builtin_va_arg"
                   (mksignature (AST.Xptr :: AST.Xint :: nil) AST.Xvoid
                     cc_default)) ((tptr tvoid) :: tuint :: nil) tvoid
     cc_default)) ::
 (___builtin_va_copy,
   Gfun(External (EF_builtin "__builtin_va_copy"
                   (mksignature (AST.Xptr :: AST.Xptr :: nil) AST.Xvoid
                     cc_default)) ((tptr tvoid) :: (tptr tvoid) :: nil) tvoid
     cc_default)) ::
 (___builtin_va_end,
   Gfun(External (EF_builtin "__builtin_va_end"
                   (mksignature (AST.Xptr :: nil) AST.Xvoid cc_default))
     ((tptr tvoid) :: nil) tvoid cc_default)) ::
 (___builtin_unreachable,
   Gfun(External (EF_builtin "__builtin_unreachable"
                   (mksignature nil AST.Xvoid cc_default)) nil tvoid
     cc_default)) ::
 (___builtin_expect,
   Gfun(External (EF_builtin "__builtin_expect"
                   (mksignature (AST.Xlong :: AST.Xlong :: nil) AST.Xlong
                     cc_default)) (tlong :: tlong :: nil) tlong cc_default)) ::
 (___builtin_fmax,
   Gfun(External (EF_builtin "__builtin_fmax"
                   (mksignature (AST.Xfloat :: AST.Xfloat :: nil) AST.Xfloat
                     cc_default)) (tdouble :: tdouble :: nil) tdouble
     cc_default)) ::
 (___builtin_fmin,
   Gfun(External (EF_builtin "__builtin_fmin"
                   (mksignature (AST.Xfloat :: AST.Xfloat :: nil) AST.Xfloat
                     cc_default)) (tdouble :: tdouble :: nil) tdouble
     cc_default)) ::
 (___builtin_fmadd,
   Gfun(External (EF_builtin "__builtin_fmadd"
                   (mksignature
                     (AST.Xfloat :: AST.Xfloat :: AST.Xfloat :: nil)
                     AST.Xfloat cc_default))
     (tdouble :: tdouble :: tdouble :: nil) tdouble cc_default)) ::
 (___builtin_fmsub,
   Gfun(External (EF_builtin "__builtin_fmsub"
                   (mksignature
                     (AST.Xfloat :: AST.Xfloat :: AST.Xfloat :: nil)
                     AST.Xfloat cc_default))
     (tdouble :: tdouble :: tdouble :: nil) tdouble cc_default)) ::
 (___builtin_fnmadd,
   Gfun(External (EF_builtin "__builtin_fnmadd"
                   (mksignature
                     (AST.Xfloat :: AST.Xfloat :: AST.Xfloat :: nil)
                     AST.Xfloat cc_default))
     (tdouble :: tdouble :: tdouble :: nil) tdouble cc_default)) ::
 (___builtin_fnmsub,
   Gfun(External (EF_builtin "__builtin_fnmsub"
                   (mksignature
                     (AST.Xfloat :: AST.Xfloat :: AST.Xfloat :: nil)
                     AST.Xfloat cc_default))
     (tdouble :: tdouble :: tdouble :: nil) tdouble cc_default)) ::
 (___builtin_read16_reversed,
   Gfun(External (EF_builtin "__builtin_read16_reversed"
                   (mksignature (AST.Xptr :: nil) AST.Xint16unsigned
                     cc_default)) ((tptr tushort) :: nil) tushort
     cc_default)) ::
 (___builtin_read32_reversed,
   Gfun(External (EF_builtin "__builtin_read32_reversed"
                   (mksignature (AST.Xptr :: nil) AST.Xint cc_default))
     ((tptr tuint) :: nil) tuint cc_default)) ::
 (___builtin_write16_reversed,
   Gfun(External (EF_builtin "__builtin_write16_reversed"
                   (mksignature (AST.Xptr :: AST.Xint16unsigned :: nil)
                     AST.Xvoid cc_default))
     ((tptr tushort) :: tushort :: nil) tvoid cc_default)) ::
 (___builtin_write32_reversed,
   Gfun(External (EF_builtin "__builtin_write32_reversed"
                   (mksignature (AST.Xptr :: AST.Xint :: nil) AST.Xvoid
                     cc_default)) ((tptr tuint) :: tuint :: nil) tvoid
     cc_default)) ::
 (___builtin_debug,
   Gfun(External (EF_external "__builtin_debug"
                   (mksignature (AST.Xint :: nil) AST.Xvoid
                     {|cc_vararg:=(Some 1); cc_unproto:=false; cc_structret:=false|}))
     (tint :: nil) tvoid
     {|cc_vararg:=(Some 1); cc_unproto:=false; cc_structret:=false|})) ::
 (_eb_input, Gvar v_eb_input) :: (_eb_output, Gvar v_eb_output) ::
 (_eb_out, Gvar v_eb_out) :: (_emit, Gfun(Internal f_emit)) ::
 (_begin_output, Gfun(Internal f_begin_output)) ::
 (_end_output, Gfun(Internal f_end_output)) :: (_dp, Gvar v_dp) ::
 (_vertical, Gvar v_vertical) :: (_horizontal, Gvar v_horizontal) ::
 (_open_cost, Gvar v_open_cost) :: (_extension, Gvar v_extension) ::
 (_mismatch, Gvar v_mismatch) :: (_n, Gvar v_n) ::
 (_cost_add, Gfun(Internal f_cost_add)) ::
 (_offer, Gfun(Internal f_offer)) ::
 (_diagonal, Gfun(Internal f_diagonal)) ::
 (_extend_minimum, Gfun(Internal f_extend_minimum)) ::
 (_offer_gaps, Gfun(Internal f_offer_gaps)) ::
 (_align_cell, Gfun(Internal f_align_cell)) ::
 (_align, Gfun(Internal f_align)) :: (_main, Gfun(Internal f_main)) :: nil).

Definition public_idents : list ident :=
(_main :: _eb_output :: _eb_input :: ___builtin_debug ::
 ___builtin_write32_reversed :: ___builtin_write16_reversed ::
 ___builtin_read32_reversed :: ___builtin_read16_reversed ::
 ___builtin_fnmsub :: ___builtin_fnmadd :: ___builtin_fmsub ::
 ___builtin_fmadd :: ___builtin_fmin :: ___builtin_fmax ::
 ___builtin_expect :: ___builtin_unreachable :: ___builtin_va_end ::
 ___builtin_va_copy :: ___builtin_va_arg :: ___builtin_va_start ::
 ___builtin_membar :: ___builtin_annot_intval :: ___builtin_annot ::
 ___builtin_sel :: ___builtin_memcpy_aligned :: ___builtin_sqrt ::
 ___builtin_fsqrt :: ___builtin_fabsf :: ___builtin_fabs ::
 ___builtin_ctzll :: ___builtin_ctzl :: ___builtin_ctz :: ___builtin_clzll ::
 ___builtin_clzl :: ___builtin_clz :: ___builtin_bswap16 ::
 ___builtin_bswap32 :: ___builtin_bswap :: ___builtin_bswap64 ::
 ___builtin_ais_annot :: ___compcert_i64_umulh :: ___compcert_i64_smulh ::
 ___compcert_i64_sar :: ___compcert_i64_shr :: ___compcert_i64_shl ::
 ___compcert_i64_umod :: ___compcert_i64_smod :: ___compcert_i64_udiv ::
 ___compcert_i64_sdiv :: ___compcert_i64_utof :: ___compcert_i64_stof ::
 ___compcert_i64_utod :: ___compcert_i64_stod :: ___compcert_i64_dtou ::
 ___compcert_i64_dtos :: ___compcert_va_composite ::
 ___compcert_va_float64 :: ___compcert_va_int64 :: ___compcert_va_int32 ::
 nil).

Definition prog : Clight.program := 
  mkprogram composites global_definitions public_idents _main Logic.I.


