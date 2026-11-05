From Trusted Require Import Obligation.
From Trusted Require Import Execution BasicDomain.
From Stdlib Require Import List ZArith Lia.
From compcert Require Import Coqlib Maps Integers AST Values Memory Events Globalenvs Smallstep Ctypes Cop Clight.
Import ListNotations.
Open Scope Z_scope.
Transparent Mem.alloc Mem.free Mem.store Mem.load Mem.storebytes Mem.loadbytes.
Transparent Int.repr Int.unsigned Int.signed Ptrofs.repr Ptrofs.unsigned.
Transparent Int64.repr Byte.repr peq plt option_eq intsize_eq signedness_eq floatsize_eq attr_eq type_eq typelist_eq Memdata.quantity_eq.
Transparent calling_convention_eq typ_eq xtype_eq signature_eq chunk_eq external_function_eq Val.eq.

Fixpoint range_dec_nat (n:nat) m b lo k p :
 {Mem.range_perm m b lo (lo + Z.of_nat n) k p} + {~Mem.range_perm m b lo (lo + Z.of_nat n) k p}.
Proof.
 destruct n as [|n].
 - left. intros ofs H; lia.
 - destruct (Mem.perm_dec m b lo k p) as [P|P].
   + destruct (range_dec_nat n m b (lo+1) k p) as [R|R].
     * left. intros ofs H. destruct (Z.eq_dec ofs lo); [subst; exact P|]. apply R; lia.
     * right. intro H. apply R. intros ofs B. apply H; lia.
   + right. intro H. apply P. apply H; lia.
Defined.
Definition fast_range_dec m b lo hi k p : {Mem.range_perm m b lo hi k p}+{~Mem.range_perm m b lo hi k p}.
Proof.
 destruct (zle hi lo) as [H|H].
 - left. intros ofs B; lia.
 - destruct (range_dec_nat (Z.to_nat (hi-lo)) m b lo k p) as [R|R].
   + left. intros ofs B. apply R. rewrite Z2Nat.id by lia. lia.
   + right. intro Q. apply R. intros ofs B. apply Q. rewrite Z2Nat.id in B by lia. lia.
Defined.
Definition fast_valid_dec m ch b ofs p : {Mem.valid_access m ch b ofs p}+{~Mem.valid_access m ch b ofs p}.
Proof.
 destruct (fast_range_dec m b ofs (ofs + Memdata.size_chunk ch) Cur p) as [R|R].
 - destruct (Zdivide_dec (Memdata.align_chunk ch) ofs) as [D|D].
   + left; split; auto.
   + right; intros [_ H]; auto.
 - right; intros [H _]; auto.
Defined.
Definition fast_load ch m b ofs :=
 if fast_valid_dec m ch b ofs Readable then
 Some (Memdata.decode_val ch (Mem.getN (Memdata.size_chunk_nat ch) ofs (PMap.get b (Mem.mem_contents m)))) else None.
Lemma fast_load_eq ch m b ofs : fast_load ch m b ofs = Mem.load ch m b ofs.
Proof.
 unfold fast_load, Mem.load. destruct fast_valid_dec; destruct Mem.valid_access_dec; try contradiction; reflexivity.
Qed.
Definition fast_loadv ch m addr :=
 match addr with Vptr b ofs => if zle (Ptrofs.unsigned ofs + Memdata.size_chunk ch) Ptrofs.modulus
 then fast_load ch m b (Ptrofs.unsigned ofs) else None | _ => None end.
Lemma fast_loadv_eq ch m addr : fast_loadv ch m addr = Mem.loadv ch m addr.
Proof.
 destruct addr; try reflexivity. unfold fast_loadv, Mem.loadv. destruct zle; auto. apply fast_load_eq.
Qed.
Definition fast_drop_perm m b lo hi p : option mem :=
 match fast_range_dec m b lo hi Cur Freeable with
 | left r => Some (Mem.mkmem (Mem.mem_contents m)
     (PMap.set b (fun ofs k => if zle lo ofs && zlt ofs hi then Some p else PMap.get b (Mem.mem_access m) ofs k) (Mem.mem_access m))
     (Mem.nextblock m)
     (Memory.Mem.drop_perm_obligation_1 m b lo hi p)
     (Memory.Mem.drop_perm_obligation_2 m b lo hi p r)
     (Memory.Mem.drop_perm_obligation_3 m))
 | right _ => None end.
Lemma fast_drop_perm_eq m b lo hi p : fast_drop_perm m b lo hi p = Mem.drop_perm m b lo hi p.
Proof.
 unfold fast_drop_perm, Mem.drop_perm.
 destruct fast_range_dec; destruct Mem.range_perm_dec; try contradiction; auto.
 f_equal. apply Mem.mkmem_ext; reflexivity.
Qed.
Ltac inv H := inversion H; subst; clear H.
Definition ncont (d:PTree.t Memdata.memval) (t:PTree.t (ZMap.t Memdata.memval)) :=
 ((Memdata.Undef,d), PTree.map (fun _ v => (Memdata.Undef,snd v)) t).
Lemma ncont_default d t : forall b, fst (PMap.get b (ncont d t)) = Memdata.Undef.
Proof.
 intro b. cbv delta [ZMap.t PMap.t] in *. unfold ncont, PMap.get; simpl. rewrite PTree.gmap.
 destruct (PTree.get b t); reflexivity.
Qed.
Definition compact (m:mem) : mem :=
 match m with Mem.mkmem c a n am nn cd =>
 match c with ((Memdata.Undef,d),t) =>
   Mem.mkmem (ncont d t) a n am nn (ncont_default d t)
 | _ => m end end.
Lemma compact_eq m : compact m = m.
Proof.
 destruct m as [[[v d] t] a n am nn cd]. destruct v; try reflexivity.
 simpl compact. cbv delta [ZMap.t PMap.t] in *. apply Mem.mkmem_ext; auto. unfold ncont. f_equal.
 apply PTree.extensionality; intro b. rewrite PTree.gmap.
 destruct (PTree.get b t) as [[v tr]|] eqn:E; simpl; auto.
 specialize (cd b). unfold PMap.get in cd; simpl in cd. rewrite E in cd. simpl in cd. subst v; reflexivity.
Qed.
Lemma store_default c (D:forall b, fst (PMap.get b c) = Memdata.Undef) b p vl :
 forall b', fst (PMap.get b' (PMap.set b (Mem.setN vl p (PMap.get b c)) c)) = Memdata.Undef.
Proof.
 intro b'. rewrite PMap.gsspec. destruct (peq b' b).
 - rewrite Mem.setN_default. apply D.
 - apply D.
Qed.
Definition raw_store ch (m:mem) b ofs v : option mem :=
 match m with Mem.mkmem c a n am nn cd =>
 if fast_valid_dec m ch b ofs Writable then
 Some (Mem.mkmem (PMap.set b (Mem.setN (Memdata.encode_val ch v) ofs (PMap.get b c)) c)
   a n am nn (store_default c cd b ofs (Memdata.encode_val ch v)))
 else None end.
Lemma raw_store_eq ch m b ofs v : raw_store ch m b ofs v = Mem.store ch m b ofs v.
Proof.
 destruct m. unfold raw_store, Mem.store. destruct fast_valid_dec; destruct Mem.valid_access_dec; try contradiction; auto.
 f_equal. apply Mem.mkmem_ext; reflexivity.
Qed.
Definition fast_store ch m b ofs v :=
 match raw_store ch m b ofs v with
 | Some m' => Some (if Z.eqb (ofs mod 1024) 0 then compact m' else m')
 | None => None end.
Lemma fast_store_eq ch m b ofs v : fast_store ch m b ofs v = Mem.store ch m b ofs v.
Proof.
 unfold fast_store. rewrite raw_store_eq. destruct (Mem.store ch m b ofs v); auto.
 destruct Z.eqb; [rewrite compact_eq|]; reflexivity.
Qed.
Definition fast_storev ch m addr v :=
 match addr with Vptr b ofs =>
 if zle (Ptrofs.unsigned ofs + Memdata.size_chunk ch) Ptrofs.modulus then
 fast_store ch m b (Ptrofs.unsigned ofs) v else None
 | _ => None end.
Lemma fast_storev_eq ch m addr v : fast_storev ch m addr v = Mem.storev ch m addr v.
Proof.
 destruct addr; try reflexivity. unfold fast_storev, Mem.storev.
 destruct zle; auto. apply fast_store_eq.
Qed.
Fixpoint store_words_fast m b ofs xs : option mem :=
 match xs with [] => Some m | x::xs =>
 match fast_store Mint32 m b ofs (Vint (Int.repr x)) with
 Some m' => store_words_fast m' b (ofs+4) xs | _ => None end end.
Lemma store_words_fast_eq m b ofs xs : store_words_fast m b ofs xs = store_words m b ofs xs.
Proof.
 revert m ofs. induction xs; intros; simpl; auto. rewrite fast_store_eq.
 destruct (Mem.store Mint32 m b ofs (Vint (Int.repr a))); auto.
Qed.
Definition readval (ty:type) (m:mem) (b:block) (o:ptrofs) : option val :=
 match access_mode ty with
 | By_value ch => fast_loadv ch m (Vptr b o)
 | By_reference | By_copy => Some (Vptr b o)
 | _ => None
 end.
Definition locvar (ge:genv) (e:env) (id:ident) (ty:type) : option (block * ptrofs) :=
 match PTree.get id e with
 | Some (b,t) => if type_eq t ty then Some (b,Ptrofs.zero) else None
 | None => match Genv.find_symbol ge id with Some b => Some (b,Ptrofs.zero) | None => None end
 end.
Fixpoint ev (ge:genv) (e:env) (le:temp_env) (m:mem) (a:expr) : option val :=
 match a with
 | Econst_int i _ => Some (Vint i)
 | Etempvar id _ => PTree.get id le
 | Evar id ty => match locvar ge e id ty with Some (b,o) => readval ty m b o | None => None end
 | Ederef a ty => match ev ge e le m a with Some (Vptr b o) => readval ty m b o | _ => None end
 | Ebinop op a b _ => match ev ge e le m a, ev ge e le m b with
     Some v, Some w => sem_binary_operation ge op v (typeof a) w (typeof b) m | _,_ => None end
 | _ => None
 end.
Definition lv ge e le m a :=
 match a with
 | Evar id ty => locvar ge e id ty
 | Ederef a _ => match ev ge e le m a with Some (Vptr b o) => Some (b,o) | _ => None end
 | _ => None
 end.
Ltac splitmatch := repeat match goal with
 | H: context [match ?x with _ => _ end] |- _ => destruct x eqn:?; try discriminate
 | H: context [if ?x then _ else _] |- _ => destruct x eqn:?; try discriminate
 end.
Lemma readval_ok ty m b o v : readval ty m b o = Some v ->
 deref_loc ty m b o Full v /\ forall w, deref_loc ty m b o Full w -> w=v.
Proof.
 unfold readval. destruct (access_mode ty) eqn:A; intro H; try rewrite fast_loadv_eq in H; try discriminate;
 split; try (inv H; econstructor; eauto);
 intros w D; inv D; try congruence; congruence.
Qed.
Lemma locvar_ok ge e id ty b o : locvar ge e id ty = Some (b,o) ->
 (forall le m, eval_lvalue ge e le m (Evar id ty) b o Full) /\
 (forall le m b' o' bf, eval_lvalue ge e le m (Evar id ty) b' o' bf -> b'=b /\ o'=o /\ bf=Full).
Proof.
 unfold locvar. destruct (e!id) as [[b0 t]|] eqn:A.
 - destruct (type_eq t ty); try discriminate. subst t. intro H; inv H. split.
   + intros; eapply eval_Evar_local; eauto.
   + intros; match goal with H:eval_lvalue _ _ _ _ _ _ _ _ |- _ => inv H end; try congruence. repeat split; congruence.
 - destruct (Genv.find_symbol ge id) eqn:B; try discriminate. intro H; inv H. split.
   + intros; eapply eval_Evar_global; eauto.
   + intros; match goal with H:eval_lvalue _ _ _ _ _ _ _ _ |- _ => inv H end; try congruence. repeat split; congruence.
Qed.
Lemma ev_ok ge e le m a :
 (forall v, ev ge e le m a = Some v -> eval_expr ge e le m a v /\
   forall w, eval_expr ge e le m a w -> w=v) /\
 (forall b o, lv ge e le m a = Some (b,o) -> eval_lvalue ge e le m a b o Full /\
   forall b' o' bf, eval_lvalue ge e le m a b' o' bf -> b'=b /\ o'=o /\ bf=Full).
Proof.
 induction a; split; simpl; intros; try discriminate.
 - inv H. split; [constructor|]. intros w D; inv D; try reflexivity.
   match goal with H:eval_lvalue _ _ _ _ _ _ _ _ |- _ => inv H end.
 - destruct (locvar ge e i t) as [[b o]|] eqn:L; try discriminate.
   destruct (locvar_ok _ _ _ _ _ _ L) as [LS LU].
   destruct (readval_ok _ _ _ _ _ H) as [RS RU]. split.
   + eapply eval_Elvalue; [apply LS|exact RS].
   + intros w D; inv D.
     match goal with D:eval_lvalue _ _ _ _ _ _ _ _ |- _ => destruct (LU _ _ _ _ _ D) as [? [? ?]]; subst end.
     eauto.
 - apply locvar_ok in H. destruct H as [A B]. split; eauto.
 - split; [constructor; auto|]. intros w D; inv D; try congruence.
   match goal with H:eval_lvalue _ _ _ _ _ _ _ _ |- _ => inv H end.
 - destruct (ev ge e le m a) eqn:E; try discriminate. destruct v0; try discriminate.
   destruct (IHa) as [IH _]. destruct (IH _ eq_refl) as [ES EU].
   destruct (readval_ok _ _ _ _ _ H) as [RS RU]. split.
   + eapply eval_Elvalue; [econstructor; exact ES|exact RS].
   + intros w D; inv D.
     match goal with D:eval_lvalue _ _ _ _ _ _ _ _ |- _ => inv D end.
     match goal with D:eval_expr _ _ _ _ a _ |- _ => specialize (EU _ D); inv EU end.
     eauto.
 - destruct (ev ge e le m a) eqn:E; try discriminate. destruct v; try discriminate.
   inv H. destruct IHa as [IH _]. destruct (IH _ eq_refl) as [ES EU]. split.
   + econstructor; exact ES.
   + intros b' o' bf D; inv D.
     match goal with D:eval_expr _ _ _ _ a _ |- _ => specialize (EU _ D); inv EU end.
     auto.
 - destruct (ev ge e le m a1) eqn:E1; try discriminate.
   destruct (ev ge e le m a2) eqn:E2; try discriminate.
   destruct IHa1 as [IH1 _]. destruct IHa2 as [IH2 _].
   destruct (IH1 _ eq_refl) as [S1 U1]. destruct (IH2 _ eq_refl) as [S2 U2]. split.
   + econstructor; eauto.
   + intros w D; inv D.
     * match goal with D:eval_expr _ _ _ _ a1 _ |- _ => specialize (U1 _ D); subst end.
       match goal with D:eval_expr _ _ _ _ a2 _ |- _ => specialize (U2 _ D); subst end. congruence.
     * match goal with D:eval_lvalue _ _ _ _ _ _ _ _ |- _ => inv D end.
Qed.
Fixpoint evs ge e le m (aa:list expr) (tys:list type) : option (list val) :=
 match aa,tys with
 | [],[] => Some []
 | a::aa,t::tys => match ev ge e le m a with Some v =>
    match sem_cast v (typeof a) t m, evs ge e le m aa tys with
    | Some w,Some ww => Some (w::ww) | _,_ => None end
    | _ => None end
 | _,_ => None end.
Lemma evs_ok ge e le m aa tys vv : evs ge e le m aa tys = Some vv ->
 eval_exprlist ge e le m aa tys vv /\ forall ww, eval_exprlist ge e le m aa tys ww -> ww=vv.
Proof.
 revert tys vv. induction aa as [|a aa IH]; intros [|t tys] vv H; simpl in H; try discriminate.
 - inv H. split; [constructor|]. intros ww D; inv D; auto.
 - destruct (ev ge e le m a) eqn:E; try discriminate.
   destruct (sem_cast v (typeof a) t m) eqn:C; try discriminate.
   destruct (evs ge e le m aa tys) eqn:L; try discriminate. inv H.
   destruct (proj1 (ev_ok ge e le m a) _ E) as [S U].
   destruct (IH _ _ L) as [SS UU]. split; [econstructor; eauto|].
   intros ww D; inv D.
   match goal with D:eval_expr _ _ _ _ a _ |- _ => specialize (U _ D); subst end.
   match goal with D:eval_exprlist _ _ _ _ aa tys _ |- _ => specialize (UU _ D); subst end.
   f_equal; congruence.
Qed.
Definition enter (f:function) (args:list val) : option temp_env :=
 match fn_vars f with
 | [] => if list_norepet_dec ident_eq (var_names (fn_params f)) then
   if list_disjoint_dec ident_eq (var_names (fn_params f)) (var_names (fn_temps f)) then
   bind_parameter_temps (fn_params f) args (create_undef_temps (fn_temps f)) else None else None
 | _ => None end.
Lemma enter_ok ge f args m le : enter f args = Some le ->
 function_entry2 ge f args m empty_env le m /\
 forall e' le' m', function_entry2 ge f args m e' le' m' -> e'=empty_env /\ le'=le /\ m'=m.
Proof.
 unfold enter. destruct (fn_vars f) eqn:V; try discriminate.
 destruct (list_norepet_dec ident_eq (var_names (fn_params f))); try discriminate.
 destruct (list_disjoint_dec ident_eq (var_names (fn_params f)) (var_names (fn_temps f))); try discriminate.
 intro H. split.
 - constructor; auto; rewrite V; constructor.
 - intros e' le' m' D; inv D.
   match goal with D:alloc_variables _ _ _ _ _ _ |- _ => rewrite V in D; inv D end.
   repeat split; congruence.
Qed.
Definition put (ge:genv) (ty:type) m b o v : option mem :=
 match access_mode ty with By_value ch => fast_storev ch m (Vptr b o) v | _ => None end.
Lemma put_ok ge ty m b o v m' : put ge ty m b o v = Some m' ->
 assign_loc ge ty m b o Full v m' /\
 forall m'', assign_loc ge ty m b o Full v m'' -> m''=m'.
Proof.
 unfold put. destruct (access_mode ty) eqn:A; try discriminate. rewrite fast_storev_eq. intro H.
 split; [econstructor; eauto|]. intros m'' D; inv D; congruence.
Qed.
Definition next (ge:genv) (s:state) : option state :=
 match s with
 | State f st k e le m =>
   match st with
   | Ssequence s1 s2 => Some (State f s1 (Kseq s2 k) e le m)
   | Sloop s1 s2 => Some (State f s1 (Kloop1 s1 s2 k) e le m)
   | Sskip => match k with
     | Kseq s k => Some (State f s k e le m)
     | Kloop1 a b k => Some (State f b (Kloop2 a b k) e le m)
     | Kloop2 a b k => Some (State f (Sloop a b) k e le m)
     | Kswitch k => Some (State f Sskip k e le m)
     | _ => match Mem.free_list m (blocks_of_env ge e) with
       | Some m' => Some (Returnstate Vundef k m') | _ => None end
     end
   | Sbreak => match k with
     | Kseq _ k => Some (State f Sbreak k e le m)
     | Kloop1 _ _ k | Kloop2 _ _ k | Kswitch k => Some (State f Sskip k e le m)
     | _ => None end
   | Sset id a => match ev ge e le m a with
     Some v => Some (State f Sskip k e (PTree.set id v le) m) | _ => None end
   | Sassign a b => match lv ge e le m a,ev ge e le m b with
     | Some (loc,o),Some v => match sem_cast v (typeof b) (typeof a) m with
       | Some v' => match put ge (typeof a) m loc o v' with
          Some m' => Some (State f Sskip k e le m') | _ => None end
       | _ => None end
     | _,_ => None end
   | Sifthenelse a s1 s2 => match ev ge e le m a with Some v =>
     match bool_val v (typeof a) m with Some b => Some (State f (if b then s1 else s2) k e le m) | _ => None end
     | _ => None end
   | Scall id a aa => match classify_fun (typeof a) with
     | fun_case_f tys tr cc => match ev ge e le m a,evs ge e le m aa tys with
       | Some vf,Some vv => match Genv.find_funct ge vf with
         | Some fd => if type_eq (type_of_fundef fd) (Tfunction tys tr cc) then
           Some (Callstate fd vv (Kcall id f e le k) m) else None
         | _ => None end
       | _,_ => None end
     | _ => None end
   | Sreturn (Some a) => match ev ge e le m a with Some v =>
     match sem_cast v (typeof a) (fn_return f) m, Mem.free_list m (blocks_of_env ge e) with
     | Some v',Some m' => Some (Returnstate v' (call_cont k) m') | _,_ => None end
     | _ => None end
   | _ => None end
 | Callstate (Internal f) args k m => match enter f args with
   Some le => Some (State f (fn_body f) k empty_env le m) | _ => None end
 | Returnstate v (Kcall id f e le k) m => Some (State f Sskip k e (set_opttemp id v le) m)
 | _ => None end.
Ltac facts := repeat match goal with
 | H:ev ?ge ?e ?le ?m ?a = Some ?v |- _ =>
   let S := fresh "ES" in let U := fresh "EU" in
   destruct (proj1 (ev_ok ge e le m a) v H) as [S U]; clear H
 | H:lv ?ge ?e ?le ?m ?a = Some (?b,?o) |- _ =>
   let S := fresh "LS" in let U := fresh "LU" in
   destruct (proj2 (ev_ok ge e le m a) b o H) as [S U]; clear H
 | H:evs ?ge ?e ?le ?m ?a ?tys = Some ?v |- _ =>
   let S := fresh "AS" in let U := fresh "AU" in
   destruct (evs_ok ge e le m a tys v H) as [S U]; clear H
 | H:enter ?f ?args = Some ?le |- _ =>
   let S := fresh "FS" in let U := fresh "FU" in
   destruct (enter_ok _ f args _ le H) as [S U]; clear H
 | H:put ?ge ?ty ?m ?b ?o ?v = Some ?m' |- _ =>
   let S := fresh "PS" in let U := fresh "PU" in
   destruct (put_ok ge ty m b o v m' H) as [S U]; clear H
 end.
Lemma next_sound ge s s' : next ge s = Some s' -> step2 ge s E0 s'.
Proof.
 destruct s as [f st k e le m|fd args k m|v k m]; simpl.
 - destruct st; try discriminate;
   try (destruct k; simpl; try discriminate);
   intro H; splitmatch; inv H; facts;
   unfold step2; try solve [econstructor; eauto; simpl; auto].
   all: try solve [eapply step_ifthenelse with (b:=true); eauto | eapply step_ifthenelse with (b:=false); eauto | eapply step_return_1; eauto].
   all: match goal with |- step _ _ (State _ _ ?kk _ _ _) _ _ => eapply step_return_1 with (k:=kk); eauto end.
 - destruct fd; try discriminate. intro H; splitmatch; inv H; facts.
   econstructor; eauto.
   eapply (proj1 (enter_ok ge f args m t Heqo)).
 - destruct k; try discriminate. intro H; inv H. constructor.
Qed.
Ltac unique := repeat match goal with
 | U:forall w, eval_expr ?ge ?e ?le ?m ?a w -> w = ?v,
   D:eval_expr ?ge ?e ?le ?m ?a ?w |- _ =>
   let Q:=fresh in pose proof (U _ D) as Q; clear D; subst
 | U:forall w, eval_exprlist ?ge ?e ?le ?m ?a ?tys w -> w = ?v,
   D:eval_exprlist ?ge ?e ?le ?m ?a ?tys ?w |- _ =>
   let Q:=fresh in pose proof (U _ D) as Q; clear D; subst
 | U:forall b' o' bf, eval_lvalue ?ge ?e ?le ?m ?a b' o' bf -> _,
   D:eval_lvalue ?ge ?e ?le ?m ?a _ _ _ |- _ =>
   let Q:=fresh in destruct (U _ _ _ D) as [Q [? ?]]; clear D; subst
 | U:forall m'', assign_loc ?ge ?ty ?m ?b ?o Full ?v m'' -> m'' = ?m',
   D:assign_loc ?ge ?ty ?m ?b ?o Full ?v _ |- _ =>
   let Q:=fresh in pose proof (U _ D) as Q; clear D; subst
 end.
Ltac agree := repeat match goal with
 | H: ?x = Some ?a, H': ?x = Some ?b |- _ =>
   first [constr_eq H H'; fail 1 | idtac];
   let Q:=fresh in assert (Q:a=b) by congruence; clear H'; try subst
 end.
Lemma next_unique ge s s' : next ge s = Some s' ->
 forall t s'', step2 ge s t s'' -> t=E0 /\ s''=s'.
Proof.
 destruct s as [f st k e le m|fd args k m|v k m]; simpl.
 - destruct st; try discriminate;
   try (destruct k; simpl; try discriminate);
   intro H; splitmatch; inv H; facts;
   intros tr ss D; inv D; unique; try congruence;
   try match goal with H: _ \/ _ |- _ => destruct H; subst; try discriminate end;
   try solve [split; auto; congruence].
   all: try solve [contradiction].
   all: try solve [simpl in *; contradiction].
   all: agree; unique; agree; try solve [split; auto; congruence].
   all: match goal with H:classify_fun ?x = _, H':classify_fun ?x = _ |- _ => rewrite H in H'; inv H' end; unique; auto.
 - destruct fd; try discriminate. intro H; splitmatch; inv H.
   intros tr ss D; inv D.
   match goal with D:function_entry2 _ _ _ _ _ _ _ |- _ =>
     destruct (proj2 (enter_ok ge f args m _ Heqo) _ _ _ D) as [? [? ?]]; subst end.
   auto.
 - destruct k; try discriminate. intro H; inv H. intros tr ss D; inv D; auto.
Qed.
Lemma safe_next p s s' : next (globalenv p) s = Some s' ->
 safe_from p s' -> safe_from p s.
Proof.
 intros N S q t R. inv R.
 - right. exists E0, s'. apply next_sound; exact N.
 - match goal with H:step2 _ s _ _ |- _ =>
   destruct (next_unique _ _ _ N _ _ H) as [? ?]; subst end.
   eapply S; eauto.
Qed.
Lemma safe_final p r m : safe_from p (Returnstate (Vint r) Kstop m).
Proof.
 intros q t R. inv R.
 - left; eexists; constructor.
 - match goal with H:step2 _ _ _ _ |- _ => inv H end.
Qed.
Definition terminal (s:state) : option (int * mem) :=
 match s with Returnstate (Vint r) Kstop m => Some (r,m) | _ => None end.
Fixpoint finish (ge:genv) (fuel:nat) (s:state) : option (int * mem) :=
 match terminal s with
 | Some rm => Some rm
 | None => match fuel with
   | O => None
   | S n => match next ge s with Some s' => finish ge n s' | _ => None end
   end
 end.
Lemma terminal_ok s r m : terminal s = Some (r,m) -> s=Returnstate (Vint r) Kstop m.
Proof.
 destruct s; try discriminate. destruct res; try discriminate. destruct k; try discriminate.
 intro H; inv H; reflexivity.
Qed.
Lemma finish_ok p n s r m : finish (globalenv p) n s = Some (r,m) ->
 star step2 (globalenv p) s E0 (Returnstate (Vint r) Kstop m) /\ safe_from p s.
Proof.
 revert s r m. induction n as [|n IH]; intros s r m H;
 cbn [finish] in H; destruct (terminal s) as [[rr mm]|] eqn:T.
 - inv H. apply terminal_ok in T. subst. split; [constructor|apply safe_final].
 - discriminate.
 - inv H. apply terminal_ok in T. subst. split; [constructor|apply safe_final].
 - destruct (next (globalenv p) s) as [s'|] eqn:N; try discriminate.
   destruct (IH _ _ _ H) as [R S]. split.
   + eapply star_step; [apply next_sound; exact N|exact R|reflexivity].
   + eapply safe_next; eauto.
Qed.
Fixpoint zeros_nat (n:nat) m b p : option mem :=
 match n with
 | O => Some m
 | S n => match fast_store Mint8unsigned m b p Vzero with
   Some m' => zeros_nat n m' b (p+1) | None => None end end.
Lemma zeros_nat_eq n m b p : zeros_nat n m b p = store_zeros m b p (Z.of_nat n).
Proof.
 revert m p. induction n as [|n IH]; intros m p.
 - rewrite store_zeros_equation. simpl. reflexivity.
 - rewrite store_zeros_equation. destruct (zle (Z.of_nat (S n)) 0); [lia|].
   simpl zeros_nat. rewrite fast_store_eq. replace (Z.of_nat (S n)-1) with (Z.of_nat n) by lia.
   destruct (Mem.store Mint8unsigned m b p Vzero); auto.
Qed.
Definition zeros m b p n := zeros_nat (Z.to_nat n) m b p.
Lemma zeros_eq m b p n : zeros m b p n = store_zeros m b p n.
Proof.
 unfold zeros. rewrite zeros_nat_eq. destruct (Z_le_dec 0 n).
 - rewrite Z2Nat.id by auto. reflexivity.
 - replace (Z.to_nat n) with 0%nat by lia. simpl Z.of_nat.
   rewrite (store_zeros_equation m b p 0), (store_zeros_equation m b p n). simpl. destruct (zle n 0); [reflexivity|lia].
Qed.
Definition alloc_global_fast (ge:genv) (m:mem) (idg:ident * globdef fundef type) : option mem :=
 match idg with
 | (_,Gfun f) => let (m1,b) := Mem.alloc m 0 1 in fast_drop_perm m1 b 0 1 Nonempty
 | (_,Gvar v) =>
   let init := gvar_init v in let sz := init_data_list_size init in
   let (m1,b) := Mem.alloc m 0 sz in
   match zeros m1 b 0 sz with Some m2 =>
     match Genv.store_init_data_list ge m2 b 0 init with
     Some m3 => fast_drop_perm m3 b 0 sz (Genv.perm_globvar v) | _ => None end
   | _ => None end
 end.
Opaque Mem.alloc.
Lemma alloc_global_fast_eq ge m idg : alloc_global_fast ge m idg = Genv.alloc_global ge m idg.
Proof.
 destruct idg as [id [f|v]]; simpl.
 - destruct (Mem.alloc m 0 1). apply fast_drop_perm_eq.
 - destruct (Mem.alloc m 0 (init_data_list_size (gvar_init v))). rewrite zeros_eq.
   destruct (store_zeros m0 b 0 (init_data_list_size (gvar_init v))); auto.
   destruct (Genv.store_init_data_list ge m1 b 0 (gvar_init v)); auto. apply fast_drop_perm_eq.
Qed.
Transparent Mem.alloc.
Fixpoint alloc_globals_fast ge m gl : option mem :=
 match gl with [] => Some m | g::gl => match alloc_global_fast ge m g with
 Some m' => alloc_globals_fast ge m' gl | _ => None end end.
Lemma alloc_globals_fast_eq ge m gl : alloc_globals_fast ge m gl = Genv.alloc_globals ge m gl.
Proof.
 revert m. induction gl; intro m; simpl; auto. rewrite alloc_global_fast_eq.
 destruct (Genv.alloc_global ge m a); auto.
Qed.
Definition init_fast (p:Clight.program) := alloc_globals_fast (globalenv p) Mem.empty (prog_defs p).
Lemma init_fast_eq p : init_fast p = Genv.init_mem p.
Proof. apply alloc_globals_fast_eq. Qed.
Definition start (p:Clight.program) input xs : option state :=
 match init_fast p, Genv.find_symbol (globalenv p) (prog_main p), Genv.find_symbol (globalenv p) input with
 | Some m,Some main,Some b => match Genv.find_funct_ptr (globalenv p) main with
   | Some f => if type_eq (type_of_fundef f) (Tfunction [] type_int32s cc_default) then
     match store_words_fast m b 0 xs with Some m' => Some (Callstate f [] Kstop m') | _ => None end
     else None
   | _ => None end
 | _,_,_ => None end.
Lemma start_ok p input xs s : start p input xs = Some s -> boot p input xs s.
Proof.
 unfold start. intro H; splitmatch; inv H.
 econstructor; eauto.
 - econstructor; eauto. rewrite <- init_fast_eq; eauto.
 - rewrite <- store_words_fast_eq; eauto.
Qed.
Fixpoint load_words_fast n m b ofs : option (list Z) :=
 match n with O => Some [] | S n =>
 match fast_load Mint32 m b ofs, load_words_fast n m b (ofs+4) with
 | Some (Vint v), Some xs => Some (Int.signed v :: xs) | _,_ => None end end.
Lemma load_words_fast_eq n m b ofs : load_words_fast n m b ofs = load_words n m b ofs.
Proof.
 revert ofs. induction n; intro ofs; simpl; auto. rewrite fast_load_eq, IHn. reflexivity.
Qed.
Definition output_fast p out m :=
 match Genv.find_symbol (globalenv p) out with Some b => load_words_fast OutputWords m b 0 | _ => None end.
Lemma output_fast_eq p out m : output_fast p out m = output_words p out m.
Proof.
 unfold output_fast, output_words. destruct Genv.find_symbol; auto. apply load_words_fast_eq.
Qed.
Definition checkrun (fuel:nat) (p:implementation) xs (o:observation) : bool :=
 match start (Execution.program p) (input_symbol p) xs with
 | Some s => match finish (globalenv (Execution.program p)) fuel s with
   | Some (r,m) => match output_fast (Execution.program p) (output_symbol p) m with
     | Some ys => Z.eqb (Int.signed r) (fst o) &&
         if list_eq_dec Z.eq_dec ys (snd o) then true else false
     | _ => false end
   | _ => false end
 | _ => false end.
Lemma checkrun_ok fuel p xs o : checkrun fuel p xs o = true -> run p xs o.
Proof.
 unfold checkrun. intro H; splitmatch; try discriminate; try (rewrite Bool.andb_false_r in H; discriminate).
 apply Bool.andb_true_iff in H. destruct H as [R _]. apply Z.eqb_eq in R.
 destruct (finish_ok _ _ _ _ _ Heqo1) as [PATH SAFE].
 unfold run, executes. do 4 eexists. split; [eapply start_ok; eauto|].
 split; [exact SAFE|]. split; [exact PATH|]. split; [rewrite <- output_fast_eq; eauto|].
 destruct o; simpl in *; subst; reflexivity.
Qed.
Definition out0 : observation := (0, 1::1::repeat 0 8190).
Definition out2 : observation := (0, 1::0::repeat 0 8190).
Lemma run0 : run left_impl (BasicDomain.encode [1]) out0.
Proof. apply (checkrun_ok 100000). vm_compute. reflexivity. Qed.
Lemma run2 : run right_impl (BasicDomain.encode [1]) out2.
Proof. apply (checkrun_ok 100000). vm_compute. reflexivity. Qed.
Theorem solve : Obligation.goal.
Proof.
 exists [1], out0, out2. split; [reflexivity|]. split; [exact run0|].
 split; [exact run2|]. unfold out0,out2. intro H. inv H.
Qed.
