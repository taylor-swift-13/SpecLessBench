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
  Definition source_file := "EVAL_V0.c".
  Definition normalized := true.
End Info.

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
Definition _aa : ident := $"aa".
Definition _bb : ident := $"bb".
Definition _begin_output : ident := $"begin_output".
Definition _c : ident := $"c".
Definition _code_ : ident := $"code_".
Definition _combine : ident := $"combine".
Definition _e : ident := $"e".
Definition _eb_input : ident := $"eb_input".
Definition _eb_out : ident := $"eb_out".
Definition _eb_output : ident := $"eb_output".
Definition _emit : ident := $"emit".
Definition _end_output : ident := $"end_output".
Definition _env_ : ident := $"env_".
Definition _envn : ident := $"envn".
Definition _err_ : ident := $"err_".
Definition _eval_rec : ident := $"eval_rec".
Definition _i : ident := $"i".
Definition _l : ident := $"l".
Definition _leaf : ident := $"leaf".
Definition _main : ident := $"main".
Definition _n : ident := $"n".
Definition _p : ident := $"p".
Definition _r : ident := $"r".
Definition _ready : ident := $"ready".
Definition _save : ident := $"save".
Definition _t : ident := $"t".
Definition _tags : ident := $"tags".
Definition _v : ident := $"v".
Definition _val_ : ident := $"val_".
Definition _x : ident := $"x".
Definition _t'1 : ident := 128%positive.
Definition _t'10 : ident := 137%positive.
Definition _t'11 : ident := 138%positive.
Definition _t'12 : ident := 139%positive.
Definition _t'13 : ident := 140%positive.
Definition _t'14 : ident := 141%positive.
Definition _t'15 : ident := 142%positive.
Definition _t'16 : ident := 143%positive.
Definition _t'17 : ident := 144%positive.
Definition _t'18 : ident := 145%positive.
Definition _t'19 : ident := 146%positive.
Definition _t'2 : ident := 129%positive.
Definition _t'20 : ident := 147%positive.
Definition _t'21 : ident := 148%positive.
Definition _t'22 : ident := 149%positive.
Definition _t'23 : ident := 150%positive.
Definition _t'24 : ident := 151%positive.
Definition _t'25 : ident := 152%positive.
Definition _t'26 : ident := 153%positive.
Definition _t'27 : ident := 154%positive.
Definition _t'28 : ident := 155%positive.
Definition _t'29 : ident := 156%positive.
Definition _t'3 : ident := 130%positive.
Definition _t'30 : ident := 157%positive.
Definition _t'31 : ident := 158%positive.
Definition _t'32 : ident := 159%positive.
Definition _t'4 : ident := 131%positive.
Definition _t'5 : ident := 132%positive.
Definition _t'6 : ident := 133%positive.
Definition _t'7 : ident := 134%positive.
Definition _t'8 : ident := 135%positive.
Definition _t'9 : ident := 136%positive.

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

Definition v_tags := {|
  gvar_info := (tarray tint 64);
  gvar_init := (Init_space 256 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_aa := {|
  gvar_info := (tarray tint 64);
  gvar_init := (Init_space 256 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_bb := {|
  gvar_info := (tarray tint 64);
  gvar_init := (Init_space 256 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_env_ := {|
  gvar_info := (tarray tint 8);
  gvar_init := (Init_space 32 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_envn := {|
  gvar_info := tint;
  gvar_init := (Init_space 4 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_ready := {|
  gvar_info := (tarray tint 64);
  gvar_init := (Init_space 256 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_code_ := {|
  gvar_info := (tarray tint 64);
  gvar_init := (Init_space 256 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_err_ := {|
  gvar_info := (tarray tint 64);
  gvar_init := (Init_space 256 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_val_ := {|
  gvar_info := (tarray tint 64);
  gvar_init := (Init_space 256 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition f_save := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_i, tint) :: (_c, tint) :: (_e, tint) :: (_v, tint) :: nil);
  fn_vars := nil;
  fn_temps := nil;
  fn_body :=
(Ssequence
  (Sassign
    (Ederef
      (Ebinop Oadd (Evar _ready (tarray tint 64)) (Etempvar _i tint)
        (tptr tint)) tint) (Econst_int (Int.repr 1) tint))
  (Ssequence
    (Sassign
      (Ederef
        (Ebinop Oadd (Evar _code_ (tarray tint 64)) (Etempvar _i tint)
          (tptr tint)) tint) (Etempvar _c tint))
    (Ssequence
      (Sassign
        (Ederef
          (Ebinop Oadd (Evar _err_ (tarray tint 64)) (Etempvar _i tint)
            (tptr tint)) tint) (Etempvar _e tint))
      (Sassign
        (Ederef
          (Ebinop Oadd (Evar _val_ (tarray tint 64)) (Etempvar _i tint)
            (tptr tint)) tint) (Etempvar _v tint)))))
|}.

Definition f_combine := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_i, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_t, tint) :: (_l, tint) :: (_r, tint) :: (_v, tint) ::
               (_t'7, tint) :: (_t'6, tint) :: (_t'5, tint) ::
               (_t'4, tint) :: (_t'3, tint) :: (_t'2, tint) ::
               (_t'1, tint) :: (_t'32, tint) :: (_t'31, tint) ::
               (_t'30, tint) :: (_t'29, tint) :: (_t'28, tint) ::
               (_t'27, tint) :: (_t'26, tint) :: (_t'25, tint) ::
               (_t'24, tint) :: (_t'23, tint) :: (_t'22, tint) ::
               (_t'21, tint) :: (_t'20, tint) :: (_t'19, tint) ::
               (_t'18, tint) :: (_t'17, tint) :: (_t'16, tint) ::
               (_t'15, tint) :: (_t'14, tint) :: (_t'13, tint) ::
               (_t'12, tint) :: (_t'11, tint) :: (_t'10, tint) ::
               (_t'9, tint) :: (_t'8, tint) :: nil);
  fn_body :=
(Ssequence
  (Sset _t
    (Ederef
      (Ebinop Oadd (Evar _tags (tarray tint 64)) (Etempvar _i tint)
        (tptr tint)) tint))
  (Ssequence
    (Sset _l
      (Ederef
        (Ebinop Oadd (Evar _aa (tarray tint 64)) (Etempvar _i tint)
          (tptr tint)) tint))
    (Ssequence
      (Sset _r
        (Ederef
          (Ebinop Oadd (Evar _bb (tarray tint 64)) (Etempvar _i tint)
            (tptr tint)) tint))
      (Ssequence
        (Sset _v (Econst_int (Int.repr 0) tint))
        (Ssequence
          (Ssequence
            (Sset _t'30
              (Ederef
                (Ebinop Oadd (Evar _code_ (tarray tint 64))
                  (Etempvar _l tint) (tptr tint)) tint))
            (Sifthenelse (Ebinop One (Etempvar _t'30 tint)
                           (Econst_int (Int.repr 0) tint) tint)
              (Ssequence
                (Ssequence
                  (Sset _t'31
                    (Ederef
                      (Ebinop Oadd (Evar _code_ (tarray tint 64))
                        (Etempvar _l tint) (tptr tint)) tint))
                  (Ssequence
                    (Sset _t'32
                      (Ederef
                        (Ebinop Oadd (Evar _err_ (tarray tint 64))
                          (Etempvar _l tint) (tptr tint)) tint))
                    (Scall None
                      (Evar _save (Tfunction
                                    (tint :: tint :: tint :: tint :: nil)
                                    tvoid cc_default))
                      ((Etempvar _i tint) :: (Etempvar _t'31 tint) ::
                       (Etempvar _t'32 tint) ::
                       (Econst_int (Int.repr 0) tint) :: nil))))
                (Sreturn None))
              Sskip))
          (Ssequence
            (Ssequence
              (Sifthenelse (Ebinop Oeq (Etempvar _t tint)
                             (Econst_int (Int.repr 8) tint) tint)
                (Sset _t'6 (Econst_int (Int.repr 1) tint))
                (Sset _t'6
                  (Ecast
                    (Ebinop Oeq (Etempvar _t tint)
                      (Econst_int (Int.repr 9) tint) tint) tbool)))
              (Sifthenelse (Etempvar _t'6 tint)
                (Ssequence
                  (Sifthenelse (Ebinop Oeq (Etempvar _t tint)
                                 (Econst_int (Int.repr 8) tint) tint)
                    (Ssequence
                      (Sset _t'29
                        (Ederef
                          (Ebinop Oadd (Evar _val_ (tarray tint 64))
                            (Etempvar _l tint) (tptr tint)) tint))
                      (Sset _t'1
                        (Ecast (Eunop Oneg (Etempvar _t'29 tint) tint) tint)))
                    (Ssequence
                      (Sset _t'28
                        (Ederef
                          (Ebinop Oadd (Evar _val_ (tarray tint 64))
                            (Etempvar _l tint) (tptr tint)) tint))
                      (Sset _t'1
                        (Ecast
                          (Ebinop Oeq (Etempvar _t'28 tint)
                            (Econst_int (Int.repr 0) tint) tint) tint))))
                  (Sset _v (Etempvar _t'1 tint)))
                (Ssequence
                  (Ssequence
                    (Sifthenelse (Ebinop Oeq (Etempvar _t tint)
                                   (Econst_int (Int.repr 6) tint) tint)
                      (Ssequence
                        (Sset _t'27
                          (Ederef
                            (Ebinop Oadd (Evar _val_ (tarray tint 64))
                              (Etempvar _l tint) (tptr tint)) tint))
                        (Sset _t'2
                          (Ecast
                            (Ebinop Oeq (Etempvar _t'27 tint)
                              (Econst_int (Int.repr 0) tint) tint) tbool)))
                      (Sset _t'2 (Econst_int (Int.repr 0) tint)))
                    (Sifthenelse (Etempvar _t'2 tint)
                      (Ssequence
                        (Scall None
                          (Evar _save (Tfunction
                                        (tint :: tint :: tint :: tint :: nil)
                                        tvoid cc_default))
                          ((Etempvar _i tint) ::
                           (Econst_int (Int.repr 0) tint) ::
                           (Eunop Oneg (Econst_int (Int.repr 1) tint) tint) ::
                           (Econst_int (Int.repr 0) tint) :: nil))
                        (Sreturn None))
                      Sskip))
                  (Ssequence
                    (Ssequence
                      (Sifthenelse (Ebinop Oeq (Etempvar _t tint)
                                     (Econst_int (Int.repr 7) tint) tint)
                        (Ssequence
                          (Sset _t'26
                            (Ederef
                              (Ebinop Oadd (Evar _val_ (tarray tint 64))
                                (Etempvar _l tint) (tptr tint)) tint))
                          (Sset _t'3
                            (Ecast
                              (Ebinop One (Etempvar _t'26 tint)
                                (Econst_int (Int.repr 0) tint) tint) tbool)))
                        (Sset _t'3 (Econst_int (Int.repr 0) tint)))
                      (Sifthenelse (Etempvar _t'3 tint)
                        (Ssequence
                          (Scall None
                            (Evar _save (Tfunction
                                          (tint :: tint :: tint :: tint ::
                                           nil) tvoid cc_default))
                            ((Etempvar _i tint) ::
                             (Econst_int (Int.repr 0) tint) ::
                             (Eunop Oneg (Econst_int (Int.repr 1) tint) tint) ::
                             (Econst_int (Int.repr 1) tint) :: nil))
                          (Sreturn None))
                        Sskip))
                    (Ssequence
                      (Ssequence
                        (Sset _t'23
                          (Ederef
                            (Ebinop Oadd (Evar _code_ (tarray tint 64))
                              (Etempvar _r tint) (tptr tint)) tint))
                        (Sifthenelse (Ebinop One (Etempvar _t'23 tint)
                                       (Econst_int (Int.repr 0) tint) tint)
                          (Ssequence
                            (Ssequence
                              (Sset _t'24
                                (Ederef
                                  (Ebinop Oadd (Evar _code_ (tarray tint 64))
                                    (Etempvar _r tint) (tptr tint)) tint))
                              (Ssequence
                                (Sset _t'25
                                  (Ederef
                                    (Ebinop Oadd
                                      (Evar _err_ (tarray tint 64))
                                      (Etempvar _r tint) (tptr tint)) tint))
                                (Scall None
                                  (Evar _save (Tfunction
                                                (tint :: tint :: tint ::
                                                 tint :: nil) tvoid
                                                cc_default))
                                  ((Etempvar _i tint) ::
                                   (Etempvar _t'24 tint) ::
                                   (Etempvar _t'25 tint) ::
                                   (Econst_int (Int.repr 0) tint) :: nil))))
                            (Sreturn None))
                          Sskip))
                      (Sifthenelse (Ebinop Oeq (Etempvar _t tint)
                                     (Econst_int (Int.repr 2) tint) tint)
                        (Ssequence
                          (Sset _t'21
                            (Ederef
                              (Ebinop Oadd (Evar _val_ (tarray tint 64))
                                (Etempvar _l tint) (tptr tint)) tint))
                          (Ssequence
                            (Sset _t'22
                              (Ederef
                                (Ebinop Oadd (Evar _val_ (tarray tint 64))
                                  (Etempvar _r tint) (tptr tint)) tint))
                            (Sset _v
                              (Ebinop Oadd (Etempvar _t'21 tint)
                                (Etempvar _t'22 tint) tint))))
                        (Sifthenelse (Ebinop Oeq (Etempvar _t tint)
                                       (Econst_int (Int.repr 3) tint) tint)
                          (Ssequence
                            (Sset _t'19
                              (Ederef
                                (Ebinop Oadd (Evar _val_ (tarray tint 64))
                                  (Etempvar _l tint) (tptr tint)) tint))
                            (Ssequence
                              (Sset _t'20
                                (Ederef
                                  (Ebinop Oadd (Evar _val_ (tarray tint 64))
                                    (Etempvar _r tint) (tptr tint)) tint))
                              (Sset _v
                                (Ebinop Osub (Etempvar _t'19 tint)
                                  (Etempvar _t'20 tint) tint))))
                          (Sifthenelse (Ebinop Oeq (Etempvar _t tint)
                                         (Econst_int (Int.repr 4) tint) tint)
                            (Ssequence
                              (Sset _t'17
                                (Ederef
                                  (Ebinop Oadd (Evar _val_ (tarray tint 64))
                                    (Etempvar _l tint) (tptr tint)) tint))
                              (Ssequence
                                (Sset _t'18
                                  (Ederef
                                    (Ebinop Oadd
                                      (Evar _val_ (tarray tint 64))
                                      (Etempvar _r tint) (tptr tint)) tint))
                                (Sset _v
                                  (Ebinop Olt (Etempvar _t'17 tint)
                                    (Etempvar _t'18 tint) tint))))
                            (Sifthenelse (Ebinop Oeq (Etempvar _t tint)
                                           (Econst_int (Int.repr 5) tint)
                                           tint)
                              (Ssequence
                                (Sset _t'15
                                  (Ederef
                                    (Ebinop Oadd
                                      (Evar _val_ (tarray tint 64))
                                      (Etempvar _l tint) (tptr tint)) tint))
                                (Ssequence
                                  (Sset _t'16
                                    (Ederef
                                      (Ebinop Oadd
                                        (Evar _val_ (tarray tint 64))
                                        (Etempvar _r tint) (tptr tint)) tint))
                                  (Sset _v
                                    (Ebinop Oeq (Etempvar _t'15 tint)
                                      (Etempvar _t'16 tint) tint))))
                              (Sifthenelse (Ebinop Oeq (Etempvar _t tint)
                                             (Econst_int (Int.repr 6) tint)
                                             tint)
                                (Ssequence
                                  (Ssequence
                                    (Sset _t'13
                                      (Ederef
                                        (Ebinop Oadd
                                          (Evar _val_ (tarray tint 64))
                                          (Etempvar _l tint) (tptr tint))
                                        tint))
                                    (Sifthenelse (Ebinop One
                                                   (Etempvar _t'13 tint)
                                                   (Econst_int (Int.repr 0) tint)
                                                   tint)
                                      (Ssequence
                                        (Sset _t'14
                                          (Ederef
                                            (Ebinop Oadd
                                              (Evar _val_ (tarray tint 64))
                                              (Etempvar _r tint) (tptr tint))
                                            tint))
                                        (Sset _t'4
                                          (Ecast
                                            (Ebinop One (Etempvar _t'14 tint)
                                              (Econst_int (Int.repr 0) tint)
                                              tint) tbool)))
                                      (Sset _t'4
                                        (Econst_int (Int.repr 0) tint))))
                                  (Sset _v (Etempvar _t'4 tint)))
                                (Sifthenelse (Ebinop Oeq (Etempvar _t tint)
                                               (Econst_int (Int.repr 7) tint)
                                               tint)
                                  (Ssequence
                                    (Ssequence
                                      (Sset _t'11
                                        (Ederef
                                          (Ebinop Oadd
                                            (Evar _val_ (tarray tint 64))
                                            (Etempvar _l tint) (tptr tint))
                                          tint))
                                      (Sifthenelse (Ebinop One
                                                     (Etempvar _t'11 tint)
                                                     (Econst_int (Int.repr 0) tint)
                                                     tint)
                                        (Sset _t'5
                                          (Econst_int (Int.repr 1) tint))
                                        (Ssequence
                                          (Sset _t'12
                                            (Ederef
                                              (Ebinop Oadd
                                                (Evar _val_ (tarray tint 64))
                                                (Etempvar _r tint)
                                                (tptr tint)) tint))
                                          (Sset _t'5
                                            (Ecast
                                              (Ebinop One
                                                (Etempvar _t'12 tint)
                                                (Econst_int (Int.repr 0) tint)
                                                tint) tbool)))))
                                    (Sset _v (Etempvar _t'5 tint)))
                                  (Ssequence
                                    (Ssequence
                                      (Sset _t'10
                                        (Ederef
                                          (Ebinop Oadd
                                            (Evar _val_ (tarray tint 64))
                                            (Etempvar _r tint) (tptr tint))
                                          tint))
                                      (Sifthenelse (Ebinop Oeq
                                                     (Etempvar _t'10 tint)
                                                     (Econst_int (Int.repr 0) tint)
                                                     tint)
                                        (Ssequence
                                          (Scall None
                                            (Evar _save (Tfunction
                                                          (tint :: tint ::
                                                           tint :: tint ::
                                                           nil) tvoid
                                                          cc_default))
                                            ((Etempvar _i tint) ::
                                             (Econst_int (Int.repr 3) tint) ::
                                             (Etempvar _i tint) ::
                                             (Econst_int (Int.repr 0) tint) ::
                                             nil))
                                          (Sreturn None))
                                        Sskip))
                                    (Ssequence
                                      (Sset _t'8
                                        (Ederef
                                          (Ebinop Oadd
                                            (Evar _val_ (tarray tint 64))
                                            (Etempvar _l tint) (tptr tint))
                                          tint))
                                      (Ssequence
                                        (Sset _t'9
                                          (Ederef
                                            (Ebinop Oadd
                                              (Evar _val_ (tarray tint 64))
                                              (Etempvar _r tint) (tptr tint))
                                            tint))
                                        (Sset _v
                                          (Ebinop Odiv (Etempvar _t'8 tint)
                                            (Etempvar _t'9 tint) tint))))))))))))))))
            (Ssequence
              (Sifthenelse (Ebinop Olt (Etempvar _v tint)
                             (Eunop Oneg (Econst_int (Int.repr 32768) tint)
                               tint) tint)
                (Sset _t'7 (Econst_int (Int.repr 1) tint))
                (Sset _t'7
                  (Ecast
                    (Ebinop Ogt (Etempvar _v tint)
                      (Econst_int (Int.repr 32767) tint) tint) tbool)))
              (Sifthenelse (Etempvar _t'7 tint)
                (Scall None
                  (Evar _save (Tfunction
                                (tint :: tint :: tint :: tint :: nil) tvoid
                                cc_default))
                  ((Etempvar _i tint) :: (Econst_int (Int.repr 2) tint) ::
                   (Etempvar _i tint) :: (Econst_int (Int.repr 0) tint) ::
                   nil))
                (Scall None
                  (Evar _save (Tfunction
                                (tint :: tint :: tint :: tint :: nil) tvoid
                                cc_default))
                  ((Etempvar _i tint) :: (Econst_int (Int.repr 0) tint) ::
                   (Eunop Oneg (Econst_int (Int.repr 1) tint) tint) ::
                   (Etempvar _v tint) :: nil))))))))))
|}.

Definition f_leaf := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := ((_i, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_t, tint) :: (_t'5, tint) :: (_t'4, tint) :: (_t'3, tint) ::
               (_t'2, tint) :: (_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Sset _t
    (Ederef
      (Ebinop Oadd (Evar _tags (tarray tint 64)) (Etempvar _i tint)
        (tptr tint)) tint))
  (Ssequence
    (Sifthenelse (Ebinop Oeq (Etempvar _t tint)
                   (Econst_int (Int.repr 0) tint) tint)
      (Ssequence
        (Ssequence
          (Sset _t'5
            (Ederef
              (Ebinop Oadd (Evar _aa (tarray tint 64)) (Etempvar _i tint)
                (tptr tint)) tint))
          (Scall None
            (Evar _save (Tfunction (tint :: tint :: tint :: tint :: nil)
                          tvoid cc_default))
            ((Etempvar _i tint) :: (Econst_int (Int.repr 0) tint) ::
             (Eunop Oneg (Econst_int (Int.repr 1) tint) tint) ::
             (Etempvar _t'5 tint) :: nil)))
        (Sreturn (Some (Econst_int (Int.repr 1) tint))))
      Sskip)
    (Ssequence
      (Sifthenelse (Ebinop Oeq (Etempvar _t tint)
                     (Econst_int (Int.repr 1) tint) tint)
        (Ssequence
          (Ssequence
            (Sset _t'1
              (Ederef
                (Ebinop Oadd (Evar _aa (tarray tint 64)) (Etempvar _i tint)
                  (tptr tint)) tint))
            (Ssequence
              (Sset _t'2 (Evar _envn tint))
              (Sifthenelse (Ebinop Oge (Etempvar _t'1 tint)
                             (Etempvar _t'2 tint) tint)
                (Scall None
                  (Evar _save (Tfunction
                                (tint :: tint :: tint :: tint :: nil) tvoid
                                cc_default))
                  ((Etempvar _i tint) :: (Econst_int (Int.repr 1) tint) ::
                   (Etempvar _i tint) :: (Econst_int (Int.repr 0) tint) ::
                   nil))
                (Ssequence
                  (Sset _t'3
                    (Ederef
                      (Ebinop Oadd (Evar _aa (tarray tint 64))
                        (Etempvar _i tint) (tptr tint)) tint))
                  (Ssequence
                    (Sset _t'4
                      (Ederef
                        (Ebinop Oadd (Evar _env_ (tarray tint 8))
                          (Etempvar _t'3 tint) (tptr tint)) tint))
                    (Scall None
                      (Evar _save (Tfunction
                                    (tint :: tint :: tint :: tint :: nil)
                                    tvoid cc_default))
                      ((Etempvar _i tint) ::
                       (Econst_int (Int.repr 0) tint) ::
                       (Eunop Oneg (Econst_int (Int.repr 1) tint) tint) ::
                       (Etempvar _t'4 tint) :: nil)))))))
          (Sreturn (Some (Econst_int (Int.repr 1) tint))))
        Sskip)
      (Ssequence
        (Sifthenelse (Ebinop Ogt (Etempvar _t tint)
                       (Econst_int (Int.repr 10) tint) tint)
          (Ssequence
            (Scall None
              (Evar _save (Tfunction (tint :: tint :: tint :: tint :: nil)
                            tvoid cc_default))
              ((Etempvar _i tint) :: (Econst_int (Int.repr 4) tint) ::
               (Etempvar _i tint) :: (Econst_int (Int.repr 0) tint) :: nil))
            (Sreturn (Some (Econst_int (Int.repr 1) tint))))
          Sskip)
        (Sreturn (Some (Econst_int (Int.repr 0) tint)))))))
|}.

Definition f_eval_rec := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_i, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_t, tint) :: (_t'7, tint) :: (_t'6, tint) :: (_t'5, tint) ::
               (_t'4, tint) :: (_t'3, tint) :: (_t'2, tint) ::
               (_t'1, tint) :: (_t'16, tint) :: (_t'15, tint) ::
               (_t'14, tint) :: (_t'13, tint) :: (_t'12, tint) ::
               (_t'11, tint) :: (_t'10, tint) :: (_t'9, tint) ::
               (_t'8, tint) :: nil);
  fn_body :=
(Ssequence
  (Sset _t
    (Ederef
      (Ebinop Oadd (Evar _tags (tarray tint 64)) (Etempvar _i tint)
        (tptr tint)) tint))
  (Ssequence
    (Ssequence
      (Sset _t'16
        (Ederef
          (Ebinop Oadd (Evar _ready (tarray tint 64)) (Etempvar _i tint)
            (tptr tint)) tint))
      (Sifthenelse (Etempvar _t'16 tint) (Sreturn None) Sskip))
    (Ssequence
      (Ssequence
        (Scall (Some _t'1)
          (Evar _leaf (Tfunction (tint :: nil) tint cc_default))
          ((Etempvar _i tint) :: nil))
        (Sifthenelse (Etempvar _t'1 tint) (Sreturn None) Sskip))
      (Ssequence
        (Ssequence
          (Sset _t'15
            (Ederef
              (Ebinop Oadd (Evar _aa (tarray tint 64)) (Etempvar _i tint)
                (tptr tint)) tint))
          (Scall None
            (Evar _eval_rec (Tfunction (tint :: nil) tvoid cc_default))
            ((Etempvar _t'15 tint) :: nil)))
        (Ssequence
          (Ssequence
            (Ssequence
              (Ssequence
                (Ssequence
                  (Ssequence
                    (Sset _t'13
                      (Ederef
                        (Ebinop Oadd (Evar _aa (tarray tint 64))
                          (Etempvar _i tint) (tptr tint)) tint))
                    (Ssequence
                      (Sset _t'14
                        (Ederef
                          (Ebinop Oadd (Evar _code_ (tarray tint 64))
                            (Etempvar _t'13 tint) (tptr tint)) tint))
                      (Sifthenelse (Ebinop Oeq (Etempvar _t'14 tint)
                                     (Econst_int (Int.repr 0) tint) tint)
                        (Sset _t'2
                          (Ecast
                            (Ebinop One (Etempvar _t tint)
                              (Econst_int (Int.repr 8) tint) tint) tbool))
                        (Sset _t'2 (Econst_int (Int.repr 0) tint)))))
                  (Sifthenelse (Etempvar _t'2 tint)
                    (Sset _t'3
                      (Ecast
                        (Ebinop One (Etempvar _t tint)
                          (Econst_int (Int.repr 9) tint) tint) tbool))
                    (Sset _t'3 (Econst_int (Int.repr 0) tint))))
                (Sifthenelse (Etempvar _t'3 tint)
                  (Ssequence
                    (Sifthenelse (Ebinop Oeq (Etempvar _t tint)
                                   (Econst_int (Int.repr 6) tint) tint)
                      (Ssequence
                        (Sset _t'11
                          (Ederef
                            (Ebinop Oadd (Evar _aa (tarray tint 64))
                              (Etempvar _i tint) (tptr tint)) tint))
                        (Ssequence
                          (Sset _t'12
                            (Ederef
                              (Ebinop Oadd (Evar _val_ (tarray tint 64))
                                (Etempvar _t'11 tint) (tptr tint)) tint))
                          (Sset _t'5
                            (Ecast
                              (Ebinop Oeq (Etempvar _t'12 tint)
                                (Econst_int (Int.repr 0) tint) tint) tbool))))
                      (Sset _t'5 (Econst_int (Int.repr 0) tint)))
                    (Sset _t'4
                      (Ecast (Eunop Onotbool (Etempvar _t'5 tint) tint)
                        tbool)))
                  (Sset _t'4 (Econst_int (Int.repr 0) tint))))
              (Sifthenelse (Etempvar _t'4 tint)
                (Ssequence
                  (Sifthenelse (Ebinop Oeq (Etempvar _t tint)
                                 (Econst_int (Int.repr 7) tint) tint)
                    (Ssequence
                      (Sset _t'9
                        (Ederef
                          (Ebinop Oadd (Evar _aa (tarray tint 64))
                            (Etempvar _i tint) (tptr tint)) tint))
                      (Ssequence
                        (Sset _t'10
                          (Ederef
                            (Ebinop Oadd (Evar _val_ (tarray tint 64))
                              (Etempvar _t'9 tint) (tptr tint)) tint))
                        (Sset _t'7
                          (Ecast
                            (Ebinop One (Etempvar _t'10 tint)
                              (Econst_int (Int.repr 0) tint) tint) tbool))))
                    (Sset _t'7 (Econst_int (Int.repr 0) tint)))
                  (Sset _t'6
                    (Ecast (Eunop Onotbool (Etempvar _t'7 tint) tint) tbool)))
                (Sset _t'6 (Econst_int (Int.repr 0) tint))))
            (Sifthenelse (Etempvar _t'6 tint)
              (Ssequence
                (Sset _t'8
                  (Ederef
                    (Ebinop Oadd (Evar _bb (tarray tint 64))
                      (Etempvar _i tint) (tptr tint)) tint))
                (Scall None
                  (Evar _eval_rec (Tfunction (tint :: nil) tvoid cc_default))
                  ((Etempvar _t'8 tint) :: nil)))
              Sskip))
          (Scall None
            (Evar _combine (Tfunction (tint :: nil) tvoid cc_default))
            ((Etempvar _i tint) :: nil)))))))
|}.

Definition f_main := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := nil;
  fn_vars := nil;
  fn_temps := ((_n, tint) :: (_i, tint) :: (_p, tint) :: (_t'5, tint) ::
               (_t'4, tint) :: (_t'3, tint) :: (_t'2, tint) ::
               (_t'1, tint) :: (_t'14, tint) :: (_t'13, tint) ::
               (_t'12, tint) :: (_t'11, tint) :: (_t'10, tint) ::
               (_t'9, tint) :: (_t'8, tint) :: (_t'7, tint) ::
               (_t'6, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Sset _n
      (Ederef
        (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
          (Econst_int (Int.repr 0) tint) (tptr tint)) tint))
    (Ssequence
      (Sset _p (Econst_int (Int.repr 2) tint))
      (Ssequence
        (Scall None (Evar _begin_output (Tfunction nil tvoid cc_default))
          nil)
        (Ssequence
          (Ssequence
            (Sset _t'14
              (Ederef
                (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
                  (Econst_int (Int.repr 1) tint) (tptr tint)) tint))
            (Sassign (Evar _envn tint) (Etempvar _t'14 tint)))
          (Ssequence
            (Ssequence
              (Sset _i (Econst_int (Int.repr 0) tint))
              (Sloop
                (Ssequence
                  (Ssequence
                    (Sset _t'13 (Evar _envn tint))
                    (Sifthenelse (Ebinop Olt (Etempvar _i tint)
                                   (Etempvar _t'13 tint) tint)
                      Sskip
                      Sbreak))
                  (Ssequence
                    (Ssequence
                      (Sset _t'1 (Etempvar _p tint))
                      (Sset _p
                        (Ebinop Oadd (Etempvar _t'1 tint)
                          (Econst_int (Int.repr 1) tint) tint)))
                    (Ssequence
                      (Sset _t'12
                        (Ederef
                          (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
                            (Etempvar _t'1 tint) (tptr tint)) tint))
                      (Sassign
                        (Ederef
                          (Ebinop Oadd (Evar _env_ (tarray tint 8))
                            (Etempvar _i tint) (tptr tint)) tint)
                        (Etempvar _t'12 tint)))))
                (Sset _i
                  (Ebinop Oadd (Etempvar _i tint)
                    (Econst_int (Int.repr 1) tint) tint))))
            (Ssequence
              (Ssequence
                (Sset _i (Econst_int (Int.repr 0) tint))
                (Sloop
                  (Ssequence
                    (Sifthenelse (Ebinop Olt (Etempvar _i tint)
                                   (Etempvar _n tint) tint)
                      Sskip
                      Sbreak)
                    (Ssequence
                      (Ssequence
                        (Ssequence
                          (Sset _t'2 (Etempvar _p tint))
                          (Sset _p
                            (Ebinop Oadd (Etempvar _t'2 tint)
                              (Econst_int (Int.repr 1) tint) tint)))
                        (Ssequence
                          (Sset _t'11
                            (Ederef
                              (Ebinop Oadd
                                (Evar _eb_input (tarray tint 8192))
                                (Etempvar _t'2 tint) (tptr tint)) tint))
                          (Sassign
                            (Ederef
                              (Ebinop Oadd (Evar _tags (tarray tint 64))
                                (Etempvar _i tint) (tptr tint)) tint)
                            (Etempvar _t'11 tint))))
                      (Ssequence
                        (Ssequence
                          (Ssequence
                            (Sset _t'3 (Etempvar _p tint))
                            (Sset _p
                              (Ebinop Oadd (Etempvar _t'3 tint)
                                (Econst_int (Int.repr 1) tint) tint)))
                          (Ssequence
                            (Sset _t'10
                              (Ederef
                                (Ebinop Oadd
                                  (Evar _eb_input (tarray tint 8192))
                                  (Etempvar _t'3 tint) (tptr tint)) tint))
                            (Sassign
                              (Ederef
                                (Ebinop Oadd (Evar _aa (tarray tint 64))
                                  (Etempvar _i tint) (tptr tint)) tint)
                              (Etempvar _t'10 tint))))
                        (Ssequence
                          (Ssequence
                            (Ssequence
                              (Sset _t'4 (Etempvar _p tint))
                              (Sset _p
                                (Ebinop Oadd (Etempvar _t'4 tint)
                                  (Econst_int (Int.repr 1) tint) tint)))
                            (Ssequence
                              (Sset _t'9
                                (Ederef
                                  (Ebinop Oadd
                                    (Evar _eb_input (tarray tint 8192))
                                    (Etempvar _t'4 tint) (tptr tint)) tint))
                              (Sassign
                                (Ederef
                                  (Ebinop Oadd (Evar _bb (tarray tint 64))
                                    (Etempvar _i tint) (tptr tint)) tint)
                                (Etempvar _t'9 tint))))
                          (Ssequence
                            (Sassign
                              (Ederef
                                (Ebinop Oadd (Evar _ready (tarray tint 64))
                                  (Etempvar _i tint) (tptr tint)) tint)
                              (Econst_int (Int.repr 0) tint))
                            (Ssequence
                              (Sassign
                                (Ederef
                                  (Ebinop Oadd (Evar _code_ (tarray tint 64))
                                    (Etempvar _i tint) (tptr tint)) tint)
                                (Econst_int (Int.repr 0) tint))
                              (Ssequence
                                (Sassign
                                  (Ederef
                                    (Ebinop Oadd
                                      (Evar _err_ (tarray tint 64))
                                      (Etempvar _i tint) (tptr tint)) tint)
                                  (Eunop Oneg (Econst_int (Int.repr 1) tint)
                                    tint))
                                (Sassign
                                  (Ederef
                                    (Ebinop Oadd
                                      (Evar _val_ (tarray tint 64))
                                      (Etempvar _i tint) (tptr tint)) tint)
                                  (Econst_int (Int.repr 0) tint)))))))))
                  (Sset _i
                    (Ebinop Oadd (Etempvar _i tint)
                      (Econst_int (Int.repr 1) tint) tint))))
              (Ssequence
                (Scall None
                  (Evar _eval_rec (Tfunction (tint :: nil) tvoid cc_default))
                  ((Ebinop Osub (Etempvar _n tint)
                     (Econst_int (Int.repr 1) tint) tint) :: nil))
                (Ssequence
                  (Ssequence
                    (Sset _t'8
                      (Ederef
                        (Ebinop Oadd (Evar _code_ (tarray tint 64))
                          (Ebinop Osub (Etempvar _n tint)
                            (Econst_int (Int.repr 1) tint) tint) (tptr tint))
                        tint))
                    (Scall None
                      (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
                      ((Etempvar _t'8 tint) :: nil)))
                  (Ssequence
                    (Ssequence
                      (Sset _t'7
                        (Ederef
                          (Ebinop Oadd (Evar _err_ (tarray tint 64))
                            (Ebinop Osub (Etempvar _n tint)
                              (Econst_int (Int.repr 1) tint) tint)
                            (tptr tint)) tint))
                      (Scall None
                        (Evar _emit (Tfunction (tint :: nil) tvoid
                                      cc_default))
                        ((Etempvar _t'7 tint) :: nil)))
                    (Ssequence
                      (Ssequence
                        (Sset _t'6
                          (Ederef
                            (Ebinop Oadd (Evar _val_ (tarray tint 64))
                              (Ebinop Osub (Etempvar _n tint)
                                (Econst_int (Int.repr 1) tint) tint)
                              (tptr tint)) tint))
                        (Scall None
                          (Evar _emit (Tfunction (tint :: nil) tvoid
                                        cc_default))
                          ((Etempvar _t'6 tint) :: nil)))
                      (Ssequence
                        (Scall (Some _t'5)
                          (Evar _end_output (Tfunction nil tint cc_default))
                          nil)
                        (Sreturn (Some (Etempvar _t'5 tint))))))))))))))
  (Sreturn (Some (Econst_int (Int.repr 0) tint))))
|}.

Definition composites : list composite_definition :=
nil.

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
 (_end_output, Gfun(Internal f_end_output)) :: (_tags, Gvar v_tags) ::
 (_aa, Gvar v_aa) :: (_bb, Gvar v_bb) :: (_env_, Gvar v_env_) ::
 (_envn, Gvar v_envn) :: (_ready, Gvar v_ready) :: (_code_, Gvar v_code_) ::
 (_err_, Gvar v_err_) :: (_val_, Gvar v_val_) ::
 (_save, Gfun(Internal f_save)) :: (_combine, Gfun(Internal f_combine)) ::
 (_leaf, Gfun(Internal f_leaf)) :: (_eval_rec, Gfun(Internal f_eval_rec)) ::
 (_main, Gfun(Internal f_main)) :: nil).

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


