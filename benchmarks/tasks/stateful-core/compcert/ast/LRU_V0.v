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
  Definition source_file := "LRU_V0.c".
  Definition normalized := true.
End Info.

Definition _CacheNode : ident := $"CacheNode".
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
Definition _begin_output : ident := $"begin_output".
Definition _cache_put : ident := $"cache_put".
Definition _cache_query : ident := $"cache_query".
Definition _cap : ident := $"cap".
Definition _cap_ : ident := $"cap_".
Definition _eb_input : ident := $"eb_input".
Definition _eb_out : ident := $"eb_out".
Definition _eb_output : ident := $"eb_output".
Definition _emit : ident := $"emit".
Definition _end_output : ident := $"end_output".
Definition _erase_at : ident := $"erase_at".
Definition _evict_tail : ident := $"evict_tail".
Definition _execute_cache : ident := $"execute_cache".
Definition _head_ : ident := $"head_".
Definition _i : ident := $"i".
Definition _id : ident := $"id".
Definition _insert_front : ident := $"insert_front".
Definition _k : ident := $"k".
Definition _key : ident := $"key".
Definition _key_at : ident := $"key_at".
Definition _keys : ident := $"keys".
Definition _live : ident := $"live".
Definition _lookup_key : ident := $"lookup_key".
Definition _main : ident := $"main".
Definition _n : ident := $"n".
Definition _next : ident := $"next".
Definition _nodes : ident := $"nodes".
Definition _observe_cache : ident := $"observe_cache".
Definition _op : ident := $"op".
Definition _out : ident := $"out".
Definition _prev : ident := $"prev".
Definition _q : ident := $"q".
Definition _resize_cache : ident := $"resize_cache".
Definition _set_value : ident := $"set_value".
Definition _size_ : ident := $"size_".
Definition _status : ident := $"status".
Definition _tail_ : ident := $"tail_".
Definition _touch : ident := $"touch".
Definition _update : ident := $"update".
Definition _v : ident := $"v".
Definition _vals : ident := $"vals".
Definition _value : ident := $"value".
Definition _value_at : ident := $"value_at".
Definition _x : ident := $"x".
Definition _t'1 : ident := 128%positive.
Definition _t'2 : ident := 129%positive.
Definition _t'3 : ident := 130%positive.
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

Definition v_nodes := {|
  gvar_info := (tarray (Tstruct _CacheNode noattr) 8);
  gvar_init := (Init_space 160 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_keys := {|
  gvar_info := (tarray tint 8);
  gvar_init := (Init_space 32 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_vals := {|
  gvar_info := (tarray tint 8);
  gvar_init := (Init_space 32 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_size_ := {|
  gvar_info := tint;
  gvar_init := (Init_space 4 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_cap_ := {|
  gvar_info := tint;
  gvar_init := (Init_space 4 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_head_ := {|
  gvar_info := tint;
  gvar_init := (Init_space 4 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_tail_ := {|
  gvar_info := tint;
  gvar_init := (Init_space 4 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition f_lookup_key := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := ((_key, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_i, tint) :: (_t'2, tint) :: (_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Sset _i (Econst_int (Int.repr 0) tint))
    (Sloop
      (Ssequence
        (Ssequence
          (Sset _t'2 (Evar _size_ tint))
          (Sifthenelse (Ebinop Olt (Etempvar _i tint) (Etempvar _t'2 tint)
                         tint)
            Sskip
            Sbreak))
        (Ssequence
          (Sset _t'1
            (Ederef
              (Ebinop Oadd (Evar _keys (tarray tint 8)) (Etempvar _i tint)
                (tptr tint)) tint))
          (Sifthenelse (Ebinop Oeq (Etempvar _t'1 tint) (Etempvar _key tint)
                         tint)
            (Sreturn (Some (Etempvar _i tint)))
            Sskip)))
      (Sset _i
        (Ebinop Oadd (Etempvar _i tint) (Econst_int (Int.repr 1) tint) tint))))
  (Sreturn (Some (Eunop Oneg (Econst_int (Int.repr 1) tint) tint))))
|}.

Definition f_key_at := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := ((_i, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Sset _t'1
    (Ederef
      (Ebinop Oadd (Evar _keys (tarray tint 8)) (Etempvar _i tint)
        (tptr tint)) tint))
  (Sreturn (Some (Etempvar _t'1 tint))))
|}.

Definition f_value_at := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := ((_i, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Sset _t'1
    (Ederef
      (Ebinop Oadd (Evar _vals (tarray tint 8)) (Etempvar _i tint)
        (tptr tint)) tint))
  (Sreturn (Some (Etempvar _t'1 tint))))
|}.

Definition f_erase_at := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_id, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_i, tint) :: (_t'4, tint) :: (_t'3, tint) :: (_t'2, tint) ::
               (_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Sset _i
      (Ebinop Oadd (Etempvar _id tint) (Econst_int (Int.repr 1) tint) tint))
    (Sloop
      (Ssequence
        (Ssequence
          (Sset _t'4 (Evar _size_ tint))
          (Sifthenelse (Ebinop Olt (Etempvar _i tint) (Etempvar _t'4 tint)
                         tint)
            Sskip
            Sbreak))
        (Ssequence
          (Ssequence
            (Sset _t'3
              (Ederef
                (Ebinop Oadd (Evar _keys (tarray tint 8)) (Etempvar _i tint)
                  (tptr tint)) tint))
            (Sassign
              (Ederef
                (Ebinop Oadd (Evar _keys (tarray tint 8))
                  (Ebinop Osub (Etempvar _i tint)
                    (Econst_int (Int.repr 1) tint) tint) (tptr tint)) tint)
              (Etempvar _t'3 tint)))
          (Ssequence
            (Sset _t'2
              (Ederef
                (Ebinop Oadd (Evar _vals (tarray tint 8)) (Etempvar _i tint)
                  (tptr tint)) tint))
            (Sassign
              (Ederef
                (Ebinop Oadd (Evar _vals (tarray tint 8))
                  (Ebinop Osub (Etempvar _i tint)
                    (Econst_int (Int.repr 1) tint) tint) (tptr tint)) tint)
              (Etempvar _t'2 tint)))))
      (Sset _i
        (Ebinop Oadd (Etempvar _i tint) (Econst_int (Int.repr 1) tint) tint))))
  (Ssequence
    (Sset _t'1 (Evar _size_ tint))
    (Sassign (Evar _size_ tint)
      (Ebinop Osub (Etempvar _t'1 tint) (Econst_int (Int.repr 1) tint) tint))))
|}.

Definition f_touch := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_id, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_i, tint) :: (_k, tint) :: (_v, tint) :: (_t'2, tint) ::
               (_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Sset _k
    (Ederef
      (Ebinop Oadd (Evar _keys (tarray tint 8)) (Etempvar _id tint)
        (tptr tint)) tint))
  (Ssequence
    (Sset _v
      (Ederef
        (Ebinop Oadd (Evar _vals (tarray tint 8)) (Etempvar _id tint)
          (tptr tint)) tint))
    (Ssequence
      (Ssequence
        (Sset _i (Etempvar _id tint))
        (Sloop
          (Ssequence
            (Sifthenelse (Ebinop Ogt (Etempvar _i tint)
                           (Econst_int (Int.repr 0) tint) tint)
              Sskip
              Sbreak)
            (Ssequence
              (Ssequence
                (Sset _t'2
                  (Ederef
                    (Ebinop Oadd (Evar _keys (tarray tint 8))
                      (Ebinop Osub (Etempvar _i tint)
                        (Econst_int (Int.repr 1) tint) tint) (tptr tint))
                    tint))
                (Sassign
                  (Ederef
                    (Ebinop Oadd (Evar _keys (tarray tint 8))
                      (Etempvar _i tint) (tptr tint)) tint)
                  (Etempvar _t'2 tint)))
              (Ssequence
                (Sset _t'1
                  (Ederef
                    (Ebinop Oadd (Evar _vals (tarray tint 8))
                      (Ebinop Osub (Etempvar _i tint)
                        (Econst_int (Int.repr 1) tint) tint) (tptr tint))
                    tint))
                (Sassign
                  (Ederef
                    (Ebinop Oadd (Evar _vals (tarray tint 8))
                      (Etempvar _i tint) (tptr tint)) tint)
                  (Etempvar _t'1 tint)))))
          (Sset _i
            (Ebinop Osub (Etempvar _i tint) (Econst_int (Int.repr 1) tint)
              tint))))
      (Ssequence
        (Sassign
          (Ederef
            (Ebinop Oadd (Evar _keys (tarray tint 8))
              (Econst_int (Int.repr 0) tint) (tptr tint)) tint)
          (Etempvar _k tint))
        (Sassign
          (Ederef
            (Ebinop Oadd (Evar _vals (tarray tint 8))
              (Econst_int (Int.repr 0) tint) (tptr tint)) tint)
          (Etempvar _v tint))))))
|}.

Definition f_set_value := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_id, tint) :: (_v, tint) :: nil);
  fn_vars := nil;
  fn_temps := nil;
  fn_body :=
(Sassign
  (Ederef
    (Ebinop Oadd (Evar _vals (tarray tint 8)) (Etempvar _id tint)
      (tptr tint)) tint) (Etempvar _v tint))
|}.

Definition f_insert_front := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_key, tint) :: (_value, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_i, tint) :: (_id, tint) :: (_t'3, tint) :: (_t'2, tint) ::
               (_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Sset _i (Evar _size_ tint))
    (Sloop
      (Ssequence
        (Sifthenelse (Ebinop Ogt (Etempvar _i tint)
                       (Econst_int (Int.repr 0) tint) tint)
          Sskip
          Sbreak)
        (Ssequence
          (Ssequence
            (Sset _t'3
              (Ederef
                (Ebinop Oadd (Evar _keys (tarray tint 8))
                  (Ebinop Osub (Etempvar _i tint)
                    (Econst_int (Int.repr 1) tint) tint) (tptr tint)) tint))
            (Sassign
              (Ederef
                (Ebinop Oadd (Evar _keys (tarray tint 8)) (Etempvar _i tint)
                  (tptr tint)) tint) (Etempvar _t'3 tint)))
          (Ssequence
            (Sset _t'2
              (Ederef
                (Ebinop Oadd (Evar _vals (tarray tint 8))
                  (Ebinop Osub (Etempvar _i tint)
                    (Econst_int (Int.repr 1) tint) tint) (tptr tint)) tint))
            (Sassign
              (Ederef
                (Ebinop Oadd (Evar _vals (tarray tint 8)) (Etempvar _i tint)
                  (tptr tint)) tint) (Etempvar _t'2 tint)))))
      (Sset _i
        (Ebinop Osub (Etempvar _i tint) (Econst_int (Int.repr 1) tint) tint))))
  (Ssequence
    (Sassign
      (Ederef
        (Ebinop Oadd (Evar _keys (tarray tint 8))
          (Econst_int (Int.repr 0) tint) (tptr tint)) tint)
      (Etempvar _key tint))
    (Ssequence
      (Sassign
        (Ederef
          (Ebinop Oadd (Evar _vals (tarray tint 8))
            (Econst_int (Int.repr 0) tint) (tptr tint)) tint)
        (Etempvar _value tint))
      (Ssequence
        (Sset _t'1 (Evar _size_ tint))
        (Sassign (Evar _size_ tint)
          (Ebinop Oadd (Etempvar _t'1 tint) (Econst_int (Int.repr 1) tint)
            tint))))))
|}.

Definition f_evict_tail := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_out, (tptr tint)) :: (_n, (tptr tint)) :: nil);
  fn_vars := nil;
  fn_temps := ((_id, tint) :: (_t'2, tint) :: (_t'1, tint) :: (_t'6, tint) ::
               (_t'5, tint) :: (_t'4, tint) :: (_t'3, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Sset _t'6 (Evar _size_ tint))
    (Sset _id
      (Ebinop Osub (Etempvar _t'6 tint) (Econst_int (Int.repr 1) tint) tint)))
  (Ssequence
    (Ssequence
      (Scall (Some _t'1)
        (Evar _key_at (Tfunction (tint :: nil) tint cc_default))
        ((Etempvar _id tint) :: nil))
      (Ssequence
        (Sset _t'5 (Ederef (Etempvar _n (tptr tint)) tint))
        (Sassign
          (Ederef
            (Ebinop Oadd (Etempvar _out (tptr tint))
              (Ebinop Omul (Econst_int (Int.repr 2) tint)
                (Etempvar _t'5 tint) tint) (tptr tint)) tint)
          (Etempvar _t'1 tint))))
    (Ssequence
      (Ssequence
        (Scall (Some _t'2)
          (Evar _value_at (Tfunction (tint :: nil) tint cc_default))
          ((Etempvar _id tint) :: nil))
        (Ssequence
          (Sset _t'4 (Ederef (Etempvar _n (tptr tint)) tint))
          (Sassign
            (Ederef
              (Ebinop Oadd (Etempvar _out (tptr tint))
                (Ebinop Oadd
                  (Ebinop Omul (Econst_int (Int.repr 2) tint)
                    (Etempvar _t'4 tint) tint) (Econst_int (Int.repr 1) tint)
                  tint) (tptr tint)) tint) (Etempvar _t'2 tint))))
      (Ssequence
        (Ssequence
          (Sset _t'3 (Ederef (Etempvar _n (tptr tint)) tint))
          (Sassign (Ederef (Etempvar _n (tptr tint)) tint)
            (Ebinop Oadd (Etempvar _t'3 tint) (Econst_int (Int.repr 1) tint)
              tint)))
        (Scall None
          (Evar _erase_at (Tfunction (tint :: nil) tvoid cc_default))
          ((Etempvar _id tint) :: nil))))))
|}.

Definition f_cache_put := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := ((_key, tint) :: (_value, tint) :: (_out, (tptr tint)) ::
                (_n, (tptr tint)) :: nil);
  fn_vars := nil;
  fn_temps := ((_id, tint) :: (_t'1, tint) :: (_t'4, tint) :: (_t'3, tint) ::
               (_t'2, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Scall (Some _t'1)
      (Evar _lookup_key (Tfunction (tint :: nil) tint cc_default))
      ((Etempvar _key tint) :: nil))
    (Sset _id (Etempvar _t'1 tint)))
  (Ssequence
    (Sifthenelse (Ebinop Oge (Etempvar _id tint)
                   (Econst_int (Int.repr 0) tint) tint)
      (Ssequence
        (Scall None
          (Evar _set_value (Tfunction (tint :: tint :: nil) tvoid cc_default))
          ((Etempvar _id tint) :: (Etempvar _value tint) :: nil))
        (Ssequence
          (Scall None
            (Evar _touch (Tfunction (tint :: nil) tvoid cc_default))
            ((Etempvar _id tint) :: nil))
          (Sreturn (Some (Econst_int (Int.repr 1) tint)))))
      Sskip)
    (Ssequence
      (Ssequence
        (Sset _t'4 (Evar _cap_ tint))
        (Sifthenelse (Ebinop Oeq (Etempvar _t'4 tint)
                       (Econst_int (Int.repr 0) tint) tint)
          (Sreturn (Some (Econst_int (Int.repr 0) tint)))
          Sskip))
      (Ssequence
        (Ssequence
          (Sset _t'2 (Evar _size_ tint))
          (Ssequence
            (Sset _t'3 (Evar _cap_ tint))
            (Sifthenelse (Ebinop Oeq (Etempvar _t'2 tint)
                           (Etempvar _t'3 tint) tint)
              (Scall None
                (Evar _evict_tail (Tfunction
                                    ((tptr tint) :: (tptr tint) :: nil) tvoid
                                    cc_default))
                ((Etempvar _out (tptr tint)) :: (Etempvar _n (tptr tint)) ::
                 nil))
              Sskip)))
        (Ssequence
          (Scall None
            (Evar _insert_front (Tfunction (tint :: tint :: nil) tvoid
                                  cc_default))
            ((Etempvar _key tint) :: (Etempvar _value tint) :: nil))
          (Sreturn (Some (Econst_int (Int.repr 1) tint))))))))
|}.

Definition f_cache_query := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := ((_key, tint) :: (_update, tint) :: (_value, (tptr tint)) ::
                nil);
  fn_vars := nil;
  fn_temps := ((_id, tint) :: (_t'2, tint) :: (_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Scall (Some _t'1)
      (Evar _lookup_key (Tfunction (tint :: nil) tint cc_default))
      ((Etempvar _key tint) :: nil))
    (Sset _id (Etempvar _t'1 tint)))
  (Ssequence
    (Sifthenelse (Ebinop Olt (Etempvar _id tint)
                   (Econst_int (Int.repr 0) tint) tint)
      (Ssequence
        (Sassign (Ederef (Etempvar _value (tptr tint)) tint)
          (Econst_int (Int.repr 0) tint))
        (Sreturn (Some (Econst_int (Int.repr 0) tint))))
      Sskip)
    (Ssequence
      (Ssequence
        (Scall (Some _t'2)
          (Evar _value_at (Tfunction (tint :: nil) tint cc_default))
          ((Etempvar _id tint) :: nil))
        (Sassign (Ederef (Etempvar _value (tptr tint)) tint)
          (Etempvar _t'2 tint)))
      (Ssequence
        (Sifthenelse (Etempvar _update tint)
          (Scall None
            (Evar _touch (Tfunction (tint :: nil) tvoid cc_default))
            ((Etempvar _id tint) :: nil))
          Sskip)
        (Sreturn (Some (Econst_int (Int.repr 1) tint)))))))
|}.

Definition f_resize_cache := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_cap, tint) :: (_out, (tptr tint)) :: (_n, (tptr tint)) ::
                nil);
  fn_vars := nil;
  fn_temps := ((_t'2, tint) :: (_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Sassign (Evar _cap_ tint) (Etempvar _cap tint))
  (Sloop
    (Ssequence
      (Ssequence
        (Sset _t'1 (Evar _size_ tint))
        (Ssequence
          (Sset _t'2 (Evar _cap_ tint))
          (Sifthenelse (Ebinop Ogt (Etempvar _t'1 tint) (Etempvar _t'2 tint)
                         tint)
            Sskip
            Sbreak)))
      (Scall None
        (Evar _evict_tail (Tfunction ((tptr tint) :: (tptr tint) :: nil)
                            tvoid cc_default))
        ((Etempvar _out (tptr tint)) :: (Etempvar _n (tptr tint)) :: nil)))
    Sskip))
|}.

Definition f_execute_cache := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_op, tint) :: (_key, tint) :: (_value, tint) :: nil);
  fn_vars := ((_out, (tarray tint 16)) :: (_n, tint) :: (_v, tint) :: nil);
  fn_temps := ((_status, tint) :: (_id, tint) :: (_i, tint) ::
               (_t'5, tint) :: (_t'4, tint) :: (_t'3, tint) ::
               (_t'2, tint) :: (_t'1, tint) :: (_t'9, tint) ::
               (_t'8, tint) :: (_t'7, tint) :: (_t'6, tint) :: nil);
  fn_body :=
(Ssequence
  (Sassign (Evar _n tint) (Econst_int (Int.repr 0) tint))
  (Ssequence
    (Sset _status (Econst_int (Int.repr 0) tint))
    (Ssequence
      (Sassign (Evar _v tint) (Econst_int (Int.repr 0) tint))
      (Ssequence
        (Sifthenelse (Ebinop Oeq (Etempvar _op tint)
                       (Econst_int (Int.repr 0) tint) tint)
          (Ssequence
            (Scall (Some _t'1)
              (Evar _cache_put (Tfunction
                                 (tint :: tint :: (tptr tint) ::
                                  (tptr tint) :: nil) tint cc_default))
              ((Etempvar _key tint) :: (Etempvar _value tint) ::
               (Evar _out (tarray tint 16)) ::
               (Eaddrof (Evar _n tint) (tptr tint)) :: nil))
            (Sset _status (Etempvar _t'1 tint)))
          (Ssequence
            (Sifthenelse (Ebinop Oeq (Etempvar _op tint)
                           (Econst_int (Int.repr 1) tint) tint)
              (Sset _t'5 (Econst_int (Int.repr 1) tint))
              (Sset _t'5
                (Ecast
                  (Ebinop Oeq (Etempvar _op tint)
                    (Econst_int (Int.repr 2) tint) tint) tbool)))
            (Sifthenelse (Etempvar _t'5 tint)
              (Ssequence
                (Scall (Some _t'2)
                  (Evar _cache_query (Tfunction
                                       (tint :: tint :: (tptr tint) :: nil)
                                       tint cc_default))
                  ((Etempvar _key tint) ::
                   (Ebinop Oeq (Etempvar _op tint)
                     (Econst_int (Int.repr 1) tint) tint) ::
                   (Eaddrof (Evar _v tint) (tptr tint)) :: nil))
                (Sset _status (Etempvar _t'2 tint)))
              (Sifthenelse (Ebinop Oeq (Etempvar _op tint)
                             (Econst_int (Int.repr 3) tint) tint)
                (Ssequence
                  (Ssequence
                    (Scall (Some _t'3)
                      (Evar _lookup_key (Tfunction (tint :: nil) tint
                                          cc_default))
                      ((Etempvar _key tint) :: nil))
                    (Sset _id (Etempvar _t'3 tint)))
                  (Sifthenelse (Ebinop Oge (Etempvar _id tint)
                                 (Econst_int (Int.repr 0) tint) tint)
                    (Ssequence
                      (Sset _status (Econst_int (Int.repr 1) tint))
                      (Ssequence
                        (Ssequence
                          (Scall (Some _t'4)
                            (Evar _value_at (Tfunction (tint :: nil) tint
                                              cc_default))
                            ((Etempvar _id tint) :: nil))
                          (Sassign (Evar _v tint) (Etempvar _t'4 tint)))
                        (Scall None
                          (Evar _erase_at (Tfunction (tint :: nil) tvoid
                                            cc_default))
                          ((Etempvar _id tint) :: nil))))
                    Sskip))
                (Ssequence
                  (Scall None
                    (Evar _resize_cache (Tfunction
                                          (tint :: (tptr tint) ::
                                           (tptr tint) :: nil) tvoid
                                          cc_default))
                    ((Etempvar _key tint) :: (Evar _out (tarray tint 16)) ::
                     (Eaddrof (Evar _n tint) (tptr tint)) :: nil))
                  (Ssequence
                    (Sset _status (Econst_int (Int.repr 1) tint))
                    (Sassign (Evar _v tint) (Etempvar _key tint))))))))
        (Ssequence
          (Scall None (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
            ((Etempvar _op tint) :: nil))
          (Ssequence
            (Scall None
              (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
              ((Etempvar _status tint) :: nil))
            (Ssequence
              (Ssequence
                (Sset _t'9 (Evar _v tint))
                (Scall None
                  (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
                  ((Etempvar _t'9 tint) :: nil)))
              (Ssequence
                (Ssequence
                  (Sset _t'8 (Evar _n tint))
                  (Scall None
                    (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
                    ((Etempvar _t'8 tint) :: nil)))
                (Ssequence
                  (Sset _i (Econst_int (Int.repr 0) tint))
                  (Sloop
                    (Ssequence
                      (Ssequence
                        (Sset _t'7 (Evar _n tint))
                        (Sifthenelse (Ebinop Olt (Etempvar _i tint)
                                       (Ebinop Omul
                                         (Econst_int (Int.repr 2) tint)
                                         (Etempvar _t'7 tint) tint) tint)
                          Sskip
                          Sbreak))
                      (Ssequence
                        (Sset _t'6
                          (Ederef
                            (Ebinop Oadd (Evar _out (tarray tint 16))
                              (Etempvar _i tint) (tptr tint)) tint))
                        (Scall None
                          (Evar _emit (Tfunction (tint :: nil) tvoid
                                        cc_default))
                          ((Etempvar _t'6 tint) :: nil))))
                    (Sset _i
                      (Ebinop Oadd (Etempvar _i tint)
                        (Econst_int (Int.repr 1) tint) tint))))))))))))
|}.

Definition f_observe_cache := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := nil;
  fn_vars := nil;
  fn_temps := ((_i, tint) :: (_id, tint) :: (_t'5, tint) :: (_t'4, tint) ::
               (_t'3, tint) :: (_t'2, tint) :: (_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Sset _t'5 (Evar _cap_ tint))
    (Scall None (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
      ((Etempvar _t'5 tint) :: nil)))
  (Ssequence
    (Ssequence
      (Sset _t'4 (Evar _size_ tint))
      (Scall None (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
        ((Etempvar _t'4 tint) :: nil)))
    (Ssequence
      (Sset _i (Econst_int (Int.repr 0) tint))
      (Sloop
        (Ssequence
          (Ssequence
            (Sset _t'3 (Evar _size_ tint))
            (Sifthenelse (Ebinop Olt (Etempvar _i tint) (Etempvar _t'3 tint)
                           tint)
              Sskip
              Sbreak))
          (Ssequence
            (Ssequence
              (Sset _t'2
                (Ederef
                  (Ebinop Oadd (Evar _keys (tarray tint 8))
                    (Etempvar _i tint) (tptr tint)) tint))
              (Scall None
                (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
                ((Etempvar _t'2 tint) :: nil)))
            (Ssequence
              (Sset _t'1
                (Ederef
                  (Ebinop Oadd (Evar _vals (tarray tint 8))
                    (Etempvar _i tint) (tptr tint)) tint))
              (Scall None
                (Evar _emit (Tfunction (tint :: nil) tvoid cc_default))
                ((Etempvar _t'1 tint) :: nil)))))
        (Sset _i
          (Ebinop Oadd (Etempvar _i tint) (Econst_int (Int.repr 1) tint)
            tint))))))
|}.

Definition f_main := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := nil;
  fn_vars := nil;
  fn_temps := ((_q, tint) :: (_i, tint) :: (_t'1, tint) :: (_t'5, tint) ::
               (_t'4, tint) :: (_t'3, tint) :: (_t'2, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Sset _q
      (Ederef
        (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
          (Econst_int (Int.repr 1) tint) (tptr tint)) tint))
    (Ssequence
      (Scall None (Evar _begin_output (Tfunction nil tvoid cc_default)) nil)
      (Ssequence
        (Ssequence
          (Sset _t'5
            (Ederef
              (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
                (Econst_int (Int.repr 0) tint) (tptr tint)) tint))
          (Sassign (Evar _cap_ tint) (Etempvar _t'5 tint)))
        (Ssequence
          (Sassign (Evar _size_ tint) (Econst_int (Int.repr 0) tint))
          (Ssequence
            (Sassign (Evar _head_ tint)
              (Eunop Oneg (Econst_int (Int.repr 1) tint) tint))
            (Ssequence
              (Sassign (Evar _tail_ tint)
                (Eunop Oneg (Econst_int (Int.repr 1) tint) tint))
              (Ssequence
                (Ssequence
                  (Sset _i (Econst_int (Int.repr 0) tint))
                  (Sloop
                    (Ssequence
                      (Sifthenelse (Ebinop Olt (Etempvar _i tint)
                                     (Econst_int (Int.repr 8) tint) tint)
                        Sskip
                        Sbreak)
                      (Ssequence
                        (Sassign
                          (Efield
                            (Ederef
                              (Ebinop Oadd
                                (Evar _nodes (tarray (Tstruct _CacheNode noattr) 8))
                                (Etempvar _i tint)
                                (tptr (Tstruct _CacheNode noattr)))
                              (Tstruct _CacheNode noattr)) _live tint)
                          (Econst_int (Int.repr 0) tint))
                        (Ssequence
                          (Sassign
                            (Efield
                              (Ederef
                                (Ebinop Oadd
                                  (Evar _nodes (tarray (Tstruct _CacheNode noattr) 8))
                                  (Etempvar _i tint)
                                  (tptr (Tstruct _CacheNode noattr)))
                                (Tstruct _CacheNode noattr)) _prev tint)
                            (Eunop Oneg (Econst_int (Int.repr 1) tint) tint))
                          (Sassign
                            (Efield
                              (Ederef
                                (Ebinop Oadd
                                  (Evar _nodes (tarray (Tstruct _CacheNode noattr) 8))
                                  (Etempvar _i tint)
                                  (tptr (Tstruct _CacheNode noattr)))
                                (Tstruct _CacheNode noattr)) _next tint)
                            (Eunop Oneg (Econst_int (Int.repr 1) tint) tint)))))
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
                          (Sset _t'2
                            (Ederef
                              (Ebinop Oadd
                                (Evar _eb_input (tarray tint 8192))
                                (Ebinop Oadd (Econst_int (Int.repr 2) tint)
                                  (Ebinop Omul (Econst_int (Int.repr 3) tint)
                                    (Etempvar _i tint) tint) tint)
                                (tptr tint)) tint))
                          (Ssequence
                            (Sset _t'3
                              (Ederef
                                (Ebinop Oadd
                                  (Evar _eb_input (tarray tint 8192))
                                  (Ebinop Oadd (Econst_int (Int.repr 3) tint)
                                    (Ebinop Omul
                                      (Econst_int (Int.repr 3) tint)
                                      (Etempvar _i tint) tint) tint)
                                  (tptr tint)) tint))
                            (Ssequence
                              (Sset _t'4
                                (Ederef
                                  (Ebinop Oadd
                                    (Evar _eb_input (tarray tint 8192))
                                    (Ebinop Oadd
                                      (Econst_int (Int.repr 4) tint)
                                      (Ebinop Omul
                                        (Econst_int (Int.repr 3) tint)
                                        (Etempvar _i tint) tint) tint)
                                    (tptr tint)) tint))
                              (Scall None
                                (Evar _execute_cache (Tfunction
                                                       (tint :: tint ::
                                                        tint :: nil) tvoid
                                                       cc_default))
                                ((Etempvar _t'2 tint) ::
                                 (Etempvar _t'3 tint) ::
                                 (Etempvar _t'4 tint) :: nil))))))
                      (Sset _i
                        (Ebinop Oadd (Etempvar _i tint)
                          (Econst_int (Int.repr 1) tint) tint))))
                  (Ssequence
                    (Scall None
                      (Evar _observe_cache (Tfunction nil tvoid cc_default))
                      nil)
                    (Ssequence
                      (Scall (Some _t'1)
                        (Evar _end_output (Tfunction nil tint cc_default))
                        nil)
                      (Sreturn (Some (Etempvar _t'1 tint)))))))))))))
  (Sreturn (Some (Econst_int (Int.repr 0) tint))))
|}.

Definition composites : list composite_definition :=
(Composite _CacheNode Struct
   (Member_plain _key tint :: Member_plain _value tint ::
    Member_plain _prev tint :: Member_plain _next tint ::
    Member_plain _live tint :: nil)
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
 (_end_output, Gfun(Internal f_end_output)) :: (_nodes, Gvar v_nodes) ::
 (_keys, Gvar v_keys) :: (_vals, Gvar v_vals) :: (_size_, Gvar v_size_) ::
 (_cap_, Gvar v_cap_) :: (_head_, Gvar v_head_) :: (_tail_, Gvar v_tail_) ::
 (_lookup_key, Gfun(Internal f_lookup_key)) ::
 (_key_at, Gfun(Internal f_key_at)) ::
 (_value_at, Gfun(Internal f_value_at)) ::
 (_erase_at, Gfun(Internal f_erase_at)) ::
 (_touch, Gfun(Internal f_touch)) ::
 (_set_value, Gfun(Internal f_set_value)) ::
 (_insert_front, Gfun(Internal f_insert_front)) ::
 (_evict_tail, Gfun(Internal f_evict_tail)) ::
 (_cache_put, Gfun(Internal f_cache_put)) ::
 (_cache_query, Gfun(Internal f_cache_query)) ::
 (_resize_cache, Gfun(Internal f_resize_cache)) ::
 (_execute_cache, Gfun(Internal f_execute_cache)) ::
 (_observe_cache, Gfun(Internal f_observe_cache)) ::
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


