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
  Definition source_file := "FOREST_V0.c".
  Definition normalized := true.
End Info.

Definition _Edge : ident := $"Edge".
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
Definition _b : ident := $"b".
Definition _begin_output : ident := $"begin_output".
Definition _better : ident := $"better".
Definition _choose_edge : ident := $"choose_edge".
Definition _components : ident := $"components".
Definition _eb_input : ident := $"eb_input".
Definition _eb_out : ident := $"eb_out".
Definition _eb_output : ident := $"eb_output".
Definition _edge_count : ident := $"edge_count".
Definition _edges : ident := $"edges".
Definition _emit : ident := $"emit".
Definition _end_output : ident := $"end_output".
Definition _i : ident := $"i".
Definition _id : ident := $"id".
Definition _j : ident := $"j".
Definition _main : ident := $"main".
Definition _mask : ident := $"mask".
Definition _mode : ident := $"mode".
Definition _order : ident := $"order".
Definition _p : ident := $"p".
Definition _parent : ident := $"parent".
Definition _root : ident := $"root".
Definition _selected : ident := $"selected".
Definition _spanning_forest : ident := $"spanning_forest".
Definition _total : ident := $"total".
Definition _u : ident := $"u".
Definition _v : ident := $"v".
Definition _vertices : ident := $"vertices".
Definition _visited : ident := $"visited".
Definition _weight : ident := $"weight".
Definition _x : ident := $"x".
Definition _t'1 : ident := 128%positive.
Definition _t'10 : ident := 137%positive.
Definition _t'11 : ident := 138%positive.
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

Definition v_edges := {|
  gvar_info := (tarray (Tstruct _Edge noattr) 28);
  gvar_init := (Init_space 448 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_parent := {|
  gvar_info := (tarray tint 8);
  gvar_init := (Init_space 32 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_visited := {|
  gvar_info := (tarray tint 8);
  gvar_init := (Init_space 32 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_selected := {|
  gvar_info := (tarray tint 28);
  gvar_init := (Init_space 112 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_vertices := {|
  gvar_info := tint;
  gvar_init := (Init_space 4 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition v_edge_count := {|
  gvar_info := tint;
  gvar_init := (Init_space 4 :: nil);
  gvar_readonly := false;
  gvar_volatile := false
|}.

Definition f_root := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := ((_x, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Sloop
    (Ssequence
      (Ssequence
        (Sset _t'1
          (Ederef
            (Ebinop Oadd (Evar _parent (tarray tint 8)) (Etempvar _x tint)
              (tptr tint)) tint))
        (Sifthenelse (Ebinop One (Etempvar _t'1 tint) (Etempvar _x tint)
                       tint)
          Sskip
          Sbreak))
      (Sset _x
        (Ederef
          (Ebinop Oadd (Evar _parent (tarray tint 8)) (Etempvar _x tint)
            (tptr tint)) tint)))
    Sskip)
  (Sreturn (Some (Etempvar _x tint))))
|}.

Definition f_choose_edge := {|
  fn_return := tvoid;
  fn_callconv := cc_default;
  fn_params := ((_id, tint) :: (_total, (tptr tint)) :: nil);
  fn_vars := nil;
  fn_temps := ((_t'2, tint) :: (_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Sassign
    (Ederef
      (Ebinop Oadd (Evar _selected (tarray tint 28)) (Etempvar _id tint)
        (tptr tint)) tint) (Econst_int (Int.repr 1) tint))
  (Ssequence
    (Sset _t'1 (Ederef (Etempvar _total (tptr tint)) tint))
    (Ssequence
      (Sset _t'2
        (Efield
          (Ederef
            (Ebinop Oadd (Evar _edges (tarray (Tstruct _Edge noattr) 28))
              (Etempvar _id tint) (tptr (Tstruct _Edge noattr)))
            (Tstruct _Edge noattr)) _weight tint))
      (Sassign (Ederef (Etempvar _total (tptr tint)) tint)
        (Ebinop Oadd (Etempvar _t'1 tint) (Etempvar _t'2 tint) tint)))))
|}.

Definition f_better := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := ((_a, tint) :: (_b, tint) :: nil);
  fn_vars := nil;
  fn_temps := ((_t'2, tint) :: (_t'1, tint) :: nil);
  fn_body :=
(Ssequence
  (Sifthenelse (Ebinop Olt (Etempvar _b tint) (Econst_int (Int.repr 0) tint)
                 tint)
    (Sreturn (Some (Econst_int (Int.repr 1) tint)))
    Sskip)
  (Ssequence
    (Sset _t'1
      (Efield
        (Ederef
          (Ebinop Oadd (Evar _edges (tarray (Tstruct _Edge noattr) 28))
            (Etempvar _a tint) (tptr (Tstruct _Edge noattr)))
          (Tstruct _Edge noattr)) _weight tint))
    (Ssequence
      (Sset _t'2
        (Efield
          (Ederef
            (Ebinop Oadd (Evar _edges (tarray (Tstruct _Edge noattr) 28))
              (Etempvar _b tint) (tptr (Tstruct _Edge noattr)))
            (Tstruct _Edge noattr)) _weight tint))
      (Sreturn (Some (Ebinop Olt (Etempvar _t'1 tint) (Etempvar _t'2 tint)
                       tint))))))
|}.

Definition f_spanning_forest := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := ((_total, (tptr tint)) :: nil);
  fn_vars := ((_order, (tarray tint 28)) :: nil);
  fn_temps := ((_i, tint) :: (_j, tint) :: (_x, tint) :: (_a, tint) ::
               (_b, tint) :: (_components, tint) :: (_t'4, tint) ::
               (_t'3, tint) :: (_t'2, tint) :: (_t'1, tint) ::
               (_t'11, tint) :: (_t'10, tint) :: (_t'9, tint) ::
               (_t'8, tint) :: (_t'7, tint) :: (_t'6, tint) ::
               (_t'5, tint) :: nil);
  fn_body :=
(Ssequence
  (Sset _components (Evar _vertices tint))
  (Ssequence
    (Ssequence
      (Sset _i (Econst_int (Int.repr 0) tint))
      (Sloop
        (Ssequence
          (Ssequence
            (Sset _t'11 (Evar _edge_count tint))
            (Sifthenelse (Ebinop Olt (Etempvar _i tint) (Etempvar _t'11 tint)
                           tint)
              Sskip
              Sbreak))
          (Sassign
            (Ederef
              (Ebinop Oadd (Evar _order (tarray tint 28)) (Etempvar _i tint)
                (tptr tint)) tint) (Etempvar _i tint)))
        (Sset _i
          (Ebinop Oadd (Etempvar _i tint) (Econst_int (Int.repr 1) tint)
            tint))))
    (Ssequence
      (Ssequence
        (Sset _i (Econst_int (Int.repr 1) tint))
        (Sloop
          (Ssequence
            (Ssequence
              (Sset _t'10 (Evar _edge_count tint))
              (Sifthenelse (Ebinop Olt (Etempvar _i tint)
                             (Etempvar _t'10 tint) tint)
                Sskip
                Sbreak))
            (Ssequence
              (Sset _x
                (Ederef
                  (Ebinop Oadd (Evar _order (tarray tint 28))
                    (Etempvar _i tint) (tptr tint)) tint))
              (Ssequence
                (Sset _j (Etempvar _i tint))
                (Ssequence
                  (Sloop
                    (Ssequence
                      (Ssequence
                        (Sifthenelse (Ebinop Ogt (Etempvar _j tint)
                                       (Econst_int (Int.repr 0) tint) tint)
                          (Ssequence
                            (Ssequence
                              (Sset _t'9
                                (Ederef
                                  (Ebinop Oadd (Evar _order (tarray tint 28))
                                    (Ebinop Osub (Etempvar _j tint)
                                      (Econst_int (Int.repr 1) tint) tint)
                                    (tptr tint)) tint))
                              (Scall (Some _t'2)
                                (Evar _better (Tfunction
                                                (tint :: tint :: nil) tint
                                                cc_default))
                                ((Etempvar _x tint) ::
                                 (Etempvar _t'9 tint) :: nil)))
                            (Sset _t'1 (Ecast (Etempvar _t'2 tint) tbool)))
                          (Sset _t'1 (Econst_int (Int.repr 0) tint)))
                        (Sifthenelse (Etempvar _t'1 tint) Sskip Sbreak))
                      (Ssequence
                        (Ssequence
                          (Sset _t'8
                            (Ederef
                              (Ebinop Oadd (Evar _order (tarray tint 28))
                                (Ebinop Osub (Etempvar _j tint)
                                  (Econst_int (Int.repr 1) tint) tint)
                                (tptr tint)) tint))
                          (Sassign
                            (Ederef
                              (Ebinop Oadd (Evar _order (tarray tint 28))
                                (Etempvar _j tint) (tptr tint)) tint)
                            (Etempvar _t'8 tint)))
                        (Sset _j
                          (Ebinop Osub (Etempvar _j tint)
                            (Econst_int (Int.repr 1) tint) tint))))
                    Sskip)
                  (Sassign
                    (Ederef
                      (Ebinop Oadd (Evar _order (tarray tint 28))
                        (Etempvar _j tint) (tptr tint)) tint)
                    (Etempvar _x tint))))))
          (Sset _i
            (Ebinop Oadd (Etempvar _i tint) (Econst_int (Int.repr 1) tint)
              tint))))
      (Ssequence
        (Ssequence
          (Sset _i (Econst_int (Int.repr 0) tint))
          (Sloop
            (Ssequence
              (Ssequence
                (Sset _t'7 (Evar _edge_count tint))
                (Sifthenelse (Ebinop Olt (Etempvar _i tint)
                               (Etempvar _t'7 tint) tint)
                  Sskip
                  Sbreak))
              (Ssequence
                (Sset _x
                  (Ederef
                    (Ebinop Oadd (Evar _order (tarray tint 28))
                      (Etempvar _i tint) (tptr tint)) tint))
                (Ssequence
                  (Ssequence
                    (Ssequence
                      (Sset _t'6
                        (Efield
                          (Ederef
                            (Ebinop Oadd
                              (Evar _edges (tarray (Tstruct _Edge noattr) 28))
                              (Etempvar _x tint)
                              (tptr (Tstruct _Edge noattr)))
                            (Tstruct _Edge noattr)) _u tint))
                      (Scall (Some _t'3)
                        (Evar _root (Tfunction (tint :: nil) tint cc_default))
                        ((Etempvar _t'6 tint) :: nil)))
                    (Sset _a (Etempvar _t'3 tint)))
                  (Ssequence
                    (Ssequence
                      (Ssequence
                        (Sset _t'5
                          (Efield
                            (Ederef
                              (Ebinop Oadd
                                (Evar _edges (tarray (Tstruct _Edge noattr) 28))
                                (Etempvar _x tint)
                                (tptr (Tstruct _Edge noattr)))
                              (Tstruct _Edge noattr)) _v tint))
                        (Scall (Some _t'4)
                          (Evar _root (Tfunction (tint :: nil) tint
                                        cc_default))
                          ((Etempvar _t'5 tint) :: nil)))
                      (Sset _b (Etempvar _t'4 tint)))
                    (Sifthenelse (Ebinop One (Etempvar _a tint)
                                   (Etempvar _b tint) tint)
                      (Ssequence
                        (Sassign
                          (Ederef
                            (Ebinop Oadd (Evar _parent (tarray tint 8))
                              (Etempvar _a tint) (tptr tint)) tint)
                          (Etempvar _b tint))
                        (Ssequence
                          (Sset _components
                            (Ebinop Osub (Etempvar _components tint)
                              (Econst_int (Int.repr 1) tint) tint))
                          (Scall None
                            (Evar _choose_edge (Tfunction
                                                 (tint :: (tptr tint) :: nil)
                                                 tvoid cc_default))
                            ((Etempvar _x tint) ::
                             (Etempvar _total (tptr tint)) :: nil))))
                      Sskip)))))
            (Sset _i
              (Ebinop Oadd (Etempvar _i tint) (Econst_int (Int.repr 1) tint)
                tint))))
        (Sreturn (Some (Etempvar _components tint)))))))
|}.

Definition f_main := {|
  fn_return := tint;
  fn_callconv := cc_default;
  fn_params := nil;
  fn_vars := ((_total, tint) :: nil);
  fn_temps := ((_i, tint) :: (_p, tint) :: (_components, tint) ::
               (_mask, tint) :: (_mode, tint) :: (_t'2, tint) ::
               (_t'1, tint) :: (_t'11, tint) :: (_t'10, tint) ::
               (_t'9, tint) :: (_t'8, tint) :: (_t'7, tint) ::
               (_t'6, tint) :: (_t'5, tint) :: (_t'4, tint) ::
               (_t'3, tint) :: nil);
  fn_body :=
(Ssequence
  (Ssequence
    (Sassign (Evar _total tint) (Econst_int (Int.repr 0) tint))
    (Ssequence
      (Sset _mask (Econst_int (Int.repr 0) tint))
      (Ssequence
        (Sset _mode
          (Ederef
            (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
              (Econst_int (Int.repr 0) tint) (tptr tint)) tint))
        (Ssequence
          (Scall None (Evar _begin_output (Tfunction nil tvoid cc_default))
            nil)
          (Ssequence
            (Ssequence
              (Sset _t'11
                (Ederef
                  (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
                    (Econst_int (Int.repr 1) tint) (tptr tint)) tint))
              (Sassign (Evar _vertices tint) (Etempvar _t'11 tint)))
            (Ssequence
              (Ssequence
                (Sset _t'10
                  (Ederef
                    (Ebinop Oadd (Evar _eb_input (tarray tint 8192))
                      (Econst_int (Int.repr 2) tint) (tptr tint)) tint))
                (Sassign (Evar _edge_count tint) (Etempvar _t'10 tint)))
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
                          (Ederef
                            (Ebinop Oadd (Evar _parent (tarray tint 8))
                              (Etempvar _i tint) (tptr tint)) tint)
                          (Etempvar _i tint))
                        (Sassign
                          (Ederef
                            (Ebinop Oadd (Evar _visited (tarray tint 8))
                              (Etempvar _i tint) (tptr tint)) tint)
                          (Econst_int (Int.repr 0) tint))))
                    (Sset _i
                      (Ebinop Oadd (Etempvar _i tint)
                        (Econst_int (Int.repr 1) tint) tint))))
                (Ssequence
                  (Ssequence
                    (Sset _i (Econst_int (Int.repr 0) tint))
                    (Sloop
                      (Ssequence
                        (Sifthenelse (Ebinop Olt (Etempvar _i tint)
                                       (Econst_int (Int.repr 28) tint) tint)
                          Sskip
                          Sbreak)
                        (Sassign
                          (Ederef
                            (Ebinop Oadd (Evar _selected (tarray tint 28))
                              (Etempvar _i tint) (tptr tint)) tint)
                          (Econst_int (Int.repr 0) tint)))
                      (Sset _i
                        (Ebinop Oadd (Etempvar _i tint)
                          (Econst_int (Int.repr 1) tint) tint))))
                  (Ssequence
                    (Ssequence
                      (Sset _i (Econst_int (Int.repr 0) tint))
                      (Sloop
                        (Ssequence
                          (Ssequence
                            (Sset _t'9 (Evar _edge_count tint))
                            (Sifthenelse (Ebinop Olt (Etempvar _i tint)
                                           (Etempvar _t'9 tint) tint)
                              Sskip
                              Sbreak))
                          (Ssequence
                            (Sset _p
                              (Ebinop Oadd (Econst_int (Int.repr 3) tint)
                                (Ebinop Omul (Econst_int (Int.repr 3) tint)
                                  (Etempvar _i tint) tint) tint))
                            (Ssequence
                              (Ssequence
                                (Sset _t'8
                                  (Ederef
                                    (Ebinop Oadd
                                      (Evar _eb_input (tarray tint 8192))
                                      (Etempvar _p tint) (tptr tint)) tint))
                                (Sassign
                                  (Efield
                                    (Ederef
                                      (Ebinop Oadd
                                        (Evar _edges (tarray (Tstruct _Edge noattr) 28))
                                        (Etempvar _i tint)
                                        (tptr (Tstruct _Edge noattr)))
                                      (Tstruct _Edge noattr)) _u tint)
                                  (Etempvar _t'8 tint)))
                              (Ssequence
                                (Ssequence
                                  (Sset _t'7
                                    (Ederef
                                      (Ebinop Oadd
                                        (Evar _eb_input (tarray tint 8192))
                                        (Ebinop Oadd (Etempvar _p tint)
                                          (Econst_int (Int.repr 1) tint)
                                          tint) (tptr tint)) tint))
                                  (Sassign
                                    (Efield
                                      (Ederef
                                        (Ebinop Oadd
                                          (Evar _edges (tarray (Tstruct _Edge noattr) 28))
                                          (Etempvar _i tint)
                                          (tptr (Tstruct _Edge noattr)))
                                        (Tstruct _Edge noattr)) _v tint)
                                    (Etempvar _t'7 tint)))
                                (Ssequence
                                  (Ssequence
                                    (Sset _t'6
                                      (Ederef
                                        (Ebinop Oadd
                                          (Evar _eb_input (tarray tint 8192))
                                          (Ebinop Oadd (Etempvar _p tint)
                                            (Econst_int (Int.repr 2) tint)
                                            tint) (tptr tint)) tint))
                                    (Sassign
                                      (Efield
                                        (Ederef
                                          (Ebinop Oadd
                                            (Evar _edges (tarray (Tstruct _Edge noattr) 28))
                                            (Etempvar _i tint)
                                            (tptr (Tstruct _Edge noattr)))
                                          (Tstruct _Edge noattr)) _weight
                                        tint) (Etempvar _t'6 tint)))
                                  (Sassign
                                    (Efield
                                      (Ederef
                                        (Ebinop Oadd
                                          (Evar _edges (tarray (Tstruct _Edge noattr) 28))
                                          (Etempvar _i tint)
                                          (tptr (Tstruct _Edge noattr)))
                                        (Tstruct _Edge noattr)) _id tint)
                                    (Etempvar _i tint)))))))
                        (Sset _i
                          (Ebinop Oadd (Etempvar _i tint)
                            (Econst_int (Int.repr 1) tint) tint))))
                    (Ssequence
                      (Ssequence
                        (Scall (Some _t'1)
                          (Evar _spanning_forest (Tfunction
                                                   ((tptr tint) :: nil) tint
                                                   cc_default))
                          ((Eaddrof (Evar _total tint) (tptr tint)) :: nil))
                        (Sset _components (Etempvar _t'1 tint)))
                      (Ssequence
                        (Ssequence
                          (Sset _t'5 (Evar _total tint))
                          (Scall None
                            (Evar _emit (Tfunction (tint :: nil) tvoid
                                          cc_default))
                            ((Etempvar _t'5 tint) :: nil)))
                        (Ssequence
                          (Scall None
                            (Evar _emit (Tfunction (tint :: nil) tvoid
                                          cc_default))
                            ((Etempvar _components tint) :: nil))
                          (Ssequence
                            (Sifthenelse (Ebinop Oeq (Etempvar _mode tint)
                                           (Econst_int (Int.repr 1) tint)
                                           tint)
                              (Ssequence
                                (Ssequence
                                  (Sset _i (Econst_int (Int.repr 0) tint))
                                  (Sloop
                                    (Ssequence
                                      (Ssequence
                                        (Sset _t'4 (Evar _edge_count tint))
                                        (Sifthenelse (Ebinop Olt
                                                       (Etempvar _i tint)
                                                       (Etempvar _t'4 tint)
                                                       tint)
                                          Sskip
                                          Sbreak))
                                      (Ssequence
                                        (Sset _t'3
                                          (Ederef
                                            (Ebinop Oadd
                                              (Evar _selected (tarray tint 28))
                                              (Etempvar _i tint) (tptr tint))
                                            tint))
                                        (Sifthenelse (Etempvar _t'3 tint)
                                          (Sset _mask
                                            (Ebinop Oadd
                                              (Etempvar _mask tint)
                                              (Ebinop Oshl
                                                (Econst_int (Int.repr 1) tint)
                                                (Etempvar _i tint) tint)
                                              tint))
                                          Sskip)))
                                    (Sset _i
                                      (Ebinop Oadd (Etempvar _i tint)
                                        (Econst_int (Int.repr 1) tint) tint))))
                                (Scall None
                                  (Evar _emit (Tfunction (tint :: nil) tvoid
                                                cc_default))
                                  ((Etempvar _mask tint) :: nil)))
                              Sskip)
                            (Ssequence
                              (Scall (Some _t'2)
                                (Evar _end_output (Tfunction nil tint
                                                    cc_default)) nil)
                              (Sreturn (Some (Etempvar _t'2 tint)))))))))))))))))
  (Sreturn (Some (Econst_int (Int.repr 0) tint))))
|}.

Definition composites : list composite_definition :=
(Composite _Edge Struct
   (Member_plain _u tint :: Member_plain _v tint ::
    Member_plain _weight tint :: Member_plain _id tint :: nil)
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
 (_end_output, Gfun(Internal f_end_output)) :: (_edges, Gvar v_edges) ::
 (_parent, Gvar v_parent) :: (_visited, Gvar v_visited) ::
 (_selected, Gvar v_selected) :: (_vertices, Gvar v_vertices) ::
 (_edge_count, Gvar v_edge_count) :: (_root, Gfun(Internal f_root)) ::
 (_choose_edge, Gfun(Internal f_choose_edge)) ::
 (_better, Gfun(Internal f_better)) ::
 (_spanning_forest, Gfun(Internal f_spanning_forest)) ::
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


