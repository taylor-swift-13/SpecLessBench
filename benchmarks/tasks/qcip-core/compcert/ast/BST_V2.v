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
  Definition source_file := "BST_V2.c".
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
Definition _arena : ident := $"arena".
Definition _b : ident := $"b".
Definition _begin_output : ident := $"begin_output".
Definition _eb_input : ident := $"eb_input".
Definition _eb_out : ident := $"eb_out".
Definition _eb_output : ident := $"eb_output".
Definition _emit : ident := $"emit".
Definition _end_output : ident := $"end_output".
Definition _erase : ident := $"erase".
Definition _i : ident := $"i".
Definition _initial_insert : ident := $"initial_insert".
Definition _k : ident := $"k".
Definition _key : ident := $"key".
Definition _left : ident := $"left".
Definition _live : ident := $"live".
Definition _lookup : ident := $"lookup".
Definition _main : ident := $"main".
Definition _n : ident := $"n".
Definition _new_node : ident := $"new_node".
Definition _node : ident := $"node".
Definition _op : ident := $"op".
Definition _p : ident := $"p".
Definition _pos : ident := $"pos".
Definition _project : ident := $"project".
Definition _pushdown_left : ident := $"pushdown_left".
Definition _q : ident := $"q".
Definition _retire : ident := $"retire".
Definition _right : ident := $"right".
Definition _root : ident := $"root".
Definition _turn_left : ident := $"turn_left".
Definition _used : ident := $"used".
Definition _v : ident := $"v".
Definition _value : ident := $"value".
Definition _x : ident := $"x".
Definition _t'1 : ident := 128%positive.
Definition _t'2 : ident := 129%positive.
Definition _t'3 : ident := 130%positive.
Definition _t'4 : ident := 131%positive.
Definition _t'5 : ident := 132%positive.
Definition _t'6 : ident := 133%positive.
Definition _t'7 : ident := 134%positive.

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

Definition v_arena := {|
  gvar_info := (tarray (Tstruct _node noattr) 32);
  gvar_init := (Init_space 1024 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_used := {|
  gvar_info := tint;
  gvar_init := (Init_space 4 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_root := {|
  gvar_info := (tptr (Tstruct _node noattr));
  gvar_init := (Init_space 8 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition f_new_node := {|
  fn_return := (tptr (Tstruct _node noattr));
  fn_callconv := cc_default;
  fn_params := ((_k, tint) :: (_v, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_p, (tptr (Tstruct _node noattr))) :: (_t'2, tint) ::
               (_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Sset _t'2 (Evar _used tint))
    (Sset _p
      (Ebinop Oadd (Evar _arena (tarray (Tstruct _node noattr) 32))
        (Etempvar _t'2 tint) (tptr (Tstruct _node noattr)))))
  (Ssequence
    (Ssequence
      (Sset _t'1 (Evar _used tint))
      (Sassign (Evar _used tint)
        (Ebinop Oadd (Etempvar _t'1 tint) (Econst_int (Int.repr 1) tint)
          tint)))
    (Ssequence
      (Sassign
        (Efield
          (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
            (Tstruct _node noattr)) _key tint) (Etempvar _k tint))
      (Ssequence
        (Sassign
          (Efield
            (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
              (Tstruct _node noattr)) _value tint) (Etempvar _v tint))
        (Ssequence
          (Sassign
            (Efield
              (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
                (Tstruct _node noattr)) _live tint)
            (Econst_int (Int.repr 1) tint))
          (Ssequence
            (Sassign
              (Efield
                (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
                  (Tstruct _node noattr)) _left
                (tptr (Tstruct _node noattr)))
              (Ecast (Econst_int (Int.repr 0) tint) (tptr tvoid)))
            (Ssequence
              (Sassign
                (Efield
                  (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
                    (Tstruct _node noattr)) _right
                  (tptr (Tstruct _node noattr)))
                (Ecast (Econst_int (Int.repr 0) tint) (tptr tvoid)))
              (Sreturn (Some (Etempvar _p (tptr (Tstruct _node noattr))))))))))))
|}.

Definition f_retire := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_p, (tptr (Tstruct _node noattr))) :: nil);
  fn_vars := nil;
  fn_temps := nil;
  fn_body :=
(Sassign
  (Efield
    (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
      (Tstruct _node noattr)) _live tint) (Econst_int (Int.repr 0) tint))
|}.

Definition f_initial_insert := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_k, tint) :: (_v, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_p, (tptr (tptr (Tstruct _node noattr)))) ::
               (_t'1, (tptr (Tstruct _node noattr))) ::
               (_t'6, (tptr (Tstruct _node noattr))) ::
               (_t'5, (tptr (Tstruct _node noattr))) ::
               (_t'4, (tptr (Tstruct _node noattr))) :: (_t'3, tint) ::
               (_t'2, (tptr (Tstruct _node noattr))) :: nil);
  fn_body :=
(Ssequence
  (Sset _p
    (Eaddrof (Evar _root (tptr (Tstruct _node noattr)))
      (tptr (tptr (Tstruct _node noattr)))))
  (Ssequence
    (Sloop
      (Ssequence
        (Ssequence
          (Sset _t'6
            (Ederef (Etempvar _p (tptr (tptr (Tstruct _node noattr))))
              (tptr (Tstruct _node noattr))))
          (Sifthenelse (Ebinop One
                         (Etempvar _t'6 (tptr (Tstruct _node noattr)))
                         (Ecast (Econst_int (Int.repr 0) tint) (tptr tvoid))
                         tint)
            Sskip
            Sbreak))
        (Ssequence
          (Sset _t'2
            (Ederef (Etempvar _p (tptr (tptr (Tstruct _node noattr))))
              (tptr (Tstruct _node noattr))))
          (Ssequence
            (Sset _t'3
              (Efield
                (Ederef (Etempvar _t'2 (tptr (Tstruct _node noattr)))
                  (Tstruct _node noattr)) _key tint))
            (Sifthenelse (Ebinop Olt (Etempvar _k tint) (Etempvar _t'3 tint)
                           tint)
              (Ssequence
                (Sset _t'5
                  (Ederef (Etempvar _p (tptr (tptr (Tstruct _node noattr))))
                    (tptr (Tstruct _node noattr))))
                (Sset _p
                  (Eaddrof
                    (Efield
                      (Ederef (Etempvar _t'5 (tptr (Tstruct _node noattr)))
                        (Tstruct _node noattr)) _left
                      (tptr (Tstruct _node noattr)))
                    (tptr (tptr (Tstruct _node noattr))))))
              (Ssequence
                (Sset _t'4
                  (Ederef (Etempvar _p (tptr (tptr (Tstruct _node noattr))))
                    (tptr (Tstruct _node noattr))))
                (Sset _p
                  (Eaddrof
                    (Efield
                      (Ederef (Etempvar _t'4 (tptr (Tstruct _node noattr)))
                        (Tstruct _node noattr)) _right
                      (tptr (Tstruct _node noattr)))
                    (tptr (tptr (Tstruct _node noattr))))))))))
      Sskip)
    (Ssequence
      (Scall (Some _t'1)
        (Evar _new_node (Tfunction (tint :: tint :: nil)
                          (tptr (Tstruct _node noattr)) cc_default))
        ((Etempvar _k tint) :: (Etempvar _v tint) :: nil))
      (Sassign
        (Ederef (Etempvar _p (tptr (tptr (Tstruct _node noattr))))
          (tptr (Tstruct _node noattr)))
        (Etempvar _t'1 (tptr (Tstruct _node noattr)))))))
|}.

Definition f_turn_left := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_b, (tptr (tptr (Tstruct _node noattr)))) ::
                (_p, (tptr (Tstruct _node noattr))) ::
                (_q, (tptr (Tstruct _node noattr))) :: nil);
  fn_vars := nil;
  fn_temps := ((_t'1, (tptr (Tstruct _node noattr))) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Sset _t'1
      (Efield
        (Ederef (Etempvar _q (tptr (Tstruct _node noattr)))
          (Tstruct _node noattr)) _left (tptr (Tstruct _node noattr))))
    (Sassign
      (Efield
        (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
          (Tstruct _node noattr)) _right (tptr (Tstruct _node noattr)))
      (Etempvar _t'1 (tptr (Tstruct _node noattr)))))
  (Ssequence
    (Sassign
      (Efield
        (Ederef (Etempvar _q (tptr (Tstruct _node noattr)))
          (Tstruct _node noattr)) _left (tptr (Tstruct _node noattr)))
      (Etempvar _p (tptr (Tstruct _node noattr))))
    (Sassign
      (Ederef (Etempvar _b (tptr (tptr (Tstruct _node noattr))))
        (tptr (Tstruct _node noattr)))
      (Etempvar _q (tptr (Tstruct _node noattr))))))
|}.

Definition f_pushdown_left := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_b, (tptr (tptr (Tstruct _node noattr)))) :: nil);
  fn_vars := nil;
  fn_temps := ((_p, (tptr (Tstruct _node noattr))) ::
               (_q, (tptr (Tstruct _node noattr))) ::
               (_t'1, (tptr (Tstruct _node noattr))) :: nil);
  fn_body :=
(Sloop
  (Ssequence
    Sskip
    (Ssequence
      (Sset _p
        (Ederef (Etempvar _b (tptr (tptr (Tstruct _node noattr))))
          (tptr (Tstruct _node noattr))))
      (Ssequence
        (Sset _q
          (Efield
            (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
              (Tstruct _node noattr)) _right (tptr (Tstruct _node noattr))))
        (Ssequence
          (Sifthenelse (Ebinop Oeq
                         (Etempvar _q (tptr (Tstruct _node noattr)))
                         (Ecast (Econst_int (Int.repr 0) tint) (tptr tvoid))
                         tint)
            (Ssequence
              (Ssequence
                (Sset _t'1
                  (Efield
                    (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
                      (Tstruct _node noattr)) _left
                    (tptr (Tstruct _node noattr))))
                (Sassign
                  (Ederef (Etempvar _b (tptr (tptr (Tstruct _node noattr))))
                    (tptr (Tstruct _node noattr)))
                  (Etempvar _t'1 (tptr (Tstruct _node noattr)))))
              (Ssequence
                (Scall None
                  (Evar _retire (Tfunction
                                  ((tptr (Tstruct _node noattr)) :: nil)
                                  tvoid cc_default))
                  ((Etempvar _p (tptr (Tstruct _node noattr))) :: nil))
                (Sreturn None)))
            Sskip)
          (Ssequence
            (Scall None
              (Evar _turn_left (Tfunction
                                 ((tptr (tptr (Tstruct _node noattr))) ::
                                  (tptr (Tstruct _node noattr)) ::
                                  (tptr (Tstruct _node noattr)) :: nil) tvoid
                                 cc_default))
              ((Etempvar _b (tptr (tptr (Tstruct _node noattr)))) ::
               (Etempvar _p (tptr (Tstruct _node noattr))) ::
               (Etempvar _q (tptr (Tstruct _node noattr))) :: nil))
            (Sset _b
              (Eaddrof
                (Efield
                  (Ederef (Etempvar _q (tptr (Tstruct _node noattr)))
                    (Tstruct _node noattr)) _left
                  (tptr (Tstruct _node noattr)))
                (tptr (tptr (Tstruct _node noattr))))))))))
  Sskip)
|}.

Definition f_erase := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_b, (tptr (tptr (Tstruct _node noattr)))) :: (_k, tint) ::
                nil);
  fn_vars := nil;
  fn_temps := ((_t'7, (tptr (Tstruct _node noattr))) ::
               (_t'6, (tptr (Tstruct _node noattr))) ::
               (_t'5, (tptr (Tstruct _node noattr))) :: (_t'4, tint) ::
               (_t'3, (tptr (Tstruct _node noattr))) :: (_t'2, tint) ::
               (_t'1, (tptr (Tstruct _node noattr))) :: nil);
  fn_body :=
(Sloop
  (Ssequence
    (Ssequence
      (Sset _t'7
        (Ederef (Etempvar _b (tptr (tptr (Tstruct _node noattr))))
          (tptr (Tstruct _node noattr))))
      (Sifthenelse (Ebinop One (Etempvar _t'7 (tptr (Tstruct _node noattr)))
                     (Ecast (Econst_int (Int.repr 0) tint) (tptr tvoid))
                     tint)
        Sskip
        Sbreak))
    (Ssequence
      (Sset _t'1
        (Ederef (Etempvar _b (tptr (tptr (Tstruct _node noattr))))
          (tptr (Tstruct _node noattr))))
      (Ssequence
        (Sset _t'2
          (Efield
            (Ederef (Etempvar _t'1 (tptr (Tstruct _node noattr)))
              (Tstruct _node noattr)) _key tint))
        (Sifthenelse (Ebinop Olt (Etempvar _k tint) (Etempvar _t'2 tint)
                       tint)
          (Ssequence
            (Sset _t'6
              (Ederef (Etempvar _b (tptr (tptr (Tstruct _node noattr))))
                (tptr (Tstruct _node noattr))))
            (Sset _b
              (Eaddrof
                (Efield
                  (Ederef (Etempvar _t'6 (tptr (Tstruct _node noattr)))
                    (Tstruct _node noattr)) _left
                  (tptr (Tstruct _node noattr)))
                (tptr (tptr (Tstruct _node noattr))))))
          (Ssequence
            (Sset _t'3
              (Ederef (Etempvar _b (tptr (tptr (Tstruct _node noattr))))
                (tptr (Tstruct _node noattr))))
            (Ssequence
              (Sset _t'4
                (Efield
                  (Ederef (Etempvar _t'3 (tptr (Tstruct _node noattr)))
                    (Tstruct _node noattr)) _key tint))
              (Sifthenelse (Ebinop Ogt (Etempvar _k tint)
                             (Etempvar _t'4 tint) tint)
                (Ssequence
                  (Sset _t'5
                    (Ederef
                      (Etempvar _b (tptr (tptr (Tstruct _node noattr))))
                      (tptr (Tstruct _node noattr))))
                  (Sset _b
                    (Eaddrof
                      (Efield
                        (Ederef (Etempvar _t'5 (tptr (Tstruct _node noattr)))
                          (Tstruct _node noattr)) _right
                        (tptr (Tstruct _node noattr)))
                      (tptr (tptr (Tstruct _node noattr))))))
                (Ssequence
                  (Scall None
                    (Evar _pushdown_left (Tfunction
                                           ((tptr (tptr (Tstruct _node noattr))) ::
                                            nil) tvoid cc_default))
                    ((Etempvar _b (tptr (tptr (Tstruct _node noattr)))) ::
                     nil))
                  (Sreturn None)))))))))
  Sskip)
|}.

Definition f_lookup := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_k, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_p, (tptr (Tstruct _node noattr))) :: (_t'3, tint) ::
               (_t'2, tint) :: (_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Sset _p (Evar _root (tptr (Tstruct _node noattr))))
  (Ssequence
    (Swhile
      (Ebinop One (Etempvar _p (tptr (Tstruct _node noattr)))
        (Ecast (Econst_int (Int.repr 0) tint) (tptr tvoid)) tint)
      (Ssequence
        (Sset _t'1
          (Efield
            (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
              (Tstruct _node noattr)) _key tint))
        (Sifthenelse (Ebinop Olt (Etempvar _k tint) (Etempvar _t'1 tint)
                       tint)
          (Sset _p
            (Efield
              (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
                (Tstruct _node noattr)) _left (tptr (Tstruct _node noattr))))
          (Ssequence
            (Sset _t'2
              (Efield
                (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
                  (Tstruct _node noattr)) _key tint))
            (Sifthenelse (Ebinop Ogt (Etempvar _k tint) (Etempvar _t'2 tint)
                           tint)
              (Sset _p
                (Efield
                  (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
                    (Tstruct _node noattr)) _right
                  (tptr (Tstruct _node noattr))))
              (Ssequence
                (Scall None
                  (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
                  ((Econst_int (Int.repr 1) tint) :: nil))
                (Ssequence
                  (Ssequence
                    (Sset _t'3
                      (Efield
                        (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
                          (Tstruct _node noattr)) _value tint))
                    (Scall None
                      (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
                      ((Etempvar _t'3 tint) :: nil)))
                  (Sreturn None))))))))
    (Ssequence
      (Scall None (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
        ((Econst_int (Int.repr 0) tint) :: nil))
      (Scall None (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
        ((Econst_int (Int.repr 0) tint) :: nil)))))
|}.

Definition f_project := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_p, (tptr (Tstruct _node noattr))) :: nil);
  fn_vars := nil;
  fn_temps := ((_t'4, (tptr (Tstruct _node noattr))) :: (_t'3, tint) ::
               (_t'2, tint) :: (_t'1, (tptr (Tstruct _node noattr))) :: nil);
  fn_body :=
(Sifthenelse (Ebinop One (Etempvar _p (tptr (Tstruct _node noattr)))
               (Ecast (Econst_int (Int.repr 0) tint) (tptr tvoid)) tint)
  (Ssequence
    (Ssequence
      (Sset _t'4
        (Efield
          (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
            (Tstruct _node noattr)) _left (tptr (Tstruct _node noattr))))
      (Scall None
        (Evar _project (Tfunction ((tptr (Tstruct _node noattr)) :: nil)
                         tvoid cc_default))
        ((Etempvar _t'4 (tptr (Tstruct _node noattr))) :: nil)))
    (Ssequence
      (Ssequence
        (Sset _t'3
          (Efield
            (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
              (Tstruct _node noattr)) _key tint))
        (Scall None (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
          ((Etempvar _t'3 tint) :: nil)))
      (Ssequence
        (Ssequence
          (Sset _t'2
            (Efield
              (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
                (Tstruct _node noattr)) _value tint))
          (Scall None (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
            ((Etempvar _t'2 tint) :: nil)))
        (Ssequence
          (Sset _t'1
            (Efield
              (Ederef (Etempvar _p (tptr (Tstruct _node noattr)))
                (Tstruct _node noattr)) _right (tptr (Tstruct _node noattr))))
          (Scall None
            (Evar _project (Tfunction ((tptr (Tstruct _node noattr)) :: nil)
                             tvoid cc_default))
            ((Etempvar _t'1 (tptr (Tstruct _node noattr))) :: nil))))))
  Sskip)
|}.

Definition f_main := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := nil;
  fn_vars := nil;
  fn_temps := ((_n, tint) :: (_q, tint) :: (_pos, tint) :: (_i, tint) ::
               (_op, tint) :: (_k, tint) :: (_t'1, tint) :: (_t'4, tint) ::
               (_t'3, tint) :: (_t'2, (tptr (Tstruct _node noattr))) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Sset _n
      (Ederef
        (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
          (Econst_int (Int.repr 0) tint) (tptr tint)) tint))
    (Ssequence
      (Sset _q
        (Ederef
          (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
            (Econst_int (Int.repr 1) tint) (tptr tint)) tint))
      (Ssequence
        (Sset _pos (Econst_int (Int.repr 2) tint))
        (Ssequence
          (Scall None (Evar _begin_output (Tfunction nil tvoid cc_default))
            nil)
          (Ssequence
            (Sassign (Evar _root (tptr (Tstruct _node noattr)))
              (Ecast (Econst_int (Int.repr 0) tint) (tptr tvoid)))
            (Ssequence
              (Sassign (Evar _used tint) (Econst_int (Int.repr 0) tint))
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
                          (Sset _t'3
                            (Ederef
                              (Ebinop Oadd
                                (Evar _eb_input (tarray tint 8192))
                                (Etempvar _pos tint) (tptr tint)) tint))
                          (Ssequence
                            (Sset _t'4
                              (Ederef
                                (Ebinop Oadd
                                  (Evar _eb_input (tarray tint 8192))
                                  (Ebinop Oadd (Etempvar _pos tint)
                                    (Econst_int (Int.repr 1) tint) tint)
                                  (tptr tint)) tint))
                            (Scall None
                              (Evar _initial_insert (Tfunction
                                                      (tint :: tint :: nil)
                                                      tvoid cc_default))
                              ((Etempvar _t'3 tint) ::
                               (Etempvar _t'4 tint) :: nil))))
                        (Sset _pos
                          (Ebinop Oadd (Etempvar _pos tint)
                            (Econst_int (Int.repr 2) tint) tint))))
                    (Sset _i
                      (Ebinop Oadd (Etempvar _i tint)
                        (Econst_int (Int.repr 1) tint) tint))))
                (Ssequence
                  (Ssequence
                    (Sset _i (Econst_int (Int.repr 0) tint))
                    (Sloop
                      (Ssequence
                        (Sifthenelse (Ebinop Olt (Etempvar _i tint)
                                       (Etempvar _q tint) tint)
                          Sskip
                          Sbreak)
                        (Ssequence
                          (Sset _op
                            (Ederef
                              (Ebinop Oadd
                                (Evar _eb_input (tarray tint 8192))
                                (Etempvar _pos tint) (tptr tint)) tint))
                          (Ssequence
                            (Sset _k
                              (Ederef
                                (Ebinop Oadd
                                  (Evar _eb_input (tarray tint 8192))
                                  (Ebinop Oadd (Etempvar _pos tint)
                                    (Econst_int (Int.repr 1) tint) tint)
                                  (tptr tint)) tint))
                            (Ssequence
                              (Sset _pos
                                (Ebinop Oadd (Etempvar _pos tint)
                                  (Econst_int (Int.repr 2) tint) tint))
                              (Ssequence
                                (Scall None
                                  (Evar _emit (Tfunction (tint :: nil) tvoid
                                                cc_default))
                                  ((Etempvar _op tint) :: nil))
                                (Sifthenelse (Ebinop Oeq (Etempvar _op tint)
                                               (Econst_int (Int.repr 0) tint)
                                               tint)
                                  (Ssequence
                                    (Scall None
                                      (Evar _erase (Tfunction
                                                     ((tptr (tptr (Tstruct _node noattr))) ::
                                                      tint :: nil) tvoid
                                                     cc_default))
                                      ((Eaddrof
                                         (Evar _root (tptr (Tstruct _node noattr)))
                                         (tptr (tptr (Tstruct _node noattr)))) ::
                                       (Etempvar _k tint) :: nil))
                                    (Scall None
                                      (Evar _emit (Tfunction (tint :: nil)
                                                    tvoid cc_default))
                                      ((Econst_int (Int.repr 0) tint) :: nil)))
                                  (Scall None
                                    (Evar _lookup (Tfunction (tint :: nil)
                                                    tvoid cc_default))
                                    ((Etempvar _k tint) :: nil))))))))
                      (Sset _i
                        (Ebinop Oadd (Etempvar _i tint)
                          (Econst_int (Int.repr 1) tint) tint))))
                  (Ssequence
                    (Scall None
                      (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
                      ((Eunop Oneg (Econst_int (Int.repr 2) tint) tint) ::
                       nil))
                    (Ssequence
                      (Ssequence
                        (Sset _t'2
                          (Evar _root (tptr (Tstruct _node noattr))))
                        (Scall None
                          (Evar _project (Tfunction
                                           ((tptr (Tstruct _node noattr)) ::
                                            nil) tvoid cc_default))
                          ((Etempvar _t'2 (tptr (Tstruct _node noattr))) ::
                           nil)))
                      (Ssequence
                        (Scall (Some _t'1)
                          (Evar _end_output (Tfunction nil tint cc_default))
                          nil)
                        (Sreturn (Some (Etempvar _t'1 tint))))))))))))))
  (Sreturn (Some (Econst_int (Int.repr 0) tint))))
|}.

Definition composites : list composite_definition :=
(Composite _node Struct
   (Member_plain _key tint :: Member_plain _value tint ::
    Member_plain _live tint ::
    Member_plain _left (tptr (Tstruct _node noattr)) ::
    Member_plain _right (tptr (Tstruct _node noattr)) :: nil)
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
 (_end_output, Gfun(Internal f_end_output)) :: (_arena, Gvar v_arena) ::
 (_used, Gvar v_used) :: (_root, Gvar v_root) ::
 (_new_node, Gfun(Internal f_new_node)) ::
 (_retire, Gfun(Internal f_retire)) ::
 (_initial_insert, Gfun(Internal f_initial_insert)) ::
 (_turn_left, Gfun(Internal f_turn_left)) ::
 (_pushdown_left, Gfun(Internal f_pushdown_left)) ::
 (_erase, Gfun(Internal f_erase)) :: (_lookup, Gfun(Internal f_lookup)) ::
 (_project, Gfun(Internal f_project)) :: (_main, Gfun(Internal f_main)) ::
 nil).

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


